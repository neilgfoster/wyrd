# Data Model: Haiku corpus fact-finder subagent for create-setting

This feature has no persistent state or database entities — it is a skill/agent-definition change.
The "data model" here is the shape of the two Markdown artefacts and the interface between them.

## Entity: Haiku corpus fact-finder subagent definition

**Location**: `wyrd-setting-template/.claude/agents/corpus-fact-finder.md`

**Frontmatter fields**:

| Field | Value | Notes |
|---|---|---|
| `name` | `corpus-fact-finder` | Invocation identifier |
| `description` | One sentence stating the closed retrieval task and when to use it | Following `code-explorer.md`'s style |
| `tools` | `Read, Grep, Glob` | Retrieval only — no `Write`/`Edit`/`Bash`/web tools, per research.md |
| `model` | `haiku` | The tier this feature exists to prove out |

**Body (system prompt) contents**:

- States its one job: given a claim and a corpus location, find and report the exact
  supporting/contradicting quote and its source location, or report not-found.
- States the three possible outcomes explicitly (support / contradict / not-found), each with its
  required output shape (quote text, exact file path, line number or nearest identifiable
  location).
- States what it must never do: invent, paraphrase, or approximate a quote; write setting content;
  make a judgement call about whether a claim is acceptable to keep.
- States how to report "no corpus text available to search" (empty/missing location) distinctly
  from "searched thoroughly and found nothing."

## Entity: create-setting SKILL.md (rewritten)

**Location**: `wyrd-setting-template/.claude/skills/create-setting/SKILL.md`

**Frontmatter change**: add `model: sonnet` alongside the existing `name`/`description`/
`argument-hint`/`user-invocable`/`disable-model-invocation` fields.

**Phase 3 change**: every "ground it in corpus/" instruction rewritten to describe invoking the
`corpus-fact-finder` subagent with the specific claim and the relevant corpus location, and using
its returned outcome (support/contradict/not-found) to decide what to write and how to label it.
Prose-writing/register-synthesis instructions (voice.md's register, career/bestiary/entity content
composition, hedging on thin sources) are left as invoking-skill work, with an explicit sentence
stating why they stay there (FR-008).

**Phase 4 change**: the grep-verification spot-check rewritten to invoke the same subagent instead
of running `grep -rn` inline, reusing the same three-outcome contract.

## Interface: subagent invocation

Not a machine-checked API — this is a Claude Code subagent invocation, described here instead of
in a separate `contracts/` directory (see plan.md's Project Structure section):

- **Input**: one claim (text) + one corpus location (file or directory path under `corpus/`).
- **Output**: one of
  - `{"outcome": "support", "quote": "...", "location": "<file>:<line-or-nearest-marker>"}`
  - `{"outcome": "contradict", "quote": "...", "location": "<file>:<line-or-nearest-marker>"}`
  - `{"outcome": "not_found", "reason": "searched, no match" | "no corpus text available"}`

  (Illustrative shape for the subagent's own prose response — Claude Code subagents respond in
  natural language, not literal JSON; the invoking skill reads the outcome/quote/location from
  that response rather than parsing a formal schema.)
