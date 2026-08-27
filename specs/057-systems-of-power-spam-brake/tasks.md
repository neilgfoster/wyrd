# Tasks: Brake on spamming a failing system-of-power invocation

- [X] **T001** Get operator direction on the brake's shape; redirected iteratively across three
      rounds: (a) tie to Taint/Trauma rather than an escalating cost or Strain cap; (b) resolved
      to Trauma; (c) first same-power-streak draft re-playtested and found defeated by two-power
      rotation (#172); (d) redirected to a Strain-threshold trigger keyed to an existing
      per-character stat, failure-only (FR-008).
- [X] **T002** Re-playtest the first (same-power-streak) design against a two-power rotation
      scenario with real seeded rolls; confirm it produces zero Trauma where single-power spam
      produces real Trauma — a genuine exploit, not a hypothetical (raised and tracked as #172).
- [X] **T003** Evaluate candidate thresholds: a flat engine-wide number (rejected — sits
      awkwardly against varying `strain_cost` scales) vs. an existing per-character stat; resolve
      to maximum Stamina, grounded in `03-rules.md`'s own "not meat... losing control of the
      fight" framing (FR-008).
- [X] **T004** Evaluate outcome-gating: any-outcome (no new logic needed, but taxes legitimate
      successful use) vs. failure-only (matches operator's stated intent); resolve to
      failure-only, verified by computed comparison on identical rolls (FR-002, FR-007).
- [X] **T005** Assess whether a setting could defeat the brake via `strain_cost: 0` (checked:
      already schema-rejected) or by disabling Strain/Trauma (checked: already permitted per
      `24-authoring-a-setting.md`, matching the existing Taint-disable precedent) — resolved to
      stating the degradation explicitly rather than inventing a fallback (FR-004).
- [X] **T006** Rewrite ADR 0045 (pre-merge, edited in place, not superseded) recording the full
      decision path, including the superseded first draft and all rejected alternatives (FR-008).
- [X] **T007** Rewrite `03-rules.md` §5's Trauma-gain bullet and `09-systems-of-power.md`'s cost
      section for the max-Stamina-threshold rule and the disabled-track note (FR-001–FR-004).
- [X] **T008** Rewrite `check_spam_brake.py`: verify the spam outcome across the realistic
      maximum-Stamina range (FR-005), rotation-immunity against the #172 exploit (FR-006), and
      failure-gating against a naive any-outcome variant on mostly-successful play (FR-007).
- [X] **T009** Update the ADR 0045 index entry in `docs/README.md` and the resolution note in
      `docs/design/30-playtest-transcript.md` §10.
- [X] **T010** Run `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
      `python3 -m pytest -q`; confirm clean.
