# Tasks: Two-layer companions and a positive party track

**Input**: Design documents from `/specs/027-two-layer-companions/`
**Prerequisites**: plan.md, research.md, data-model.md, quickstart.md (all present)

Single-threaded, ordered — each task depends on the ones before it landing in the same document.

- [x] **T001** Write `tools/check_companion_layers.py`: assert the mechanical-layer field set
  named in `docs/design/16-session.md` equals the fixed list `data-model.md` records (`career`,
  `bond`, `taint`, `strain`, `wounds`), no more and no fewer; assert no field appears on both the
  narrative-layer and mechanical-layer lists; assert `docs/design/03-rules.md`'s companion/succession
  passage names no mechanical field absent from that same list; compute and print the
  party-size-bound arithmetic from `data-model.md` (5 companions × 5 fields = 25 tracked values)
  rather than asserting the round number by eye (`CLAUDE.md`, "check the maths").
- [x] **T002** Amend `docs/design/16-session.md`'s companion section:
  - Introduce the narrative layer / mechanical layer split explicitly, naming both lists.
  - State the mechanical layer is closed (five fields) and why (`research.md`).
  - Complete Bond's positive effect: the Tension-offset rule from `data-model.md` (±1 point of
    Tension per point of Bond, floored at 0 added), replacing the current narrative-only
    description of what Bond does with the concrete mechanical rule plus its worked cases.
  - Confirm the "no second track" framing in prose — Bond is stated as the party's one
    positive-and-negative-modifying value, not a companion to Tension.
- [x] **T003** Amend `docs/design/03-rules.md`'s companion-and-succession passage: add the one-line
  cross-reference to the two-layer terminology now defined in `docs/design/16-session.md`, and confirm
  (rewording only if needed) that "one competence gained or limitation lost" and "inherits none of
  the competence" both read correctly against the mechanical layer.
- [x] **T004** Write `docs/adr/0034-bond-is-the-positive-party-track.md`: records the rejected
  standalone-Cohesion-track alternative and the reasoning in `research.md`, dated 2026-08-26,
  never edited after acceptance per `CLAUDE.md`'s ADR rule.
- [x] **T005** Run verification: `python3 tools/check_companion_layers.py`; grep `design/` for
  setting/system vocabulary; `python3 tools/check_docs.py` for reachability (confirms the new ADR
  is indexed and both amended documents stay reachable).
- [x] **T006** `ruff check . && ruff format --check .` and `python3 -m pytest -q` (repo-wide gate
  before PR).
