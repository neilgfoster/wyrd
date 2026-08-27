# Tasks: Specify the attack → damage → armour → critical chain through propose/commit

- [X] **T001** Decide whether this generalises #194's own mechanism or needs distinct treatment;
      resolve to generalising, since both shapes stage identically (FR-001).
- [X] **T002** Restate "Cascading resolution"'s opening paragraph to name both trigger shapes
      explicitly (FR-001).
- [X] **T003** Specify the combat chain's step mapping: landing → damage/armour (dependent,
      parallel) → combined Stamina mutation → threshold-crossing → critical (FR-002, FR-004).
- [X] **T004** Specify telling blow as read from the landing step's own `degrees`/virtual-roll
      degrees, not a separate roll (FR-003).
- [X] **T005** Work through a real worked example, reusing §7/§14's already-verified rolls, and
      confirm the resulting mutations match those sections' own figures exactly.
- [X] **T006** Update `02-architecture.md`'s CLI sketch: remove `wyrd damage`, update the
      known-follow-up note to the still-outstanding generic-tracker case only (FR-005).
- [X] **T007** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
