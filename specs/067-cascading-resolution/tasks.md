# Tasks: Cascading resolution for threshold-triggered sub-rolls

- [X] **T001** Specify the cascade trigger: a staged mutation checked against its track's own
      threshold rule, spawning the further step(s) that rule calls for (FR-001).
- [X] **T002** Specify `depends_on` recording for a cascade step (FR-002).
- [X] **T003** Specify recursion (a sub-roll's own mutation crossing a further threshold spawns
      another step) (FR-003).
- [X] **T004** State the termination reasoning, citing existing proofs (Transformation's
      hidden-threshold loop, the Affliction sawtooth) rather than re-deriving one (FR-004).
- [X] **T005** State the deferred-consequence exclusion (Aftermath is not staged immediately)
      (FR-005).
- [X] **T006** Write the worked example, reusing §8's already-published real rolls (Taint
      threshold crossing into a Transformation).
- [X] **T007** Update `31-action-resolution.md`'s own intro and forward-reference list to reflect
      cascading resolution now being specified.
- [X] **T008** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
