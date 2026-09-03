#!/usr/bin/env python3
"""Check that every mechanic named in docs/design/ is defined somewhere in docs/design/.

At least six mechanics were referenced before they were defined -- engine characteristics in
the conversion contract, Standing in Upkeep, `party_effective` in the danger formula, the
damage-type critical tables, the skill list, and the wound schema -- each reading as
authoritative. Prose review caught none of them. This is the guard, per
docs/design/27-tooling.md section 1: where a claim can be checked, check it.

A **definition** is a place a mechanic's name is established: a Markdown heading naming it, a
table row whose leading cell names it, or a glossary-style `**Term**: explanation` entry. A
**reference** is a *candidate mechanic name* found elsewhere in prose or table cells, outside
fenced code blocks and inline code spans -- detected structurally, not by first looking up a
known vocabulary (a reference to a mechanic that was never defined anywhere must still be
detectable, or the check could never fail). Two shapes count as a reference candidate:

  - a snake_case identifier (`party_effective`) -- unambiguous, code-styled;
  - a run of two or more consecutive Capitalized Words ("Skill List", "Wound Schema").

A single bare capitalized word (e.g. "Standing" on its own) is deliberately **not** treated as
a reference candidate: prose capitalizes far too many ordinary words mid-sentence (abbreviations,
list continuations, emphasis) for that signal to be reliable, and a first working version of
this check that tried it produced over a thousand false positives against this repo's own
`docs/design/` tree on the very first run. Multi-word phrases and code-styled identifiers are the
line this check draws between a mechanic's proper name and incidental capitalization -- see
research.md's "definitions and references are detected structurally, not semantically" decision
and its FR-010 trade-off (favouring precision over full recall).

A reference candidate whose exact text matches no definition anywhere under docs/design/ is a
dangling reference.

The vocabulary is derived from docs/design/ itself on every run rather than hand-maintained
(CLAUDE.md fault class 4, "stale but plausible specifications") -- there is no separate list
of mechanic names to fall behind the documents.

specs/ is out of scope, same as tools/check_docs.py's reachability exemption: a spec is the
record of one past change, not the present description, and may legitimately use a
since-superseded name.

Usage:
    python3 tools/check_dangling_mechanics.py
    python3 tools/check_dangling_mechanics.py --format json

Python 3.11+, standard library only (docs/design/27-tooling.md). Reads the filesystem, nothing else.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass

DESIGN_DIR = "docs/design"

SKIP_PARTS = {
    ".git",
    ".specify",
    ".claude",
    ".pytest_cache",
    "node_modules",
    "__pycache__",
}

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")

HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
# A table row: starts and ends (loosely) with a pipe, is not the `|---|` separator row.
TABLE_ROW = re.compile(r"^\s*\|\s*([^|]+?)\s*\|")
TABLE_SEPARATOR = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
# A glossary entry: an (optionally bulleted) bolded term followed by a colon/dash and prose.
GLOSSARY_ENTRY = re.compile(r"^\s*(?:[-*]\s+)?\*\*([^*]+)\*\*\s*[:—-]")

# Markdown emphasis/code markup to strip from a captured name before treating it as the
# mechanic's canonical spelling.
STRIP_MARKUP = re.compile(r"[*_`]")

# Reference-candidate shapes -- see module docstring.
SNAKE_CASE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
TITLE_PHRASE = re.compile(r"\b(?:[A-Z][a-zA-Z]*\s+){1,4}[A-Z][a-zA-Z]*\b")

MIN_NAME_LENGTH = 3

# Ordinary English function words that end up capitalized only because a Title Phrase match
# happened to start at the beginning of a sentence ("The GM MUST...", "A Fate point..."), not
# because the phrase is a mechanic's proper name. A phrase opening with one of these is
# dropped rather than reported.
LEADING_STOPWORDS = {
    "the",
    "a",
    "an",
    "this",
    "that",
    "these",
    "those",
    "if",
    "when",
    "while",
    "where",
    "each",
    "some",
    "all",
    "two",
    "three",
    "at",
    "on",
    "in",
    "for",
    "with",
    "by",
    "from",
    "as",
    "is",
    "are",
    "was",
    "were",
    "and",
    "or",
    "but",
    "so",
    "no",
    "not",
}

# tools/check_*.py script names are Wyrd tooling, documented in tools/ itself -- not a design
# mechanic that docs/design/ is responsible for defining.
SCRIPT_NAME_PREFIX = "check_"


class Problem(str):
    """A human-readable failure. Subclassing str keeps JSON output trivial."""


@dataclass(frozen=True)
class MechanicDefinition:
    name: str
    source: pathlib.Path
    kind: str
    line: int


@dataclass(frozen=True)
class MechanicReference:
    name: str
    source: pathlib.Path
    line: int
    context: str


def is_skipped(path: pathlib.Path, root: pathlib.Path) -> bool:
    if SKIP_PARTS & set(path.parts):
        return True
    rel = path.relative_to(root).as_posix()
    return rel.startswith("specs/")


def design_files(root: pathlib.Path) -> list[pathlib.Path]:
    design = root / DESIGN_DIR
    if not design.is_dir():
        return []
    return sorted(p for p in design.rglob("*.md") if not is_skipped(p, root))


def _clean(name: str) -> str:
    return STRIP_MARKUP.sub("", name).strip().rstrip(":").strip()


def _fenced_lines(text: str) -> list[bool]:
    """One bool per line: True if that line is inside (or is) a fenced code block."""
    fenced, in_fence = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced.append(True)
            in_fence = not in_fence
            continue
        fenced.append(in_fence)
    return fenced


def _definition_line(line: str) -> str | None:
    """Which structural kind a line matches, if any -- used to exclude it from reference scan."""
    if TABLE_SEPARATOR.match(line):
        return "separator"
    if HEADING.match(line):
        return "heading"
    if TABLE_ROW.match(line):
        return "table_row"
    if GLOSSARY_ENTRY.match(line):
        return "glossary"
    return None


def find_definitions(root: pathlib.Path) -> list[MechanicDefinition]:
    definitions: list[MechanicDefinition] = []
    for path in design_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        in_fence = _fenced_lines(text)
        for i, line in enumerate(lines):
            if in_fence[i]:
                continue

            m = HEADING.match(line)
            if m:
                name = _clean(m.group(1))
                if len(name) >= MIN_NAME_LENGTH:
                    definitions.append(MechanicDefinition(name, path, "heading", i + 1))
                continue

            if TABLE_SEPARATOR.match(line):
                continue

            m = TABLE_ROW.match(line)
            if m:
                name = _clean(m.group(1))
                if len(name) >= MIN_NAME_LENGTH:
                    definitions.append(MechanicDefinition(name, path, "table_row", i + 1))
                continue

            m = GLOSSARY_ENTRY.match(line)
            if m:
                name = _clean(m.group(1))
                if len(name) >= MIN_NAME_LENGTH:
                    definitions.append(MechanicDefinition(name, path, "glossary", i + 1))
    return definitions


def _reference_candidates(line: str) -> list[tuple[int, int, str]]:
    """Candidate (start, end, name) spans in one already-code-stripped prose/table line."""
    spans: list[tuple[int, int, str]] = []

    for m in SNAKE_CASE.finditer(line):
        if m.group(0).startswith(SCRIPT_NAME_PREFIX):
            continue
        spans.append((m.start(), m.end(), m.group(0)))

    for m in TITLE_PHRASE.finditer(line):
        words = m.group(0).split()
        if words[0].lower() in LEADING_STOPWORDS:
            continue
        # RFC2119-style directives ("MUST NOT", "SHOULD NOT") are all-uppercase keywords, not
        # mechanic names -- docs/design/01-principles.md's GM contract vocabulary, not this check's
        # concern.
        if all(w.isupper() for w in words):
            continue
        spans.append((m.start(), m.end(), m.group(0)))

    # Resolve overlaps: longer spans win (a Title Phrase should absorb the single-word
    # candidates inside it), earliest start breaks ties.
    resolved: list[tuple[int, int, str]] = []
    for start, end, name in sorted(spans, key=lambda s: (-(s[1] - s[0]), s[0])):
        if any(not (end <= r_start or start >= r_end) for r_start, r_end, _ in resolved):
            continue
        resolved.append((start, end, name))
    return sorted(resolved)


def _strip_inline_code(text: str) -> str:
    """Blank out inline code spans across the whole document, preserving line count.

    A backtick span can open on one line and close on a later one (e.g. a formula wrapped for
    line length) -- stripping per line, as check_docs.py's own strip_code does for wikilinks,
    misses that case entirely. `[^`]*` already matches newlines without re.DOTALL, so a
    document-wide substitution catches a multi-line span; replacing the match with one newline
    per newline it contained keeps every later line's number aligned with the original text.
    """
    return INLINE_CODE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def find_references(root: pathlib.Path) -> list[MechanicReference]:
    references: list[MechanicReference] = []
    for path in design_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        stripped = _strip_inline_code(text)
        lines = stripped.splitlines()
        raw_lines = text.splitlines()
        in_fence = _fenced_lines(text)
        for i, line in enumerate(lines):
            if in_fence[i]:
                continue
            raw_line = raw_lines[i]
            if _definition_line(raw_line) is not None:
                continue
            for _, _, name in _reference_candidates(line):
                if len(name) < MIN_NAME_LENGTH:
                    continue
                references.append(MechanicReference(name, path, i + 1, raw_line.strip()))
    return references


def find_problems(root: pathlib.Path) -> list[Problem]:
    """Every dangling reference, in file order. Pure over the tree, so the tests call this."""
    definitions = find_definitions(root)
    vocabulary = {d.name for d in definitions}

    references = find_references(root)

    problems: list[Problem] = []
    for ref in references:
        if ref.name in vocabulary:
            continue
        # "Maximum Stamina" qualifies an already-defined "Stamina"; the phrase is a modified
        # reference to a known mechanic, not a new undefined one. Exact-name drift between the
        # qualifier and the base term is a different fault (cross-document contradiction,
        # CLAUDE.md class 3) that this feature's spec explicitly leaves out of scope.
        last_word = ref.name.rsplit(None, 1)[-1]
        if last_word in vocabulary:
            continue
        if last_word.endswith("s") and last_word[:-1] in vocabulary:
            continue  # a plain plural of an already-defined term ("Fault Lines" / "Fault Line")
        rel = ref.source.relative_to(root).as_posix()
        problems.append(
            Problem(
                f"{rel}:{ref.line}: '{ref.name}' is referenced but not defined anywhere in "
                f"{DESIGN_DIR}/"
            )
        )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--root", default=".", help="repository root (default: cwd)")
    args = parser.parse_args(argv)

    root = pathlib.Path(args.root).resolve()
    problems = find_problems(root)
    definitions = len(find_definitions(root))
    references = len(find_references(root))

    if args.format == "json":
        print(
            json.dumps(
                {
                    "definitions": definitions,
                    "references": references,
                    "problems": list(map(str, problems)),
                },
                indent=2,
            )
        )
        return 1 if problems else 0

    if not problems:
        print(
            f"tools/check_dangling_mechanics.py: {definitions} mechanic definitions, "
            f"{references} references, 0 dangling"
        )
        return 0

    for problem in problems:
        print(problem)
    print(f"tools/check_dangling_mechanics.py: {len(problems)} dangling references found")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
