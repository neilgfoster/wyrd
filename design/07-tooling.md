# Wyrd — tooling principles

Engineering ground rules for everything under `engine/` and the `wyrd` CLI.

---

## 1. Deterministic over inference

**If a script can do it, a script does it.** The model is reserved for the things models are
actually good at.

This is not only about cost. Anything computed by inference can drift, and over a chronicle
running years, drift is indistinguishable from cheating. A rule the model *remembers* is a
rule that quietly erodes. A rule in `engine/rules/` is a rule.

### The decision procedure

Ask, in order:

1. **Does it have a single correct answer given the state?** → script.
2. **Could the player catch the GM getting it wrong?** → script.
3. **Does it need to hold across years and context resets?** → script.
4. **Is it arithmetic, lookup, validation, or bookkeeping?** → script.
5. Only if none of the above → model.

### Where the line falls

| Script — no model involved | Model |
|---|---|
| Dice rolls, and reading the Wyrd die | What the result *means* here |
| Damage, armour dice, stamina, criticals | Describing the wound |
| Taint, Trauma, Strain, Resolve arithmetic | How the taint surfaces in this scene |
| Threshold and invariant checks | Whether to call for a roll at all |
| The secret hidden threshold | — |
| Threat activation (`d100 <= imminence × 10`) | How the Threat manifests here, now |
| Elapsed-time expected-value events | What the peddler says about them |
| Thread heat decay | Which thread is worth pulling on |
| Advance eligibility against career triggers | Character voice, motive and choice |
| Calendar, lunar cycles, festivals | Scenario adaptation and pacing |
| Save read/write, schema validation, commit | Party tension events and their shape |
| Aftermath / critical / transformation table lookups | Companion behaviour |
| Reputation test, recognition roll | The consequence of being recognised |

**The dice roller in particular is non-negotiable.** It is the only defence against
principle 1 in [`01-principles.md`](01-principles.md) eroding quietly.

### The model must not recompute

When the CLI returns a result, the GM **narrates from it** and never recalculates it.
If `wyrd roll` says failure, the model does not re-add the dice. If the tool and the prose
disagree, the tool is right and the prose is a bug.

### Checked claims about the repository itself

The same principle applies to the design programme's own process, not only to play-time rules.
Three scripts under `tools/` check a claim about the documents rather than asserting it:
`backlog.py check` (the board's priority order is whole), `check_docs.py` (the document graph
is reachable, linked and indexed), and `check_dangling_mechanics.py` (every mechanic named
somewhere in `design/` is defined somewhere in `design/` — the fault that named at least six
mechanics as authoritative before anything defined them).

All three run **on demand, not in CI** — this repository has no CI workflow at all yet, so
wiring one in for a single check would be a new commitment on its own, not a natural extension
of an existing gate. Run them before a PR that touches `design/`, the same discipline
`tools/check_docs.py`'s own usage note already asks for.

---

## 2. Python, stdlib only

**Stdlib-only, zero-dependency, zero-backend.** No packages, no server process, no install step, no supply-chain surface.

- Python 3.11+, standard library only
- No daemon process, no database — the chronicle is files on disk
- Readable top to bottom; a person can audit the whole thing
- The constraint is the differentiator: portable, auditable, and it will still run in five
  years, which matters for something meant to last a decade

State is YAML with `[[wikilink]]` frontmatter, parsed by a **small internal reader** for the
restricted subset Wyrd uses. Hand-editability matters more than parser generality: at three
years deep you will want to fix a file by hand. **No third-party YAML dependency.**

---

## 3. MCP-shaped structure

Scripts are consumed by an AI, so they are structured the way an AI expects tools to be
structured — even though there is no MCP server.

### A single tool catalog drives everything

```
engine/wyrd/
├─ catalog.py     # TOOLS — the single source of truth. Pure data.
├─ client.py      # entry point; argparse dispatch built FROM the catalog
├─ verbs.py       # the operations
├─ rules.py       # resolution, damage, tracks, thresholds — pure functions
├─ tables.py      # criticals, aftermath, transformations, afflictions, oracles — pure data
├─ state.py       # load/save/validate, atomic writes, invariants
├─ calendar.py    # dates, lunar cycles, elapsed time
├─ campaign.py    # threats, threads, activation, decay
└─ render.py      # output formatting (json | text)
```

What `tables.py` loads and how a result is looked up is defined in
[`03a-tables.md`](03a-tables.md).

`TOOLS` drives **both** `describe` and the argparse dispatch, so discovery and execution can
never drift. Each entry carries:

- `name`
- `description` — onboarding-quality, including **when to use it**
- `annotations` — MCP advisory hints: `readOnlyHint`, `destructiveHint`, `idempotentHint`,
  `openWorldHint`
- `inputSchema` — **flat** JSON Schema; no `oneOf` / `allOf` / `anyOf`

### `describe` is the discovery verb

```bash
python3 -m wyrd.client describe            # whole catalog as JSON
python3 -m wyrd.client describe --name roll
```

The zero-backend equivalent of MCP `tools/list`. **The runtime catalog is the source of
truth** — skills reference verbs by name and read their schemas at runtime rather than
hardcoding usage that can rot.

### Structured output by default

Every verb emits JSON on stdout with a stable shape; `--format text` is for humans. A roll
returns the whole structured result, not a sentence:

```json
{
  "verb": "roll",
  "skill": "stealth",
  "skill_pct": 45,
  "difficulty": -10,
  "effective_pct": 35,
  "roll": 23,
  "units": 3,
  "success": true,
  "degrees": 1,
  "wyrd": "none",
  "ill_omen_range": [0],
  "natural_roll": 23,
  "state_written": true
}
```

The GM narrates from that object. It does not need to know how any of it was derived.

`skill` carries whatever the **setting** calls that skill — the engine has no skill vocabulary of
its own and echoes back the identifier it was given
([ADR 0013](adr/0013-the-engine-names-no-skill.md)). The value above is one setting's word, not an
engine skill.

### Modular and extensible

- `rules.py` and `tables.py` are **pure** — no I/O, no state, trivially testable
- Settings supply data, never code: a setting's weapon table is a data file, not a new module
- Adding a verb means adding a catalog entry and a function; nothing else changes
- Errors are structured (`{"error": {...}}`) and actionable, never bare tracebacks

---

## 4. How settings adjust the tooling

A setting may extend, retune, rename or disable what the engine provides, and may never add a
mechanism ([`13-authoring-a-setting.md`](13-authoring-a-setting.md)). The tooling has to
honour that **without settings ever shipping code.**

### Declarative only

There is no plugin system, no hook registry, no setting-supplied Python. A setting provides
**data and declarations**; the engine decides what they mean. This is what keeps the engine
auditable and what makes "a setting cannot add a mechanism" enforceable rather than merely
requested.

### The engine declares what is overridable

Overridability is a **closed set published by the engine**, not whatever a setting happens to
name. `describe` reports it, the same way it reports verbs:

```bash
python3 -m wyrd.client describe --overridable
```

An override naming something outside that set is a **load error**, not a warning. Otherwise a
setting could quietly disable an invariant.

### Load order

```
engine defaults  →  setting overrides  →  chronicle houserules
```

Last wins, and each layer may only narrow what the previous allowed. The resolved
configuration is written into the chronicle at bootstrap and versioned with everything else
([`06-state.md`](06-state.md)), so a chronicle never depends on re-resolving it later.

### The four kinds, and what each costs

| Kind | Mechanism | Cost to the tooling |
|---|---|---|
| **Extend** | a data file appended to a list — careers, gear, creatures | none; these were always data |
| **Retune** | a table path replaced | none; tables are loaded by name |
| **Rename** | a presentation-layer lookup | **none in code — see below** |
| **Disable** | a mechanism switched off | verbs and checks must react |

### Renames are presentation-only

**Internal identifiers never change.** If a setting renames Taint to Shadow, the state field
is still `taint`, the verb is still `wyrd track <id> taint +1`, and the migration that
touches it still names `taint`.

Only *rendered output* uses the setting's word. This is not a detail — it is what allows
migrations, golden chronicles, doctor checks and cross-setting tooling to be written once. A
rename that reached the state would fork the engine per setting.

### Disabling is first-class

A disabled mechanism must not merely be hidden:

- its verbs are **absent from `describe`**, so the model never offers them
- calling one anyway is a structured error, not a silent no-op
- `wyrd doctor` does not flag its fields as missing
- rules that depend on it are skipped, and rules that *require* it make the setting invalid
  at load — declaring `disable: [taint]` while retaining a table that fires on a Taint
  threshold is a contradiction the engine should refuse

That last check is why the overridable set is closed: the engine knows the dependency graph
between its own mechanisms, and a setting does not.

### `describe` reflects the active setting

Because the `TOOLS` catalog drives dispatch, filtering it by the resolved configuration means
the model **only ever sees verbs that apply here**. A setting without Taint has no
`track taint`, so the GM cannot reach for it by accident — the same discipline as the closed
overridable set, applied to the model's own view.

### Validation and versioning

Setting overrides are validated at load and carry a version like any other content. A change
to them is a **structural** change for chronicles that pinned the old version
([`09-evolution.md`](09-evolution.md)) — the representation moves, the history does not.

---

## 5. Model tiering

Use the smallest model that can do the job correctly.

| Tier | Used for |
|---|---|
| **No model** | Anything in the left column of §1. Dice, arithmetic, state, activation, validation, table lookups. |
| **Haiku** | Mechanical language work with a right answer: extracting entity updates from a session log, regenerating `recap.md` from state, matching arc hooks against live threads, picking names from setting tables, formatting a roll into a sentence. |
| **Sonnet / Opus** | The GM itself. Narration, character voice and motive, arc adaptation, party tension events, judgement about what a result means and when to call for a roll. |

Mechanical steps are delegated to a **Haiku subagent** — an agent definition in
`.claude/agents/` with `model: haiku` frontmatter — rather than being done inline by the
session model. Session-close compaction is the clearest case: it is bulk structured
extraction against files that already exist, it has a right answer, and it does not need
the GM's context.

The GM session itself stays on the capable model. Wyrd's whole value is the quality of the
fiction; that is the one place not to economise.

### Rule of thumb

> If you can write the acceptance test, it does not need a large model.
> If you cannot, it does not need a small one.

---

## 6. Testing

- `rules.py` and `tables.py` are pure — unit tests, no fixtures
- Dice distributions are asserted statistically, with the expected values stated in the
  tests themselves rather than referenced elsewhere
- State invariants from [`06-state.md`](06-state.md) are enforced on **every** write and
  tested directly
- Golden chronicles: a saved state plus a scripted sequence of verbs, asserting the
  resulting state — this is what catches rule drift across refactors
- `stdlib unittest`. No pytest.
