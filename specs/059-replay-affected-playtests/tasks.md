# Tasks: Re-play playtest scenarios affected by rule changes made during the playtest epic

- [X] **T001** Identify which of §6-§12 exercised a mechanic later changed by ADR 0043/0044/0045
      (§7, §8, §10) versus one that only changed on paper (ADR 0046, §12 — no replay needed)
      versus untouched (§6, §9, §11).
- [X] **T002** Re-derive §7's three defence rolls against ADR 0044's virtual-roll formula;
      identify the now-telling blow and its consequence (FR-001).
- [X] **T003** Recompute §7's critical and Aftermath rolls by reusing the original die values
      under their new modifiers, confirming the resulting band for each (FR-002).
- [X] **T004** Replay §8's Resolve exercise with fresh seeded rolls under ADR 0043, including the
      single-Rally edge case shown honestly rather than skipped (FR-003).
- [X] **T005** Replay §10's Resolve recurrence and spam sequence with fresh seeded rolls under
      ADR 0043/0045, against Kester's own character (FR-004).
- [X] **T006** Write §14 in `docs/design/30-playtest-transcript.md`, cross-referencing §7/§8/§10
      without editing their original text (FR-005).
- [X] **T007** Confirm no new design decision was made in the process (FR-006).
- [X] **T008** Run `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
      `python3 -m pytest -q`; confirm clean (fixing one genuinely new false-positive along the
      way, a Title-Case-looking sentence opener, by rewording).
