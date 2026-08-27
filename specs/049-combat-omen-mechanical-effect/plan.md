# Implementation Plan: Combat Omens carry a ±10 modifier on the roller's next roll

**Branch**: `049-combat-omen-mechanical-effect` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add the ±10 combat-Omen roll modifier to `docs/design/03-rules.md` §2, alongside its existing
narrative framing. Record the decision as ADR 0042, since a real alternative (status quo:
narrative-only in combat too) is rejected. Verify with a new script,
`check_omen_effect.py`, extending `specs/018-player-facing-combat/check_conversion.py`'s own
Markov fight model with a pending-modifier state dimension, confirming the shift in expected
damage per round stays under a stated materiality threshold across every representative pairing.

## Technical Context

**Language/Version**: Python 3.11+ stdlib (`fractions`, `functools.lru_cache`) for the
verification script; the rule itself is Markdown.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 tools/check_probability_coverage.py` (extended to cover this new claim),
`python3 -m pytest -q`.

**Constraints**: No stacking, lapses unused (FR-002/FR-003). Additive to narrative framing, not a
replacement (FR-004). Scoped to combat only (FR-005). The verification script must reuse
`check_conversion.py`'s own numbers (armour, weapon, telling threshold, PAIRINGS) rather than
re-deriving them differently, and must use probability-bucket grouping rather than per-natural-roll
enumeration — an early version enumerating 100 rolls per roll, per round, per growing state, was
too slow to finish (a real instance of CLAUDE.md's own recorded "exact-arithmetic scripts are
slow" fault).

**Scale/Scope**: One new ADR (~90 lines), one paragraph added to `03-rules.md` §2, one new
~230-line verification script.

## Constitution Check

- **Nothing unpublishable** — pure rules/verification-script addition. PASS.
- **No setting or system names** — none introduced. PASS.
- **Decisions are recorded** — a real alternative (status quo) is rejected; ADR 0042 records it.
  PASS.
- **Design documents rewritten in place** — the new paragraph sits inside §2's existing bullet
  list. PASS.
- **Deterministic over inference** — the materiality claim is computed, not assumed; a real bug
  in the first draft (parameter mismapping producing identical results across every pairing) was
  caught by the computation's own suspicious output, not trusted because it ran without error.
  PASS.

No violations. No Complexity Tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/049-combat-omen-mechanical-effect/
├── plan.md, spec.md, tasks.md, check_omen_effect.py
└── checklists/requirements.md
```

### Repository changes

```text
docs/adr/0042-combat-omens-carry-a-plus-minus-10-modifier.md   # new
docs/README.md                                                 # ADR index entry added
docs/design/03-rules.md                                        # sec2 gains the Omen rule
```

## Complexity Tracking

*(empty — no constitution violations)*
