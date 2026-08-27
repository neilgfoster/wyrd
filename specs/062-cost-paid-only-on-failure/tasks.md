# Tasks: Systems-of-power costs paid only on a failed invocation

- [X] **T001** Confirm no other engine mechanic is win-or-lose (grep the design corpus for
      "regardless of outcome" / "win-or-lose") and that Strain's own generic definition
      (`03-rules.md` §5) is already failure-driven (FR-004).
- [X] **T002** Write ADR 0048, recording the decision and the rejected alternatives (keep
      win-or-lose; split Strain/Resolve timing) (FR-004).
- [X] **T003** Rewrite `09-systems-of-power.md`'s Resolution paragraph, Trauma-threshold
      paragraph, "no new resolution path" line, and both worked examples for failure-only cost
      (FR-001, FR-002, FR-003) — also fixing a pre-existing "Strain drops" wording bug found
      while editing the same sentence.
- [X] **T004** Add the ADR 0048 index entry to `docs/README.md`.
- [X] **T005** Rewrite `check_spam_brake.py`: failure-only accrual, re-verified spam/ordinary/
      rotation-immunity properties, a new `resolve_cost`-timing check, and a direct
      win-or-lose-vs-failure-only comparison on the exact sequences already on record (FR-005).
- [X] **T006** Replay the major-tier (seed `20260842`) and minor-tier (seed `20260850`) spam
      sequences under the corrected timing, including the Affliction sawtooth (FR-006).
- [X] **T007** Replay the "ordinary use" worked example's own three rolls under the corrected
      timing (FR-006).
- [X] **T008** Replay the Resolve-recurrence check (seed `20260841`, continued honestly to an
      actual failure) under the corrected timing (FR-006).
- [X] **T009** Write §17 in `docs/design/30-playtest-transcript.md`, without editing any prior
      section (FR-006).
- [X] **T010** Run `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`
      (fixing one genuinely new false positive by rewording, twice, until it resolved), and
      `python3 -m pytest -q`; confirm clean.
