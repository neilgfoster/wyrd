# Tasks: The dependency-graph partial-reroll mechanism

- [X] **T001** Specify `reroll`'s request shape (proposal id, target step, resource) (FR-001).
- [X] **T002** Specify the downstream-set computation from `depends_on` and the discard/preserve
      split (FR-002, FR-003).
- [X] **T003** Specify re-resolution under the resource's own modifier (FR-004).
- [X] **T004** Specify the resource's own cost as a staged mutation (FR-005).
- [X] **T005** Specify that a freshly-resolved step is checked against cascading resolution again
      (FR-006).
- [X] **T006** Specify that `reroll` does not invalidate the proposal id (FR-007).
- [X] **T007** Work through a real seeded example (two independent Exposure tests, one rerolled
      via the Bargain), including an honest still-fails outcome — reword any Title-Case labels
      that trip the dangling-mechanics checker unnecessarily.
- [X] **T008** Note the attack→damage outcome-conditional-chain gap surfaced while working the
      example, without resolving it in this feature.
- [X] **T009** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
