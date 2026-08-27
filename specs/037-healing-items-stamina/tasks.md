# Tasks: Healing items have no mechanical effect on Stamina

**Input**: Design documents from `/specs/037-healing-items-stamina/`
**Prerequisites**: plan.md, spec.md

## Task List

- [ ] **T001** Add an explicit "healing items have no mechanical effect on Stamina" paragraph to
      the Stamina recovery section of `docs/design/03-rules.md`, grounded in ADR 0020's "no new
      cadence" reasoning (satisfies FR-001, FR-002, FR-003, FR-004).
- [ ] **T002** Run `python3 tools/check_docs.py` to confirm reachability/link policy still holds
      (SC-002).
- [ ] **T003** Grep the new paragraph for any invented mechanic name and confirm none was
      introduced, so nothing dangles for the project's dangling-mechanic check (SC-002, FR-004).

No code, schema, or test-suite changes are in scope — this is a documentation-only feature per the
issue's Definition of Done and the plan's Constitution Check.
