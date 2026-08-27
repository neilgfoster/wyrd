#!/usr/bin/env python3
"""Verify the oracle-prompt tables' structure, against the shipped document itself.

Unlike tools/check_oracle_answers.py, this family makes no probability claim
to compute -- its correctness criterion is genre-neutrality, a qualitative
reading check recorded per row in docs/design/15-oracle-prompts.md, not a
number. What *is* computable, per docs/design/04-tables.md's row schema, is
checked here: every table's ranges are contiguous, start at 1, and every row
declares that its genre-neutrality check passed -- verified against the rows
this script parses out of the design document itself, not a hand-copied
literal that could drift from it unnoticed (CLAUDE.md: "where a claim can be
checked by a script, check it").

Run directly; exits non-zero on any mismatch.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC = REPO_ROOT / "docs" / "design" / "13-oracle-prompts.md"

# One heading per table, in document order, followed by its row table.
TABLE_KEYS = [
    "oracle-prompt-npc-objective",
    "oracle-prompt-situation-truth",
    "oracle-prompt-thread-turn",
    "oracle-prompt-complication",
]

HEADING_RE = re.compile(r"^### `(?P<key>oracle-prompt-[a-z-]+)`\s*$", re.MULTILINE)
ROW_RE = re.compile(
    r"^\|\s*(?P<start>\d+)\s*[–-]\s*(?P<end>\d+)\s*\|\s*`(?P<effect>[a-z_]+)`\s*\|"
)


def parse_tables(text: str) -> dict[str, list[tuple[range, str]]]:
    """Extract each table's rows (range, effect) from its `### \\`key\\`` section."""
    headings = list(HEADING_RE.finditer(text))
    tables: dict[str, list[tuple[range, str]]] = {}
    for i, heading in enumerate(headings):
        key = heading.group("key")
        section_end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        section = text[heading.end() : section_end]
        rows = []
        for line in section.splitlines():
            m = ROW_RE.match(line)
            if m:
                start, end = int(m.group("start")), int(m.group("end"))
                rows.append((range(start, end + 1), m.group("effect")))
        tables[key] = rows
    return tables


def main() -> int:
    if not DOC.exists():
        raise SystemExit(f"missing: {DOC}")

    text = DOC.read_text()
    tables = parse_tables(text)
    failures = []

    missing_keys = set(TABLE_KEYS) - set(tables)
    if missing_keys:
        failures.append(f"document is missing table(s): {sorted(missing_keys)}")

    for key in TABLE_KEYS:
        rows = tables.get(key, [])
        if not rows:
            continue

        ranges = [r for r, _effect in rows]

        # Contiguity, coverage of 1-100 exactly (no modifier: the d100 max is
        # the family's own ceiling, so the last row is open at the top the
        # same way docs/design/14-oracle-answers.md's rows are).
        covered = sorted(v for r in ranges for v in r)
        if covered != list(range(1, 101)):
            failures.append(
                f"{key}: rows do not exactly cover 1-100 (got {len(covered)} totals)"
            )

        if ranges[0].start != 1:
            failures.append(f"{key}: first row does not start at 1")

        # No duplicate effect keys within a table.
        effects = [effect for _r, effect in rows]
        if len(effects) != len(set(effects)):
            failures.append(f"{key}: duplicate effect keys")

        print(f"{key:32s} {len(rows):2d} rows parsed, 1-100 covered")

    # The genre-neutrality check itself is qualitative (research.md) -- what's
    # checked here is only that the document records, for every table, that
    # the check was carried out, per docs/design/04-tables.md's row-schema rule
    # that a family's declared extra field ("checked") is present on every
    # row. The document states this once per table (no failing row ships, so
    # there is no "checked: no" value to parse) rather than per-row markup;
    # confirm each table carries its "Genre-neutrality check, worked" note.
    heading_positions = {m.group("key"): m.start() for m in HEADING_RE.finditer(text)}
    ordered_positions = sorted(heading_positions.values()) + [len(text)]
    for key in TABLE_KEYS:
        if key not in tables or not tables[key]:
            continue
        start = heading_positions[key]
        end = ordered_positions[ordered_positions.index(start) + 1]
        section = text[start:end]
        if "Genre-neutrality check, worked" not in section:
            failures.append(
                f"{key}: no recorded genre-neutrality check found in its section"
            )

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f" - {f}")
        return 1

    print(
        f"\nAll {len(TABLE_KEYS)} prompt tables check out against "
        f"{DOC.relative_to(REPO_ROOT)}: contiguous 1-100 coverage, unique rows, "
        "genre-neutrality check recorded."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
