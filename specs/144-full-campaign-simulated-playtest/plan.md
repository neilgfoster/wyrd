# Implementation Plan: Full-campaign simulated playtest across every subsystem

**Branch**: `144-full-campaign-simulated-playtest` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

## Summary

Add a new section to `docs/design/30-playtest-transcript.md` (section 19, following the
existing document's numbering) that carries Senna Vask — the character established in section 1
and reused throughout the transcript — through a representative multi-session arc: creation
continuity, at least three sessions each closing at a Rally or downtime step, a conflict
producing harm, the recovery that follows it, at least one economic-advancement event, and at
least one solo-procedure-driven scene (an oracle consultation, a companion beat, or a journey
leg). Every roll traces to a real seeded `python3 random` draw, in the same discipline as every
prior section. The new section reports functional correctness and behavioral fidelity as two
distinct, separately-verdicted subsections, per #90's Definition of Done — the first section in
this document to carry that split explicitly at full-campaign scale. Any real behavioral gap
found is raised as its own follow-up issue, following specs/055/059's synthesis pattern, rather
than fixed inline.

## Technical Context

**Language/Version**: Python 3.11+ stdlib (`random`) for roll generation; the record itself is
Markdown.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m ruff format --check .`.

**Constraints**: Real seeded rolls throughout (FR-001). Functional correctness and behavioral
fidelity are reported as two distinct, separately-verdicted sections, never folded into one
(FR-004). Any real behavioral gap is raised as a follow-up issue rather than fixed inline
(FR-005). The scripted run must execute without crashing (FR-006).

**Scale/Scope**: One new section in `docs/design/30-playtest-transcript.md`, spanning several
scripted sessions for one character.

## Constitution Check

- **Nothing unpublishable** — continues using Senna Vask, the character already established in
  section 1; no new setting content or source-text quotation introduced. PASS.
- **No setting or system names** — none introduced; the arc exercises existing, already-named
  engine mechanics only. PASS.
- **Design documents rewritten in place** — the new section is appended to
  `docs/design/30-playtest-transcript.md`'s existing structure, matching every prior section's
  precedent (specs/046, specs/047, specs/053, and others). PASS.
- **No ADR in this feature** — nothing found requires a design decision; this is a worked
  playtest record composing existing, already-specified mechanics. PASS (per spec.md
  Assumptions). If the run surfaces a real behavioral gap needing a rule change, that becomes its
  own follow-up feature/ADR, not folded into this one.
- **Deterministic over inference** — every claimed roll traces to an actual seeded draw in a
  stated fixed order; functional correctness is checked against what the engine actually returned
  for each step, not asserted from memory of the design prose. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/144-full-campaign-simulated-playtest/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new section 19
```

## Complexity Tracking

*(empty — no constitution violations)*
