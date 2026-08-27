# Tasks: Reconcile write invariants and state the transaction lifecycle

- [X] **T001** Restate "persist precedes narrate" to distinguish narrating a proposal from
      narrating a settled result (FR-001).
- [X] **T002** Split the Invariants list into passive validation and active triggers, matching
      what `31-action-resolution.md`'s Cascading resolution section already states for each
      (FR-002).
- [X] **T003** Correct the Spent formula to ADR 0049's dual threshold (FR-003).
- [X] **T004** Read `chronicle.yaml`'s existing `pending.rolled` field and state the transaction
      lifecycle by reusing it (FR-004).
- [X] **T005** Cross-reference `pending.rolled`'s own section to point at the new transaction
      lifecycle statement.
- [X] **T006** Add `wyrd reroll` to `02-architecture.md`'s CLI sketch (FR-005).
- [X] **T007** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
