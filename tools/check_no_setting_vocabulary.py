#!/usr/bin/env python3
"""Confirm no setting or system name has reached docs/design/ or README.md.

CLAUDE.md: "No setting or system names in docs/design/ or README.md -- not in prose, not in
examples, not in a table row." That rule has held by review discipline alone until now; this
script makes it checkable rather than asserted, per Stage 13's own closing requirement (#92).

The denylist is derived from settings.yaml -- the actual, current catalogue of settings this repo
knows about -- rather than a hand-maintained list that could drift from it. Each setting's `id`
(split on '-' into its distinctive tokens) and `title` (as a whole phrase, and split on '/',
':' and '(' into its distinctive clauses) contributes search terms. Generic English words that
happen to be an id or a title clause on their own (e.g. a one-word title) are dropped from the
denylist -- a setting titled a common word would otherwise make this check fail on unrelated
prose, which is exactly the false-positive-tolerant posture tools/check_dangling_mechanics.py
already established for a different kind of pattern in this repo.

Run: python3 tools/check_no_setting_vocabulary.py
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SETTINGS_YAML = ROOT / "settings.yaml"
DESIGN_DIR = ROOT / "docs" / "design"
README = ROOT / "README.md"

# Terms too generic to search for on their own -- a real English word or a bare acronym that
# would false-positive against ordinary engine prose. Excluded from the denylist entirely,
# the same posture as check_dangling_mechanics.py's own tolerated gaps.
TOO_GENERIC = {
    "tor",
    "titan",
    "1st",
    "2nd",
    "3rd",
    "4th",
    "edition",
    "the",
    "and",
    "domesday",
}


def load_settings_terms() -> list[str]:
    """Extract id/title search terms from settings.yaml without a YAML dependency.

    settings.yaml is simple, hand-written `key: value` and `- id: value` lines -- the same
    restricted subset tools/check_bestiary.py's own reader targets. This only needs `id:` and
    `title:` scalars, so a couple of regexes suffice.
    """
    text = SETTINGS_YAML.read_text()
    ids = re.findall(r"^\s*-\s*id:\s*(\S+)\s*$", text, re.MULTILINE)
    titles = re.findall(r'^\s*title:\s*"([^"]+)"\s*$', text, re.MULTILINE)

    terms: set[str] = set()
    for id_ in ids:
        for token in id_.split("-"):
            terms.add(token)
    for title in titles:
        # The whole title is a term (longer phrases are the safest, most specific matches).
        terms.add(title)
        # Its clauses split on common separators, so "Dark Heresy -- the Calixis Sector"
        # also contributes "Dark Heresy" and "the Calixis Sector" as standalone terms.
        for clause in re.split(r"[—:/(),]", title):
            clause = clause.strip()
            if clause:
                terms.add(clause)

    return sorted(t for t in terms if t.lower() not in TOO_GENERIC and len(t) > 3)


def scan(terms: list[str], targets: list[pathlib.Path]) -> list[str]:
    problems = []
    patterns = [(t, re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)) for t in terms]
    for path in targets:
        text = path.read_text()
        for line_no, line in enumerate(text.splitlines(), start=1):
            for term, pattern in patterns:
                if pattern.search(line):
                    rel = path.relative_to(ROOT)
                    problems.append(
                        f"{rel}:{line_no}: setting/system term '{term}' found: {line.strip()[:100]}"
                    )
    return problems


def main() -> int:
    terms = load_settings_terms()
    targets = sorted(DESIGN_DIR.glob("*.md")) + [README]
    problems = scan(terms, targets)

    print(
        f"Checked {len(targets)} files against {len(terms)} setting/system terms "
        f"(from {SETTINGS_YAML.relative_to(ROOT)})."
    )
    if problems:
        print("FAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("No setting or system vocabulary found in docs/design/ or README.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
