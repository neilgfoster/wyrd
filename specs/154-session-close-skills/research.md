# Research: Character, downtime and session-close skills

## Decision: repo split (two PRs, one issue)

**Decision**: Part 1 (CLI verb wiring) lands in `wyrd`; part 2 (the three `SKILL.md` files)
lands in `wyrd-chronicle-template`, as a separate PR.

**Rationale**: `wyrd-chronicle-template`'s own README states the repo is "self-contained after
bootstrap" and lists `/wyrd-play` next to the not-yet-built skills this feature adds — these are
chronicle-repo concerns, operating on chronicle-local files (`pc.yaml`, `party.yaml`,
`recap.md`) that do not exist in the engine repo. The engine repo, per this repo's own
`CLAUDE.md`, holds "engine, design, decision records" — not GM-facing skills.

**Alternatives considered**: Putting all three skills in `wyrd` and documenting that a chronicle
copies them in at bootstrap — rejected because nothing else in `wyrd` is copied into a chronicle
this way (the `bootstrap` script in `wyrd-chronicle-template` copies `engine/` and `setting/`,
never `.claude/`), and it would mean the engine repo carries prompt-level GM instructions
alongside its `docs/design/`, which the repo table explicitly scopes to "engine, design,
decision records."

## Decision: which parts of downtime.py/rally.py need new CLI verbs

**Decision**: Two new verbs — `downtime` (covering Upkeep, Mend and Rest, the three genuinely
mechanical downtime pieces) and `rally` (covering recovery, the pending-proposal discard, and
the optional advance award). `advance_downtime`'s own step-transition/exactly-one-undertaking
gate is **not** wired to a CLI verb in this feature.

**Rationale**: `engine/wyrd/downtime.py` and `rally.py` exist as pure functions with zero
`catalog.py`/`verbs.py`/`client.py` wiring today — confirmed by grep, and by `adjust-standing`'s
own catalog description explicitly excluding Upkeep ("outside Upkeep"), meaning no existing verb
covers it either. The issue's own DoD ("no skill reimplements arithmetic") makes wiring these
required, not optional, once the gap is found.

`advance_downtime`'s state-transition gate is designed for a downtime phase that persists across
multiple separate calls (its docstring: "moving to undertaking... raises if an undertaking has
already been chosen"). This feature's downtime skill runs Destination through Rest inside a
single invocation, so the "exactly one Undertaking" rule is naturally enforced by the skill's own
prose presenting that choice once — wiring the state machine itself would add a verb with no
call site inside this feature's scope. A future feature that makes downtime resumable
mid-phase (e.g. across a session boundary) would be the place to wire it.

**Alternatives considered**: Wiring `advance_downtime` too, for completeness — rejected as
speculative; nothing in this feature's user stories calls it, and the reuse-over-invention rule
in `CLAUDE.md` cuts against adding an unused code path.

## Decision: the five non-Mend Undertakings' mechanical effect is out of scope

**Decision**: Only Mend's effect (`apply_mend`'s ladder-stepping) is wired. Recover, Pursue,
Cultivate, Learn and Ask are presented as the choice only; this feature does not invent a
mechanical effect for the other five.

**Rationale**: `downtime.py`'s own module docstring states plainly: "Mend... is the one
undertaking this module implements in full." No other module in `engine/wyrd/` implements a
"reduce Taint by N" or "reduce Strain by N" function callable from Recover, or any function for
Pursue/Cultivate/Learn/Ask. Inventing one here would be new game-rule arithmetic with no ADR
behind it — exactly what `CLAUDE.md`'s "before proposing a rule change" section warns against,
and out of what the tracking issue asked for (it names Upkeep and "the Undertaking choice", not
each Undertaking's numeric payoff). docs/design/02-architecture.md's code/prose table entry for
"Downtime's Undertaking" ("the mechanical effect of whichever is chosen" is code) is read as
describing the target end state across all of downtime's future work, not a claim that every
undertaking's effect is coded today — `downtime.py` itself, the module the table's own row cites,
says otherwise for five of the six.

**Alternatives considered**: Deferring the whole Undertaking step until all six have coded
effects — rejected; it would block a real, working downtime skill on work several further
tracking issues would need to do (each of Recover/Pursue/Cultivate/Learn/Ask is its own
mechanical design question), when Mend and the Upkeep/Rest pieces already give the skill genuine
mechanical teeth today.

## Decision: Rally's "commit" step is a plain git commit, not a new CLI capability

**Decision**: The `rally` CLI verb wraps `apply_rally` with no `commit` callable (Python cannot
usefully receive one over a CLI boundary); the chronicle-repo skill calls the existing `save`
verb to persist state, then runs an ordinary `git add`/`git commit` as its own step, exactly as
`/wyrd-end-session` will for the session-close commit.

**Rationale**: `apply_rally`'s `commit` parameter exists to let a Python caller inject a
persistence callback; a CLI invocation has no such callback to pass across a process boundary.
Git committing is not engine arithmetic — it is an ordinary repository operation any Claude Code
skill can already perform directly, so wrapping it in a new verb would not remove any
reimplemented arithmetic, only add indirection.

## Decision: no automated tests exist for part 2 (the skills themselves)

**Decision**: Part 2's `quickstart.md` documents a manual walkthrough; no CI/test harness is
added to `wyrd-chronicle-template`.

**Rationale**: That repo has no CI and no test harness today (confirmed: no `.github/workflows`,
no `tests/`), and `SKILL.md` files are prompt-level instructions with no runtime to unit-test.
Part 1's new CLI verbs get ordinary `unittest` coverage in `wyrd`, same as every other verb.
