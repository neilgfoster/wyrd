# Tasks: The base propose/commit mechanism — staged rolls and mutations

- [X] **T001** Decide whether this earns an ADR (a real rejected alternative — "commit
      immediately" — exists); write ADR 0050 (FR-004, FR-005, FR-006).
- [X] **T002** Specify `propose`'s request shape (actor, mechanic, skill, target, difficulty,
      already-decided declaration bonus) — no roll, effective%, or mutation supplied by the
      caller (FR-001, FR-002).
- [X] **T003** Specify `propose`'s response shape (roll data + staged mutations + id) (FR-003).
- [X] **T004** Specify `commit`/`discard` behaviour, including the invalid-id error case
      (FR-005, FR-006, FR-007).
- [X] **T005** State cascading resolution, partial reroll, and Omen carryover as explicitly out
      of scope (FR-008).
- [X] **T006** Work through a real seeded example (an Exposure test, propose then commit),
      showing state unchanged before commit and correctly mutated after.
- [X] **T007** Write `docs/design/31-action-resolution.md`, link it from `README.md`.
- [X] **T008** Update `docs/design/02-architecture.md`'s CLI sketch and Memory-tiers
      cross-reference; flag `damage`/`track` as a known follow-up rather than leaving them
      silently inconsistent with the new mechanism.
- [X] **T009** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
