# Phase 0 Research: Career completion grants Stamina and a Mark

## R1 — When does the payout fire?

**Decision**: At the moment a spend carries the career from not-complete to complete — inside
`spend_advance`, on the same call that made the last granted skill reach the cap. Not on leaving
the career, and not on a separate claim.

**Rationale**: `docs/design/03-rules.md` §6 names the trigger as "completing a career", not
"leaving a completed career". Deferring to departure would mean a character who finishes a career
and stays in it for the rest of a chronicle is never toughened, which contradicts calling the
grant "the only durable toughening". It would also let a career change the character never makes
withhold a reward they have already earned.

**Alternatives considered**:

- *Pay on departure.* Simplest to bolt onto #277's existing `career_complete` call at departure,
  and wrong for the reason above. It also makes the reward contingent on spending a further
  advance, which the rules never price.
- *A separate `complete-career` verb the caller claims.* Rejected: it lets a caller assert a
  completion the engine never observed, which is precisely the "GM being generous by accident"
  the advance economy exists to prevent (§6).
- *Recompute the payout from the sheet whenever asked.* Rejected: `docs/design/29-evolution.md`
  forbids recomputing history, and a wound lowering a skill would retroactively unpay a
  completion.

## R2 — How is "per career-instance" represented?

**Decision**: One boolean on the character view — whether *this* occupancy of the current career
has already paid. It is set by the payout, cleared by a career change, and copied into the
career-history entry when the character leaves.

**Rationale**: An instance has no identity a character needs to carry beyond "has it paid yet".
The history already records one entry per departure, so past instances are already
distinguishable; only the live one needs a flag.

**Alternatives considered**:

- *Count entries in `career_history` matching the career.* Rejected: history records departures,
  so the live instance is by definition absent from it, and this would have to re-derive the
  answer from skills — the recompute R1 rules out.
- *An instance id or sequence number.* Rejected as unused weight: nothing in the engine addresses
  a past instance individually.
- *Count Marks naming the career.* Rejected for the same reason as the first alternative, plus it
  breaks the moment a Mark is granted at the ceiling with no Stamina beside it.

## R3 — The `completed` flag written into history at departure

**Decision**: Read it from the instance's paid flag, not by recomputing `career_complete` against
the character's live skills.

**Rationale**: This is a correction to #277, not a new choice. `completed_career_ids`'s own
docstring already states the intent — "Completion is read off the record written when a career was
left, never re-derived from the live skills: [...] a wound may have lowered one since" — but
`_spend_change_career` re-derives it at exactly that moment. A character wounded after finishing
Guard would have lost their eligibility for Guard-Captain. The flag makes the docstring true.

**Alternatives considered**: none worth recording; the existing behaviour is a defect against its
own stated rule.

## R4 — Does a career granting no skills complete?

**Decision**: No. `career_complete` returns `False` for a career with an empty grant list.

**Rationale**: `all()` over an empty mapping is vacuously `True`, which would make an empty career
instantly complete and pay a free Mark and Stamina point to any character who entered it. A career
that grants nothing is a setting-data fault; the engine declining to pay for it is the safe
reading, and it costs nothing for well-formed data.

**Alternatives considered**: raising a load error instead. Deferred — validating a setting's
career table belongs to the setting-loading work, not to the spend path, and `career_complete` is
called at play time where refusing to pay is the right failure.

## R5 — Does the payout raise *current* Stamina too?

**Decision**: No. Maximum Stamina rises by one; current is untouched.

**Rationale**: `docs/design/03-rules.md` §6 says "+1 maximum Stamina" and nothing about current.
Recovery (`docs/design/`'s Rally and downtime rules, #270) is what fills the vessel; a completion
widens it. Raising both would quietly make a completion a healing effect, which no document
describes.

**Alternatives considered**: raising current alongside max, on the grounds that a character at
full Stamina would otherwise be one short. Rejected — completion is not a recovery event, and the
next Rally closes the gap anyway.

## R6 — Where do the numbers come from?

**Decision**: The ceiling of 10 and the starting maximum of 6 are not derived here. The tests
import `tools/check_advancement.py` and assert the engine's constants equal the figures that
script computes, and reproduce its twelve-instance chronicle against the engine's own payout path.

**Rationale**: Two independent copies of a computed figure is exactly how a repo ends up with a
design document and a script that disagree. Asserting agreement makes a future change to the
script fail these tests rather than pass silently.

**Alternatives considered**: hard-coding 6 and 10 with a comment citing the script. Rejected — a
comment is not a check.
