# Contract: the three `SKILL.md` files (part 2, `wyrd-chronicle-template`)

Each lives at `.claude/skills/<name>/SKILL.md`, invocable as `/<name>` in Claude Code, per
docs/adr/0013 (a Claude Code skill, not a game-mechanic definition — the engine's own
vocabulary, Rally/Downtime/Undertaking/advance, is what the prose names, never a slash-command
concept the engine itself knows about).

## `/wyrd-character`

**Reads**: `pc.yaml` via `wyrd character-load`/`wyrd session-context`.

**Player choices gathered**: whether to spend an unspent advance, and if so, on which skill or
career change (`spend`, `skill`, `target` — `spend-advance`'s own parameters).

**Code calls**: `wyrd character-load`, `wyrd spend-advance` (only when the player chooses to
spend).

**Never**: computes an advance's effect itself, or invents a refusal message not already
returned by `spend-advance`.

## `/wyrd-downtime`

**Reads**: `pc.yaml` (`standing`, `coin`, `stamina_max`, `wounds`).

**Player choices gathered, in order**: Destination (home or away — governs whether Upkeep asks
for a trade at all); the Upkeep trade (Standing vs coin) when away from home; which one of the
six Undertakings (Recover, Mend, Pursue, Cultivate, Learn, Ask); if Mend, which wound by name/id.

**Code calls**: `wyrd downtime --action upkeep` (skipped entirely when Destination is home);
`wyrd downtime --action mend` (only when Undertaking is Mend); `wyrd downtime --action rest`
(always, unconditionally, per FR-005); `wyrd character-save` to persist the resulting sheet.

**Never**: computes an Upkeep trade's Standing/coin delta itself, steps a wound's effect itself,
or invents a numeric payoff for Recover/Pursue/Cultivate/Learn/Ask (research.md: out of scope —
these five are recorded as the chosen Undertaking and otherwise played in prose).

## `/wyrd-end-session`

**Reads/writes**: `chronicle.yaml`, `recap.md`.

**Player choices gathered**: none beyond confirming the session is ending; if the last beat is
unresolved, the skill asks nothing — it always writes the `pending:` marker per
docs/design/16-session.md rather than asking the player to decide.

**Code calls**: `wyrd save` (persist current state first), `wyrd recap` (regenerate `recap.md`
from the now-persisted state), then a plain `git add`/`git commit` (not a `wyrd` verb — see
research.md).

**Never**: writes `recap.md`'s text itself instead of using `recap`'s returned text verbatim, or
commits before `save` has run.
