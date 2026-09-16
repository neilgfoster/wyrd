# Research: Haiku corpus fact-finder subagent for create-setting

## Decision: subagent-definition file format

**Decision**: A `.claude/agents/<name>.md` file with YAML frontmatter carrying `name`,
`description`, `tools`, and `model`, followed by the subagent's system-prompt-style instructions
as the file body — no other required fields.

**Rationale**: Confirmed directly against real, shipping examples on this machine rather than
guessed:

- `/root/.claude/plugins/marketplaces/claude-plugins-official/plugins/feature-dev/agents/code-explorer.md`
  — `name: code-explorer`, `description: ...`, `tools: Glob, Grep, LS, Read, NotebookRead,
  WebFetch, TodoWrite, WebSearch, KillShell, BashOutput`, `model: sonnet`, plus an optional
  `color:` field.
- `/root/.claude/plugins/marketplaces/claude-plugins-official/plugins/code-modernization/agents/test-engineer.md`
  — `name`, `description`, `tools` only (no `model:`, no `color:`), demonstrating both fields
  beyond `name`/`description`/`tools` are optional.

`model:` accepts `haiku | sonnet | opus | inherit` per the issue's own verified statement, matching
`code-explorer.md`'s `model: sonnet` usage.

**Alternatives considered**: Inventing a schema instead of checking real examples — rejected per
the issue's own explicit instruction and per this repository's "deterministic over inference"
rule (`docs/design/27-tooling.md` section 1): a checkable claim about file format must be
checked, not guessed.

## Decision: subagent's tool list

**Decision**: `Read, Grep, Glob` — read files, search their contents, and enumerate the corpus
directory tree. No `Write`, `Edit`, `Bash`, or web-access tools.

**Rationale**: FR-002/FR-003 scope the subagent to retrieval and reporting only — locating a
verbatim quote in already-extracted `corpus/*.txt` files and reporting its source location.
`Read`/`Grep`/`Glob` are sufficient for that and nothing more; omitting write/execute/web tools
is itself part of the mechanical-vs-judgement boundary (a retrieval-only tool a subagent cannot
misuse to write setting content, matching the issue's "closed, mechanical retrieval task" framing
and `docs/design/27-tooling.md`'s Haiku-tier description: "Mechanical language work with a right
answer").

**Alternatives considered**:
- Adding `Bash` for `grep -rn` calls — rejected; `Grep`/`Glob` already give equivalent search
  capability without shell access, keeping the subagent's tool surface minimal and auditable.
- Adding `WebFetch`/`WebSearch` — rejected outright; corpus fact-finding is explicitly scoped to
  `corpus/` text only (per the issue and spec's Edge Cases), never web research, which is a
  separate, existing Phase 1 permission the invoking skill handles itself.

## Decision: subagent invocation shape (input/output contract)

**Decision**: The subagent is invoked with two inputs — the specific claim to ground (a name,
quote, statistic, or fact) and a corpus location (a file or directory under `corpus/`) — and
returns one of three outcomes: (1) a supporting quote with its exact source file and
line/location, (2) a contradicting quote with its exact source file and line/location, labelled
as contradicting, or (3) an explicit not-found result, distinguishing "searched and found
nothing" from "no corpus text available to search" (per the spec's Edge Cases).

**Rationale**: This is the smallest contract that satisfies FR-002 (closed, checkable retrieval)
while giving the invoking Sonnet-tier skill everything it needs to decide what to write and how to
label it — the subagent never decides whether a claim is acceptable to keep, only what the corpus
does or does not say about it. Keeping the outcome three-valued (support / contradict / not-found)
rather than binary matches spec Acceptance Scenario 3 and avoids forcing the invoking skill to
re-derive "contradicting" from a bare quote.

**Alternatives considered**: A binary yes/no with no quote returned — rejected; without the exact
quote and location, the invoking skill could not write an accurate, checkable grounding note, and
Phase 4's own grep-verification step (which this subagent now also performs) already requires the
exact match text.

## Decision: where Phase 3/4 delegate versus where they don't

**Decision**: Every step that locates or verifies a specific claim's textual support in `corpus/`
delegates to the subagent. Every step that decides what a `voice.md` register sounds like,
composes career/gear/bestiary/entity prose, or judges whether a thin/ambiguous source is enough to
proceed stays on the invoking Sonnet-tier skill.

**Rationale**: This is exactly the boundary the issue and `docs/design/27-tooling.md` section 5
already draw ("mechanical corpus-reading... mixes with... genuine judgement... the class
27-tooling.md keeps on the capable tier"). Re-reading `create-setting`'s existing Phase 3/4
text (see `wyrd-setting-template/.claude/skills/create-setting/SKILL.md`) confirms every
claim-grounding mention ("ground it in this setting's actual corpus/ text", the Phase 4 grep
spot-check) is a retrieval action, while every mention of writing register, deciding what belongs,
or hedging on ambiguous sources is a judgement action — no existing sentence mixes the two, so the
rewrite can split cleanly along existing paragraph boundaries rather than needing to invent new
structure.

**Alternatives considered**: Delegating the whole of Phase 3 to Haiku — rejected outright by the
issue itself and by `docs/design/27-tooling.md`'s explicit stance that narration/voice/judgement
never moves to a smaller model. Leaving Phase 4's grep step inline (not delegated) — rejected,
since it is the same mechanical retrieval action as Phase 3's grounding calls and the issue names
it explicitly ("Phase 4's grep-verification step, if it overlaps").
