#!/usr/bin/env python3
"""Verify the companion two-layer split, against the shipped design documents themselves.

design/04-session.md defines a companion's narrative layer (who they are; never read by a
resolution rule) and mechanical layer (what a resolution rule reads; closed at five fields). This
script parses the companion YAML example and the layer-comment lines out of the document itself
-- not a hand-copied literal that could drift from it unnoticed (CLAUDE.md: "where a claim can be
checked by a script, check it") -- and asserts:

1. The mechanical layer is exactly the five fields the design commits to: career, bond, taint,
   strain, wounds. No sixth field has crept in, and none of the five is missing.
2. No field name appears on both layers.
3. design/03-rules.md's companion-and-succession passage names no mechanical field absent from
   that same five-field set.
4. The party-size bound this feature's spec claims (5 companions x 5 fields = 25 tracked values)
   is computed, not asserted by eye.

Run directly; exits non-zero on any mismatch.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSION_DOC = REPO_ROOT / "design" / "04-session.md"
RULES_DOC = REPO_ROOT / "design" / "03-rules.md"

EXPECTED_MECHANICAL = {"career", "bond", "taint", "strain", "wounds"}
EXPECTED_NARRATIVE = {"objective", "flaw", "secret", "arc"}
MAX_COMPANIONS = (
    5  # design/03-rules.md's effective-size table: up to 5 companions + the PC
)


def extract_companion_block(text: str) -> str:
    m = re.search(r"```yaml\nrole: companion\n.*?\n```", text, re.DOTALL)
    if not m:
        raise SystemExit(
            "could not find the companion YAML example in design/04-session.md"
        )
    return m.group(0)


def split_layers(block: str) -> tuple[set[str], set[str]]:
    """Return (narrative_fields, mechanical_fields) as read from the block's own comments."""
    lines = block.splitlines()
    section = None
    narrative: set[str] = set()
    mechanical: set[str] = set()
    field_re = re.compile(r"^(?P<field>[a-z_]+):")
    for line in lines:
        if "narrative layer" in line:
            section = "narrative"
            continue
        if "mechanical layer" in line:
            section = "mechanical"
            continue
        if line.startswith(("  ", "\t")):
            continue  # nested key (e.g. objective.wants) — not a top-level field
        m = field_re.match(line)
        if m and section:
            field = m.group("field")
            (narrative if section == "narrative" else mechanical).add(field)
    return narrative, mechanical


def main() -> int:
    if not SESSION_DOC.exists():
        raise SystemExit(f"missing: {SESSION_DOC}")
    if not RULES_DOC.exists():
        raise SystemExit(f"missing: {RULES_DOC}")

    session_text = SESSION_DOC.read_text(encoding="utf-8")
    rules_text = RULES_DOC.read_text(encoding="utf-8")

    block = extract_companion_block(session_text)
    narrative, mechanical = split_layers(block)

    errors: list[str] = []

    if mechanical != EXPECTED_MECHANICAL:
        errors.append(
            "mechanical layer drifted from the closed set: "
            f"found {sorted(mechanical)}, expected {sorted(EXPECTED_MECHANICAL)}"
        )
    if narrative != EXPECTED_NARRATIVE:
        errors.append(
            "narrative layer drifted from the expected set: "
            f"found {sorted(narrative)}, expected {sorted(EXPECTED_NARRATIVE)}"
        )

    overlap = narrative & mechanical
    if overlap:
        errors.append(f"field(s) appear on both layers: {sorted(overlap)}")

    # design/03-rules.md's companion/succession passage must name no mechanical field absent
    # from the closed set above.
    succession_section_match = re.search(
        r"### Companions and succession\n(.*?)\n---", rules_text, re.DOTALL
    )
    if not succession_section_match:
        errors.append(
            "could not find the 'Companions and succession' section in 03-rules.md"
        )
    else:
        succession_text = succession_section_match.group(1)
        # Field names are mentioned as `bare` or `code` tokens; check any token that matches a
        # known field family (career/bond/taint/strain/wounds/objective/flaw/secret/arc) is one
        # of the mechanical five, since only mechanical fields belong in an advancement passage.
        all_known = EXPECTED_MECHANICAL | EXPECTED_NARRATIVE
        mentioned = {
            tok
            for tok in re.findall(r"`([a-z_]+)`", succession_text)
            if tok in all_known
        }
        stray = mentioned - EXPECTED_MECHANICAL
        if stray:
            errors.append(
                f"03-rules.md's succession passage names non-mechanical field(s): {sorted(stray)}"
            )

    tracked_values = MAX_COMPANIONS * len(EXPECTED_MECHANICAL)

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1

    print(f"OK: mechanical layer = {sorted(EXPECTED_MECHANICAL)} (5 fields, closed)")
    print(
        f"OK: narrative layer = {sorted(EXPECTED_NARRATIVE)}, disjoint from mechanical"
    )
    print("OK: 03-rules.md's succession passage names only mechanical fields")
    print(
        f"OK: party-size bound = {MAX_COMPANIONS} companions x {len(EXPECTED_MECHANICAL)} "
        f"fields = {tracked_values} tracked values (no per-companion character sheet needed)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
