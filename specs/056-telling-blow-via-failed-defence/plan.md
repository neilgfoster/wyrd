# Implementation Plan: Clarify how telling blow is computed via a failed defence roll

**Branch**: `156-telling-blow-failed-defence` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Resolve #155: a blow landing via a failed defence roll can trigger a telling blow, computed via
the virtual-roll symmetry `check_conversion.py`'s own damage-multiplier modelling for ADR 0028
already assumed (`virtual_eff = 100 − eff_def`, `virtual_roll = 101 − r`, then §1's degrees
formula on the virtual inputs). Recorded as ADR 0044. `03-rules.md` §2 states the per-roll
procedure explicitly. `check_defence_telling.py` proves the procedure reproduces
`check_conversion.py`'s own aggregate rate exactly at every effective% from 5-95 in steps of 5,
confirming ADR 0028's published figures need no re-derivation. §7's playtest gains a note pointing
to the resolution without rewriting its own worked example.

## Technical Context

**Language/Version**: Python 3 (verification script only; no engine code).

**Testing**: `python3 specs/056-telling-blow-via-failed-defence/check_defence_telling.py`,
`python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, `python3 -m pytest -q`.

**Constraints**: The stated procedure must be verified computationally against
`check_conversion.py`'s existing modelling, not asserted (FR-003). ADR 0028's figures confirmed,
not re-derived, unless the check fails (FR-004).

**Scale/Scope**: One new ADR, one `03-rules.md` §2 edit (two degrees bullets), one new
verification script, one playtest-transcript note, `docs/README.md`'s ADR index entry.

## Constitution Check

- **A real rejected alternative, someone would re-propose it** — attack-only telling blow is
  workable and was actually used in #148's playtest. Earns an ADR. PASS.
- **Design documents rewritten in place** — `03-rules.md`'s degrees bullets are rewritten, not
  appended to with a changelog note. PASS.
- **Deterministic over inference** — the procedure is verified against `check_conversion.py`'s own
  modelling by direct computation, not asserted to match. PASS.
- **No setting or system names** — none introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/056-telling-blow-via-failed-defence/
├── plan.md, spec.md, tasks.md
├── checklists/requirements.md
└── check_defence_telling.py
```

### Repository changes

```text
docs/adr/0044-telling-blow-via-a-failed-defence-roll-is-symmetric.md   # new ADR
docs/README.md                                                          # ADR index entry
docs/design/03-rules.md                                                 # §2 degrees bullets rewritten
docs/design/30-playtest-transcript.md                                   # §7 resolution note, §13 status update
```

## Complexity Tracking

*(empty — no constitution violations)*
