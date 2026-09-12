#!/usr/bin/env python3
"""End-to-end setting build: Pass 0 then the corpus pipeline, in one idempotent command (#388).

Epic #28's own Definition of Done: "a setting repo with a loaded library can be processed end to
end by running one command, twice, with the second run being a no-op." `tools/setting_pass0.py`
(#100) and `engine/wyrd/corpus_pipeline.py` (#101) each already deliver that property on their
own; nothing previously called them together. This script is deliberately thin orchestration --
it adds no new extraction or indexing logic of its own (specs/150-setting-build-command/spec.md
FR-002):

  1. Run Pass 0's existing catalogue/gap-report step, unmodified.
  2. For every `present`-status catalogue record, read its file's text and build the document
     dict `corpus_pipeline.build_setting_corpus_indexes` (#101) requires -- reusing Pass 0's own
     per-document `content_hash` as the sole staleness signal (FR-006), never a second hash.
  3. Skip the corpus-index step entirely when nothing changed since the last build (a second run
     with an unchanged library does no work and writes nothing -- FR-005), otherwise rebuild the
     full `documents`/`nouns`/`terms`/`tables` index set and record what was built.
  4. Report what was processed and what was skipped, and why (FR-007).

The scenarios/arcs (fifth) index is out of scope here -- its one-model-call-per-adventure,
lazy-on-first-need build is explicitly excluded from the scheduled/deterministic run
(docs/design/26-corpus-index.md's "Scheduled execution" section; FR-009).

This script never reads, writes, or otherwise touches any real wyrd-setting-* repository's
content, and never fetches or embeds source material -- it operates on a <setting-dir> the
caller supplies, and this repo's own tests exercise it only against fixtures under
tools/fixtures/setting_build/ (CLAUDE.md's repository table).

Usage:
    python3 tools/setting_build.py <setting-dir>
    python3 tools/setting_build.py <setting-dir> --format json

Python 3.11+, standard library only (docs/design/27-tooling.md section 2).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO_ROOT / "engine"))

import setting_pass0 as pass0  # noqa: E402
from wyrd import corpus_pipeline  # noqa: E402

CACHE_FILENAME = "corpus_build_cache.json"


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class CorpusBuildCache:
    generated_at: str
    setting: str
    documents: dict[str, str] = field(default_factory=dict)  # path -> content_hash

    def to_json(self) -> dict:
        return asdict(self)


def load_corpus_build_cache(setting_dir: Path) -> CorpusBuildCache | None:
    """The previous run's cache, or `None` if this setting directory has never been built."""
    cache_path = setting_dir / "index" / CACHE_FILENAME
    if not cache_path.exists():
        return None
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    return CorpusBuildCache(
        generated_at=data.get("generated_at", _now()),
        setting=data.get("setting", ""),
        documents=data.get("documents", {}),
    )


def write_corpus_build_cache(setting_dir: Path, setting: str, documents: dict[str, str]) -> Path:
    index_dir = setting_dir / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    path = index_dir / CACHE_FILENAME
    cache = CorpusBuildCache(generated_at=_now(), setting=setting, documents=dict(documents))
    path.write_text(json.dumps(cache.to_json(), indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


def corpus_step_needed(
    present_records: list[pass0.CatalogueRecord], setting: str, cache: CorpusBuildCache | None
) -> bool:
    """Whether the corpus-index step must (re)build, per FR-005/FR-006.

    `True` when there is no prior cache, the setting name differs from the cache's own, or the
    current present-record `(path, content_hash)` set differs at all from the cache's -- an
    addition, a removal, or a changed hash. `False` only on an exact match, in which case the
    corpus-index step does no work this run.
    """
    if cache is None or cache.setting != setting:
        return True
    current = {r.path: r.content_hash for r in present_records}
    return current != cache.documents


def build_corpus_document(record: pass0.CatalogueRecord, text: str, setting: str) -> dict:
    """The document dict `corpus_pipeline.build_setting_corpus_indexes` requires, built from one
    present catalogue record and its file's already-read text (FR-003).

    Fields `build_setting_corpus_indexes` needs that Pass 0's own catalogue record does not carry
    (`system`, `edition`, `page_count`, `extraction_method`) get documented, reasonable defaults
    (spec.md Assumptions) -- deriving them precisely is outside both #100's and #101's own
    delivered scope. `document_type` reuses Pass 0's own `kind`, the closest existing signal.
    `world_category` is always `None`: Pass 0's `CatalogueRecord` carries no such field today
    (spec.md Edge Cases), so this command never excludes a document from `terms`/`tables`.
    """
    return {
        "id": record.id,
        "path": record.path,
        "system": "unspecified",
        "edition": "unspecified",
        "document_type": record.kind,
        "page_count": 0,
        "extraction_method": "plain-text",
        "text": text,
        "setting": setting,
        "world_category": None,
    }


def run_corpus_step(setting_dir: Path, catalogue: pass0.Catalogue, setting: str) -> dict:
    """Build (or skip) the four deterministic corpus indexes for `setting_dir`'s present
    documents. Returns the `corpus` report sub-object (FR-007)."""
    present = [r for r in catalogue.records.values() if r.status == "present"]
    cache = load_corpus_build_cache(setting_dir)

    if not corpus_step_needed(present, setting, cache):
        return {
            "built": False,
            "documents": len(present),
            "skipped_reason": "no catalogue or corpus-index changes since the last build",
        }

    library_dir = setting_dir / "library"
    documents = []
    for record in present:
        text = (library_dir / record.path).read_text(encoding="utf-8")
        documents.append(build_corpus_document(record, text, setting))

    indexes = corpus_pipeline.build_setting_corpus_indexes(documents)

    index_dir = setting_dir / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / "documents.json").write_text(
        json.dumps(indexes["documents"], indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    (index_dir / "nouns.json").write_text(
        json.dumps(indexes["nouns"], indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    (index_dir / "terms.json").write_text(
        json.dumps(indexes["terms"], indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    (index_dir / "tables.json").write_text(
        json.dumps(indexes["tables"], indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    write_corpus_build_cache(setting_dir, setting, {r.path: r.content_hash for r in present})

    return {"built": True, "documents": len(present), "skipped_reason": None}


def run(setting_dir: Path) -> dict:
    """Run Pass 0 then the corpus-index step end to end against `setting_dir` (FR-001).

    Returns the combined report: Pass 0's own summary fields plus a `corpus` sub-object.
    """
    pass0_summary = pass0.run(setting_dir)
    catalogue = pass0.load_catalogue(setting_dir)
    setting = setting_dir.name
    corpus_summary = run_corpus_step(setting_dir, catalogue, setting)

    return {**pass0_summary, "corpus": corpus_summary}


def _format_text(summary: dict) -> str:
    lines = [
        f"Pass 0: {len(summary['processed'])} processed, {len(summary['removed'])} removed, "
        f"{summary['gaps']} gaps, {summary['conflicts']} conflicts."
    ]
    corpus = summary["corpus"]
    if corpus["built"]:
        lines.append(f"Corpus indexes: built ({corpus['documents']} documents).")
    else:
        lines.append(f"Corpus indexes: skipped -- {corpus['skipped_reason']}.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("setting_dir", help="path to a setting repo (or fixture) with a library/")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    setting_dir = Path(args.setting_dir)
    if not setting_dir.is_dir() or not (setting_dir / "library").is_dir():
        print(f"error: {setting_dir} has no library/ subdirectory", file=sys.stderr)
        return 1

    try:
        summary = run(setting_dir)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(summary))
    else:
        print(_format_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
