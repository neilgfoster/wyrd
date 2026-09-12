#!/usr/bin/env python3
"""Pass 0: catalogue a setting's library, survey engine gaps, and stay idempotent.

docs/design/24-authoring-a-setting.md gives the shape of a finished setting repository, but
nothing before this script turned an unindexed `library/` into a known, ordered inventory --
each setting has done that step ad hoc (issue #100). This is that step:

  catalogue      one record per file under library/, classified by kind and authority tier
  ordering       core rules, then expansions, then community material, then scenarios/adventures
                 -- a lower-authority document never silently outranks a higher one
  gap report     which of docs/design/24-authoring-a-setting.md's requirements this library does
                 not yet evidence coverage for
  idempotence    a content hash per file; an unchanged file is never reclassified on a re-run
  conflicts      two documents at different authority tiers sharing a kind+subject are recorded
                 as a conflict, never resolved by overwriting either one's own record

Classification is signal-based (front matter, or a path/kind hint), never full-text extraction
or a model call -- Pass 0 is deliberately the cheap pass that runs before anything is imported
(docs/design/27-tooling.md's deterministic-over-inference rule; issue #100's own "cheap enough to
re-run whenever material is added").

This script never reads, writes, or otherwise touches any real wyrd-setting-* repository's
content -- it operates on a <setting-dir> the caller supplies, and this repo's own tests exercise
it only against fixtures under tools/fixtures/pass0/ (CLAUDE.md's repository table).

Usage:
    python3 tools/setting_pass0.py <setting-dir>
    python3 tools/setting_pass0.py <setting-dir> --format json

Python 3.11+, standard library only (docs/design/27-tooling.md section 2).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

# --- the closed authority-tier vocabulary, in processing order (issue #100) ---

AUTHORITY_TIERS: dict[str, int] = {
    "core-rules": 0,
    "expansion": 1,
    "community": 2,
    "scenario": 3,
    "unclassified": 4,
}

# --- the fixed setting-authoring requirement table (docs/design/24-authoring-a-setting.md) ---
# Pass 0 reads this document's own requirements rather than re-deriving a second list
# (research.md's decision -- avoids the "two documents describing one thing differently" fault).

SETTING_REQUIREMENTS: dict[str, str] = {
    "setting-identity": "no material evidences setting.yaml-shaped identity/tone coverage",
    "voice": "no material evidences voice.md-shaped register/tone guidance",
    "careers": "no material evidences careers.yaml-shaped career-graph coverage",
    "gear": "no material evidences gear.yaml-shaped weapons/armour coverage",
    "bestiary": "no material evidences bestiary.yaml-shaped adversary-block coverage",
    "names": "no material evidences names.yaml-shaped naming coverage",
    "calendar": "no material evidences calendar.yaml-shaped calendar coverage",
    "loyalties": "no material evidences loyalties.yaml-shaped Loyalty coverage",
    "drives": "no material evidences drives.yaml-shaped Drive coverage",
    "misfortunes": "no material evidences misfortunes.yaml-shaped Misfortune coverage",
}


@dataclass
class CatalogueRecord:
    id: str
    path: str
    kind: str
    authority_tier: int
    subject: str | None
    content_hash: str | None
    status: str  # "present" | "removed" | "unreadable"
    provides: list[str] = field(default_factory=list)


@dataclass
class Catalogue:
    generated_at: str
    records: dict[str, CatalogueRecord]  # keyed by relative path

    def to_json(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "records": [asdict(r) for r in self.records.values()],
        }


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_file(path: Path) -> str:
    """Return a stable sha256 content hash for a file, prefixed for readability."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest}"


def _parse_front_matter(text: str) -> dict:
    """Parse a minimal '---\\nkey: value\\n---' front-matter block, or return {}.

    Deliberately tiny: scalars, and a single-level flow list `[a, b, c]`. This is not a general
    YAML reader (check_bestiary.py's read_yaml already covers a whole-document YAML file; this
    covers the narrower, embedded front-matter case a source document carries).
    """
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}
    result: dict = {}
    for line in lines[1:end]:
        if not line.strip() or ":" not in line:
            continue
        key, _, raw_value = line.partition(":")
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value.startswith("[") and raw_value.endswith("]"):
            inner = raw_value[1:-1].strip()
            value = [v.strip() for v in inner.split(",") if v.strip()] if inner else []
        elif raw_value in ("", "null", "~"):
            value = None
        else:
            value = raw_value
        result[key] = value
    return result


def classify_document(path: Path) -> tuple[str, int, str | None, list[str]]:
    """Classify a file into (kind, authority_tier, subject, provides).

    Signal-based only: front matter if present and readable as text; otherwise the file is
    `unclassified` at the lowest authority tier (FR-002, FR-009). Never reads a binary file's
    body as text -- a decode failure is treated the same as "no signal found".
    """
    front_matter: dict = {}
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        text = ""
    if text:
        front_matter = _parse_front_matter(text)

    kind = front_matter.get("kind")
    if kind not in AUTHORITY_TIERS:
        kind = "unclassified"
    tier = AUTHORITY_TIERS[kind]
    subject = front_matter.get("subject") or None
    provides = front_matter.get("provides") or []
    if not isinstance(provides, list):
        provides = []
    return kind, tier, subject, provides


def load_catalogue(setting_dir: Path) -> Catalogue:
    catalogue_path = setting_dir / "index" / "catalogue.json"
    if not catalogue_path.exists():
        return Catalogue(generated_at=_now(), records={})
    data = json.loads(catalogue_path.read_text(encoding="utf-8"))
    records = {r["path"]: CatalogueRecord(**r) for r in data.get("records", [])}
    return Catalogue(generated_at=data.get("generated_at", _now()), records=records)


def build_catalogue(
    setting_dir: Path, previous: Catalogue
) -> tuple[Catalogue, list[str], list[str]]:
    """Diff the library against `previous` by content hash. Returns (catalogue, processed, removed).

    `processed` lists the relative paths that were (re)classified this run; a file whose hash is
    unchanged is left byte-for-byte alone in the returned records (FR-006, FR-007).
    """
    library_dir = setting_dir / "library"
    seen: set[str] = set()
    records: dict[str, CatalogueRecord] = dict(previous.records)
    processed: list[str] = []

    for file_path in sorted(p for p in library_dir.rglob("*") if p.is_file()):
        rel = str(file_path.relative_to(library_dir))
        seen.add(rel)
        try:
            content_hash = hash_file(file_path)
        except OSError:
            if rel in records and records[rel].status == "unreadable":
                continue
            records[rel] = CatalogueRecord(
                id=rel,
                path=rel,
                kind="unclassified",
                authority_tier=AUTHORITY_TIERS["unclassified"],
                subject=None,
                content_hash=None,
                status="unreadable",
                provides=[],
            )
            processed.append(rel)
            continue

        existing = records.get(rel)
        if (
            existing is not None
            and existing.content_hash == content_hash
            and existing.status == "present"
        ):
            continue  # unchanged: never reclassified (FR-006)

        kind, tier, subject, provides = classify_document(file_path)
        records[rel] = CatalogueRecord(
            id=rel,
            path=rel,
            kind=kind,
            authority_tier=tier,
            subject=subject,
            content_hash=content_hash,
            status="present",
            provides=provides,
        )
        processed.append(rel)

    removed: list[str] = []
    for rel, record in records.items():
        if rel not in seen and record.status != "removed":
            records[rel] = CatalogueRecord(**{**asdict(record), "status": "removed"})
            removed.append(rel)

    generated_at = previous.generated_at if not processed and not removed else _now()
    return Catalogue(generated_at=generated_at, records=records), processed, removed


def processing_order(catalogue: Catalogue) -> list[CatalogueRecord]:
    """Records sorted core rules -> expansions -> community -> scenarios -> unclassified.

    (FR-003)
    """
    present = [r for r in catalogue.records.values() if r.status == "present"]
    return sorted(present, key=lambda r: (r.authority_tier, r.path))


def detect_conflicts(catalogue: Catalogue) -> list[dict]:
    """Same kind+subject, different authority tiers -> a recorded conflict (FR-008).

    Neither participating record is read from or mutated here -- this only ever appends a new,
    separate conflict entry.
    """
    by_subject: dict[str, list[CatalogueRecord]] = {}
    for record in catalogue.records.values():
        if record.status != "present" or not record.subject:
            continue
        by_subject.setdefault(record.subject, []).append(record)

    conflicts: list[dict] = []
    for subject, records in sorted(by_subject.items()):
        if len({r.authority_tier for r in records}) < 2:
            continue
        conflicts.append(
            {
                "subject": subject,
                "kinds": sorted({r.kind for r in records}),
                "documents": sorted(r.id for r in records),
            }
        )
    return conflicts


def build_gap_report(catalogue: Catalogue) -> list[dict]:
    """Which setting-authoring requirements no present record evidences coverage for (FR-004)."""
    covered: set[str] = set()
    for record in catalogue.records.values():
        if record.status != "present":
            continue
        covered.update(record.provides)
    gaps = []
    for requirement, reason in SETTING_REQUIREMENTS.items():
        if requirement not in covered:
            gaps.append({"requirement": requirement, "reason": reason})
    return gaps


def write_catalogue(setting_dir: Path, catalogue: Catalogue) -> Path:
    index_dir = setting_dir / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    path = index_dir / "catalogue.json"
    path.write_text(
        json.dumps(catalogue.to_json(), indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    return path


def write_gap_report(setting_dir: Path, gaps: list[dict], conflicts: list[dict]) -> Path:
    index_dir = setting_dir / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    path = index_dir / "gap_report.json"
    path.write_text(
        json.dumps({"gaps": gaps, "conflicts": conflicts}, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return path


def run(setting_dir: Path) -> dict:
    """Run Pass 0 end to end against setting_dir. Returns the run summary dict."""
    previous = load_catalogue(setting_dir)
    catalogue, processed, removed = build_catalogue(setting_dir, previous)
    conflicts = detect_conflicts(catalogue)
    gaps = build_gap_report(catalogue)

    if processed or removed:
        write_catalogue(setting_dir, catalogue)
    write_gap_report(setting_dir, gaps, conflicts)

    return {
        "processed": processed,
        "removed": removed,
        "gaps": len(gaps),
        "conflicts": len(conflicts),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("setting_dir", help="path to a setting repo (or fixture) with a library/")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    setting_dir = Path(args.setting_dir)
    if not setting_dir.is_dir() or not (setting_dir / "library").is_dir():
        print(f"error: {setting_dir} has no library/ subdirectory", file=sys.stderr)
        return 1

    summary = run(setting_dir)

    if args.format == "json":
        print(json.dumps(summary))
    else:
        print(
            f"Pass 0: {len(summary['processed'])} processed, {len(summary['removed'])} removed, "
            f"{summary['gaps']} gaps, {summary['conflicts']} conflicts."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
