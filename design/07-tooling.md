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
| Dice rolls, and reading doubles / Wyrd die | What the result *means* here |
| Damage, armour dice, stamina, criticals | Describing the wound |
| Taint, Trauma, Strain, Resolve arithmetic | How the taint surfaces in this scene |
| Threshold and invariant checks | Whether to call for a roll at all |
| The secret hidden threshold | — |
| Threat activation (`d12 <= imminence`) | How the Threat manifests here, now |
| Elapsed-time expected-value events | What the peddler says about them |
| Thread heat decay | Which thread is worth pulling on |
| Advance eligibility against career triggers | NPC voice, motive, and choice |
| Calendar, the ill moon cycle, festivals | Scenario adaptation and pacing |
| Save read/write, schema validation, commit | Party tension events and their shape |
| Aftermath / critical / transformation table lookups | Companion behaviour |
| Reputation test, recognition roll | The consequence of being recognised |

**The dice roller in particular is non-negotiable.** It is the only defence against
principle 1 in [`01-principles.md`](01-principles.md) eroding quietly.

### The model must not recompute

When the CLI returns a result, Claude **narrates from it** and never recalculates it.
If `wyrd roll` says failure, the model does not re-add the dice. If the tool and the prose
disagree, the tool is right and the prose is a bug.

---

## 2. Python, stdlib only

Following the `msgraph-stdlib` house pattern: **stdlib-only, zero-dependency,
zero-backend.** No packages, no server process, no install step, no supply-chain surface.

- Python 3.11+, standard library only
- No otherworldly power, no database — the chronicle is files on disk
- Readable top to bottom; a person can audit the whole thing
- The constraint is the differentiator: portable, auditable, and it will still run in five
  years, which matters for something meant to last a decade

State is YAML-shaped but parsed with a small internal reader, or stored as JSON with a YAML
*view* for human editing — decided at implementation. **No third-party YAML dependency.**

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
├─ tables.py      # criticals, aftermath, transformations, oracles — pure data
├─ state.py       # load/save/validate, atomic writes, invariants
├─ calendar.py    # dates, the ill moon, elapsed time
├─ campaign.py    # threats, threads, activation, decay
└─ render.py      # output formatting (json | text)
```

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
  "skill": "stealth", "skill_value": 4, "diffisecty": 0,
  "dice": [5, 5, 2], "wyrd_die": 5, "total": 12,
  "target": 20, "modified_total": 16,
  "success": false,
  "doubles": true, "doubles_value": 5,
  "side_effect": "boon",
  "ill_omen_range": [1],
  "state_written": true
}
```

Claude narrates from that object. It does not need to know how any of it was derived.

### Modular and extensible

- `rules.py` and `tables.py` are **pure** — no I/O, no state, trivially testable
- Settings supply data, never code: a the science-fiction line weapon table is a data file, not a new module
- Adding a verb means adding a catalog entry and a function; nothing else changes
- Errors are structured (`{"error": {...}}`) and actionable, never bare tracebacks

---

## 4. Model tiering

Use the smallest model that can do the job correctly.

| Tier | Used for |
|---|---|
| **No model** | Anything in the left column of §1. Dice, arithmetic, state, activation, validation, table lookups. |
| **Haiku** | Mechanical language work with a right answer: extracting codex updates from a session log, regenerating `recap.md` from state, matching scenario hooks against live threads, picking names from setting tables, formatting a roll into a sentence. |
| **Sonnet / Opus** | The GM itself. Narration, NPC voice and motive, scenario adaptation, party tension events, judgment about what a result means and when to call for a roll. |

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

## 5. Testing

- `rules.py` and `tables.py` are pure — unit tests, no fixtures
- Dice distributions are asserted statistically (the tables in
  [`dice-design.md`](https://github.com/neilgfoster/wyrd-research/blob/main/reference/dice-design.md) are the expected values)
- State invariants from [`06-state.md`](06-state.md) are enforced on **every** write and
  tested directly
- Golden chronicles: a saved state plus a scripted sequence of verbs, asserting the
  resulting state — this is what catches rule drift across refactors
- `stdlib unittest`. No pytest.
