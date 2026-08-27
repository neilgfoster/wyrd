# Tasks: Brake on spamming a failing system-of-power invocation

- [X] **T001** Get operator direction on the brake's shape (asked; redirected to tying repeated
      failure to Taint/Trauma) (FR-006).
- [X] **T002** Decide Trauma over Taint (Taint already has a dedicated systems-of-power channel;
      Strain/Trauma are the engine's paired mental-harm tiers) and write ADR 0045, including the
      rejected Strain-cap and escalating-cost alternatives (FR-006).
- [X] **T003** Add the Trauma-gain bullet to `03-rules.md` §5 (FR-001, FR-002).
- [X] **T004** Add the cost-section paragraph to `09-systems-of-power.md`, cross-referencing §5
      (FR-003).
- [X] **T005** Write `check_spam_brake.py`: replay a comparable spam sequence to #151's playtest,
      confirm real Trauma accrues (crossing the Affliction threshold) under the new rule where the
      published rule accrued none (FR-004); confirm ordinary play (isolated failure among
      successes) costs zero (FR-005).
- [X] **T006** Add the ADR 0045 index entry to `docs/README.md`.
- [X] **T007** Add a resolution note to §10 of `docs/design/30-playtest-transcript.md`, and update
      §13's synthesis table's #163 row and closing sentence to reflect the fix.
- [X] **T008** Run `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
      `python3 -m pytest -q`; confirm clean.
