# Research: Oracle prompt tables

## Decision: four prompt families, chosen to match where invention actually runs loose

**Rationale**: The issue names four candidates already present in the existing design: an NPC's
real objective, why a situation is not as presented, what a thread turns on, what complicates a
scene. Each corresponds to a place the design already has a structure that would otherwise be
filled by unconstrained LLM invention: `docs/design/16-session.md`'s companion objectives, a scene's
presented-vs-actual state, `docs/design/19-campaign.md`/`docs/design/18-arcs-and-beats.md`'s thread turns,
and ordinary scene complication. Four families is the minimum that covers all four named gaps
without inventing a fifth nothing in the design currently needs.

**Alternatives considered**: A larger table of "atmosphere" prompts (weather, NPC mannerisms,
location dressing) — rejected explicitly by the issue's scope ("not a large table of atmosphere")
and by `CLAUDE.md`'s low-fantasy-register guidance: flavour prompts don't constrain anything an LLM
GM would otherwise get wrong, they just add content, which is a different (and out-of-scope)
problem from the escalation risk this family exists to close.

## Decision: each family is a single table, keyed `oracle-prompt-<family>`

**Rationale**: `docs/design/04-tables.md`'s naming convention is `<family>-<variant>` where a family
holds several tables. Prompts are a variant of the existing `oracles` family (spec
Clarifications), so each prompt family gets its own key under that umbrella, e.g.
`oracle-prompt-npc-objective`, `oracle-prompt-situation-truth`, `oracle-prompt-thread-turn`,
`oracle-prompt-complication`, distinguishing them from the sibling `oracle-answer` key.

**Alternatives considered**: One combined table with a family selector column — rejected. It would
mean the roll to *pick* a family and the roll to *read a row within it* are conflated into one
die, which breaks `docs/design/04-tables.md`'s rule that a family declares its own die: the four
prompt families do not obviously want the same table size, and forcing them into one table would
either waste rows or crowd them.

## Decision: `1d100`, no modifier, reused from the resolution die — same choice as the answer table

**Rationale**: As with `docs/design/14-oracle-answers.md`, `docs/design/03-rules.md` §1 already commits
the ruleset to `d100`. A prompt table with, say, 12-20 rows fits comfortably within contiguous
`1d100` ranges without needing single-digit precision, and reusing the existing die avoids adding
a second die vocabulary purely for this family (`docs/design/04-tables.md`'s "declared by the family"
clause exists to let a family diverge when it needs to, not to invite divergence by default).

**Alternatives considered**: `1d20` or `1d12` per family, matching row count more tightly —
considered, but rejected in favor of `d100` uniformity: nothing about a prompt table's shape
(unlike criticals' modifier-driven table depth) needs a different die, and staying on `d100` keeps
this variant consistent with its `oracle-answer` sibling under the same family entry.

## Decision: genre-neutrality is checked by a recorded double reading, not a computed property

**Rationale**: The issue is explicit that this feature's verification is different in kind from
#20's: "checked by reading every row twice — once as if the setting were grim and once as if it
were comic — and deleting any row that only works in one of them." This is a qualitative judgment
call, not a number, so it cannot be asserted by a probability script the way
`tools/check_oracle_answers.py` computes odds. Instead, the document records the check per row
(e.g. a table column or an explicit statement that every row was read both ways with none
rejected), and `tools/check_oracle_prompts.py` checks the structural properties that *are*
computable: range contiguity, no duplicate/overlapping rows, and that the document's own recorded
check column has no row left unmarked.

**Alternatives considered**: Skipping automated verification entirely for this family, relying on
review alone — rejected by `CLAUDE.md`'s "where a claim can be checked by a script, check it": the
structural half of table correctness (contiguous ranges, an entry for every row) is exactly the
same computable claim every other family's script checks, even though the genre-neutrality claim
itself is not.

## Decision: a prompt roll is obligatory when the GM is about to invent one of the four gaps and no answer is already established

**Rationale**: Mirrors the answer-oracle's obligation shape (`docs/design/14-oracle-answers.md`),
adapted to prompts: the GM rolls instead of inventing whenever the fiction needs one of the four
scoped things (an NPC's real objective, why a situation isn't as presented, a thread's turn, a
scene's complication) and it hasn't already been established by an earlier roll, a companion's
stated Tension, or a thread's existing state. Once generated, the content is established fact the
same way an oracle answer is, and is never re-rolled to get a different answer to the same
question.

**Alternatives considered**: Making the roll optional/advisory — rejected for the same reason
`docs/design/14-oracle-answers.md` rejects it: an oracle nobody is obliged to consult constrains
nothing, because a GM under narrative pressure reaches for it only when the invented answer
already feels risky, which is exactly the case that needs it least.

## Decision: generated content maps onto existing structures rather than introducing new state

**Rationale**: An NPC-objective row's output becomes the value the companion/objective machinery
in `docs/design/16-session.md` already holds (it does not add a new field — it fills an existing one
that was previously the GM's private invention). A thread-turn row's output becomes a state
transition the thread/threat tracking in `docs/design/19-campaign.md` and `docs/design/18-arcs-and-beats.md`
already accepts. This keeps the family additive to existing content layers instead of duplicating
them with a parallel "generated content" store.

**Alternatives considered**: A dedicated `generated-prompts.log`, separate from where the content
actually lands — rejected for the same reason the answer oracle rejected a separate oracle log:
`CLAUDE.md` names "two lists of the same work drift" as a recurring fault, and it applies equally
to two records of the same NPC's objective.

## Decision: setting extension reuses the existing `extend:` override category, applied to tables

**Rationale**: `docs/design/24-authoring-a-setting.md` already names two distinct override shapes:
**extend** (add careers, talents, gear, creatures — additive, on top of the engine's own list) and
**retune** (replace a table wholesale, e.g. `overrides.tables:`). Prompt tables want the *extend*
shape, not the *retune* one, but `extend:` today only covers list-like content, not rollable
tables. This feature closes that gap the way `docs/design/24-authoring-a-setting.md`'s own "not
permitted: adding a subsystem the engine does not know about" rule requires — a setting needing a
mechanism the engine lacks is an engine gap, generalised in the engine so every table family gets
it, not a special case invented for prompts alone. Concretely: `extend:` gains the ability to name
a table key, whose rows are appended to the engine's own after the last engine row, keeping engine
ranges untouched and giving the setting's rows a contiguous range slice above them (the *additive*
kind of table change `docs/design/04-tables.md`'s own versioning section already names, as distinct
from *tuning*).

**Alternatives considered**: A prompt-specific extension mechanism, scoped to this family only —
rejected. `docs/design/24-authoring-a-setting.md`'s override set is closed and generalised on purpose;
a mechanism that only works for prompt tables would be exactly the kind of special case that rule
exists to prevent, and every other repeatable table family (afflictions, oracle answers) would
plausibly want the same additive path later.
- Requiring settings to fully replace a prompt table to add their own rows (today's only
  mechanism via `tables:`) — rejected, since it forces every setting wanting even one
  setting-specific NPC-objective row to also copy and maintain the entire engine baseline, which
  is exactly the maintenance burden the issue's framing (settings want prompts more than
  criticals) warns against.
