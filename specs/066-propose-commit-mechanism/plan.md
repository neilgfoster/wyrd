# Implementation Plan: The base propose/commit mechanism — staged rolls and mutations

**Branch**: `193-propose-commit-mechanism` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

New design document `docs/design/31-action-resolution.md` specifies the base `propose`/
`commit`/`discard` mechanism (ADR 0050): `propose` resolves one roll against state, looks up
everything itself, stages any implied mutation, and writes nothing; `commit` applies exactly the
staged mutations atomically; `discard` writes nothing. A worked example (a real seeded Exposure
test) shows state unchanged before commit and correctly mutated after. `02-architecture.md`'s
CLI sketch gains the three verbs, replacing the previously unstaged `wyrd roll`; `damage`/
`track` are flagged as a known follow-up, not silently left inconsistent.

## Technical Context

**Language/Version**: N/A — this is a design specification; no code is implemented here.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`.

**Constraints**: Cascading resolution, partial reroll, and Omen carryover are explicitly out of
scope (FR-008) — each is a separate, dependent feature under #192.

**Scale/Scope**: One new design document, one new ADR, `02-architecture.md`'s CLI sketch and
Memory-tiers cross-reference, `README.md`'s doc index.

## Constitution Check

- **A real rejected alternative, someone would re-propose it** — "commit immediately, reverse on
  reroll" is workable and would plausibly be proposed by someone who hadn't traced through the
  cascade-reversal problem. Earns ADR 0050. PASS.
- **Design documents rewritten in place / linked from the hub** — new document added and linked
  from `README.md`, per this repo's own reachability check. PASS.
- **Deterministic over inference** — the worked example uses a real seeded roll, not asserted
  arithmetic. PASS.
- **Setting-agnostic** — no setting or system name introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/066-propose-commit-mechanism/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/adr/0050-action-resolution-proposes-before-it-commits.md   # new ADR
docs/README.md                                                    # ADR index entry
docs/design/31-action-resolution.md                               # new design document
docs/design/02-architecture.md                                    # CLI sketch, cross-references
README.md                                                          # doc index entry
```

## Complexity Tracking

*(empty — no constitution violations)*
