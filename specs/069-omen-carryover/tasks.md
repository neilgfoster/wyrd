# Tasks: Omen carryover across a proposed batch

- [X] **T001** Specify where the pending modifier lives — a persistent `pending_omen` field, not
      batch-local, since the rule's own "lapses unused" language implies cross-proposal
      persistence (FR-003).
- [X] **T002** Add `pending_omen` to `22-state.md`'s player-character frontmatter — a real gap,
      since nothing prior to this feature needed it.
- [X] **T003** Specify `propose` reading `pending_omen` at batch start and applying it to that
      actor's first roll, without consuming it until commit (FR-001, FR-004).
- [X] **T004** Specify within-batch carryover to a later step of the same actor, and
      non-stacking/replacement on a further Omen before the pending one is spent (FR-001, FR-002).
- [X] **T005** Specify Omen-consumption as a `depends_on` edge, reusing #194/#195's mechanism
      (FR-005).
- [X] **T006** Confirm rerolling an Omen-producing step correctly propagates via the existing
      downstream-set mechanism, with no new reroll logic (FR-006).
- [X] **T007** Work through a real seeded example: a two-roll batch with Omen carryover, then a
      reroll of the producing step, showing the consuming step's result genuinely change.
- [X] **T008** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
