# Tasks: Combat Omens carry a ±10 modifier on the roller's next roll

- [X] **T001** Write ADR 0042 recording the decision, its precise scope (FR-002/003/004/005),
      and the rejected alternative (FR-007).
- [X] **T002** Add the ±10 Omen rule to `docs/design/03-rules.md` sec2, alongside the existing
      narrative framing (FR-001, FR-004, FR-005).
- [X] **T003** Write `check_omen_effect.py`, extending `check_conversion.py`'s Markov model with
      a pending-modifier state dimension, using probability buckets (not per-roll enumeration)
      for tractability (FR-006, SC-002).
- [X] **T004** Run the script; found and fixed a real parameter-mapping bug (every pairing
      produced an identical result — the tell that something was wrong) before recording any
      figure.
- [X] **T005** Confirm the corrected shift (max 0.029 damage/round) is below the stated 0.1
      materiality threshold; record the full table in ADR 0042 (SC-003).
- [X] **T006** Update `docs/README.md`'s ADR index.
- [X] **T007** Run `python3 tools/check_docs.py`, `check_dangling_mechanics.py`,
      `check_probability_coverage.py`, and `pytest -q`; confirm all clean (SC-004, SC-005).
