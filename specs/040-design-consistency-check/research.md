# Cross-reading pass — findings log

Per spec.md FR-001/FR-002/SC-006: every pair read is recorded here regardless of outcome. A clean
pass is a finding, not silence.

## Pairs read

### `docs/design/03-rules.md` §2 (Combat) vs `docs/design/12-the-adversary.md`

Both describe combat mechanics from two angles: the ruleset states the procedure, the adversary
document states what an opponent carries and which rule reads each field. Checked line-by-line for
every figure restated on both sides:

- **The opponent never rolls** — stated identically in both (`03-rules.md`: "the opponent never
  rolls, its capability is a static number"; `12-the-adversary.md`: same, citing the same ADR
  0027).
- **The critical formula** — `1d6 + points below zero`, stated identically in both, against the
  same table reference (`05-criticals.md`).
- **The crowd-clearing threshold** — "ahead by 20 or more" in `03-rules.md`'s table; the same "20
  or more" cited in `12-the-adversary.md` §3's baseline discussion. Identical.
- **Aftermath's scope** — `03-rules.md` says Aftermath is rolled once per combatant who dropped,
  companions included; `12-the-adversary.md` §4 says Aftermath does not apply to an adversary
  (only a character or companion), citing the same rule. Consistent — the adversary document is
  stating the negative case of the same rule, not a different one.
- **Armour ranks** — `03-rules.md`: light `1d3`, modest `1d6`, heavy `2d6`; `12-the-adversary.md`'s
  block table names the same four ranks (`none`/`light`/`modest`/`heavy`) without restating the
  dice, deferring correctly to `03-rules.md` as the single source. No restatement to diverge.

**Finding: no divergence.**

### `docs/design/07-transformations.md` vs ADR 0029

Both describe the Taint-threshold spacing that forces a Transformation roll.

- **Threshold spacing** — `07-transformations.md`: "A Taint threshold sits at every multiple of 3,
  starting at 3: 3, 6, 9, 12, and so on." ADR 0029's title and Decision: "Taint thresholds sit at
  every 3 points." Identical.
- **What a threshold forces** — `07-transformations.md`: "A Taint threshold always forces a
  Transformation. It never forces an Affliction," explicitly resolving a collision with
  `03-rules.md` §4's older wording. ADR 0029's own Decision states the same resolution.

**Finding: no divergence.**

### `docs/design/03-rules.md` §2 (Stamina recovery) vs `docs/design/06-aftermath.md`

Both touch Stamina recovery: the ruleset states the recovery rule, Aftermath's own doc points back
to it rather than restating it independently.

- `06-aftermath.md`: "Stamina recovery... is `03-rules.md` §2's: a combatant who dropped wakes at
  0 and recovers 1 at each Rally, or to maximum at a downtime." This is a deferral with an
  accurate one-line restatement, not an independent claim that could drift silently — and the
  restatement itself matches `03-rules.md`'s own wording exactly ("recover 1 Stamina" at each
  Rally, "Stamina returns to maximum" at downtime, wakes at 0).

**Finding: no divergence** (correct deferral shape, restatement accurate).

## Scope note

This is not an exhaustive pairwise read of all 30 x 29 document combinations — that would not
distinguish signal from the very large number of pairs that legitimately never restate the same
fact (e.g. `26-corpus-index.md` and `08-afflictions.md` share no claim to diverge on). The pairs
above are the ones `docs/design/`'s own cross-references identify as describing one mechanic from
two angles — the shape CLAUDE.md's recurring-fault list names as the hardest to catch, and
precisely the shape a future reader would need to re-check if this stage's own reasoning were
forgotten.
