# Tasks: Ancestry widens creation's skill pool, never its budget

**Input**: Design documents from `/specs/038-ancestry-skill-widening/`
**Prerequisites**: plan.md, spec.md

## Task List

- [ ] **T001** Write ADR 0040 recording the decision and its two rejected alternatives (satisfies
      FR-005).
- [ ] **T002** Add a subsection to `docs/design/05-character-creation.md` §3 stating that an
      optional, setting-declared ancestry widens the eligible skill pool to the union of the
      career's and ancestry's lists, grants no additional advances, and carries no stat/Stamina/
      Luck modifier (satisfies FR-001, FR-002, FR-003, FR-004, FR-006).
- [ ] **T003** Run `python3 tools/check_docs.py` to confirm the new ADR is indexed and reachability/
      link policy holds (SC-002).
- [ ] **T004** Run `python3 tools/check_dangling_mechanics.py` and confirm no new dangling
      reference was introduced (SC-003).
- [ ] **T005** Re-read the worked examples in `05-character-creation.md` §3 and confirm none
      implies a larger or ancestry-dependent advance count (SC-004).

No code, schema, or test-suite changes are in scope — career/skill data lives in `wyrd-setting-*`
repositories, not this one.
