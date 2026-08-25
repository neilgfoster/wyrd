# Working on Wyrd

Ground rules for contributing to this repository.

**This is not the GM contract.** That governs how the engine behaves *at play time* and lives
in [`design/01-principles.md`](design/01-principles.md). This file governs how Wyrd itself
gets built.

---

## The repositories

| Repo | Holds | Visibility |
|---|---|---|
| **wyrd** *(this one)* | engine, design, decision records | **intended public** |
| **wyrd-\<setting\>** | one setting: world, content, indexes | private where its sources are |
| **wyrd-chronicle-template** | cloned to start a chronicle | template |
| **wyrd-chronicle-\<name\>** | one per chronicle | the player's |
| **wyrd-research** | corpus, mining notes, extractions, source tooling | **never public** |

**Nothing unpublishable may enter this repository.** No extracted source text, no quotes from
copyrighted rulebooks, no catalogue of a personal library, no tooling that fetches source
material. If it derives from someone else's book, it belongs in research.

## Decisions are recorded

Significant decisions become **ADRs** in [`design/adr/`](design/adr/), numbered and dated.

A decision earns a record when **both** hold:

1. a real alternative was rejected — a workable option that would have produced a different
   engine, not merely a choice of name
2. someone would plausibly propose it again, including you, in a year, having forgotten why
   not

An accepted ADR is **never edited**. If the decision changes, write a new one that supersedes
it and leave both — the rejected reasoning is as useful as the winning reasoning.

Design documents are the opposite: **rewritten in place, always describing the present.** Do
not append changelogs or leave "previously we…" notes in them. Git holds the history.

## The engine is setting-agnostic

- **No setting or system names** in `design/` or `README.md` — not in prose, not in examples,
  not in a table row.
- **Engine labels are descriptive English**, never a term borrowed from a source system. If a
  label only makes sense to someone who has read a particular book, it belongs in a setting's
  `rename:` block. *(This is how "Fellowship phase" survived five review passes: it does not
  look like a setting reference, it looks like a mechanic.)*
- **Tone is a setting property.** Grim, heroic, comic — the engine holds whatever line the
  setting draws. Never bake a register into a mechanic's description.
- Mechanic names are **defaults**; settings rename them, and renames are presentation-only.

## Work is tracked as GitHub issues, via kord

There is **no backlog file**. Open work lives on the board, because two lists of the same work
drift — which is the fault class most of this design has been corrected for.

- **Board:** the `wyrd` GitHub Project (v2). It is not repo-scoped, so it spans the engine,
  the settings and the research repo.
- **Epics** are `kord-epic`-labelled issues **in this repo**, which is the meta repo. An epic may
  have children in any `wyrd-*` repository.
- **Features** are `kord-feature`-labelled issues raised **in the repo that owns the work**.
- Epics **nest recursively** — a child is either a further epic or a feature-sized issue. There is
  no level above an epic.

| To | Use |
|---|---|
| log a requirement bigger than one feature | `kord-epic-create` |
| break one down into children | `kord-epic-decompose` |
| find one again | `kord-epic-list` |
| log feature-sized work | `kord-feature-create` |
| take a feature from spec to open PR | `kord-loop-feature` |
| see what is actually actionable now | `kord-board-help` |
| decide what to implement next | `python3 tools/backlog.py next` |

Both kord substrates are installed here: `github-issues` (the three `kord-*` labels and the issue
templates) and `speckit` (the `speckit-*` skills and `.specify/`). **Do not hand-edit either
substrate's files** — they are owned by `kord-install` and re-running it will overwrite them.

**Capability changes go through the Spec Kit cycle.** Anything that adds or changes engine
behaviour is specified before it is written: `kord-feature-specify` → `clarify` → `plan` →
`tasks` → `implement`. `specs/<feature>/` is **committed** — a spec is a design artefact and
belongs in the history. Documentation-only changes are exempt; the gate is on capability, not on
every commit.

Where a spec and a design document disagree, the design document is the engine's description and
the spec is one change to it. Update the design document when the change lands, and do not leave
the spec as the only record of current behaviour.

**Reference the issue number in commits**, and let the issue carry the reasoning that does not
belong in a design document.

### The backlog has an order

kord records a dependency order inside an epic and no priority order anywhere. Wyrd's priority
order is a numeric **`Rank`** field on the board, on **root-level items only** — issues with no
parent ([`design/adr/0010`](design/adr/0010-backlog-order-lives-on-the-board.md)). Children are
not ranked; they already carry `Depends on: #N`, and a second ordering of the same work is the
drift this repo keeps being corrected for.

```bash
python3 tools/backlog.py next     # the one issue to work on, and what it passed over
python3 tools/backlog.py list     # the whole ordered tree, with what is blocked
python3 tools/backlog.py check    # drift guard; non-zero exit on any problem
```

`next` does not stop at the rank. It descends the sub-issue tree to a **ready leaf** — no open
children, every declared dependency closed — because an epic is never something you can start.
**Where priority and dependency disagree, dependency wins:** a rank orders what you choose
between, it never authorises work whose prerequisites are open.

**Raising root-level work includes ranking it.** Ranks are seeded in tens, so inserting between
two items is one number, not a renumbering. Two things to know:

- `kord-epic-create` adds its issue to the board; **`kord-feature-create` does not.** A
  root-level feature must be added by hand (`gh project item-add`) before it can be ranked.
- `tools/backlog.py check` catches an unranked root, a duplicate rank, a labelled issue missing
  from the board, and a `Depends on:` naming an issue that does not exist. Run it after raising
  work rather than assuming the order is still whole.

### The documents are a checked graph

The repo is an Obsidian vault. **Prose links with markdown, entity data links with
`[[wikilinks]]`** ([`design/adr/0011`](design/adr/0011-markdown-links-in-prose-wikilinks-in-data.md)) —
GitHub does not render wikilinks and this repo is read there.

```bash
python3 tools/check_docs.py     # reachability, dead links, ADR index, link policy
```

Every document under `design/` must be reachable from `README.md`, directly or through an index it
links to. Adding a design document means linking it from the hub; the check fails otherwise. Four
indexes had already gone stale silently before this existed, so treat it the same way as
`backlog.py check` — run it, do not assume.

## Deterministic over inference

The rule the engine follows ([`design/07-tooling.md`](design/07-tooling.md)) applies to the
work as well. Where a claim can be checked by a script, check it — do not assert it.

Concretely, and from experience:

- **Verify a background job is actually running.** `pgrep -f foo.sh` matches its own command
  line. Twice this looked like progress and was not.
- **Bulk find-and-replace is dangerous.** It has produced `diffisecty` from *difficulty*,
  `secture` from *culture*, and "No otherworldly power, no database" from *daemon*. After any
  substitution, grep for damage rather than assuming.
- **Check the maths.** Probability claims were wrong twice, and both were only caught by
  computing them.

## Recurring faults worth checking for

Each review pass of this repo has found a different class. In rough order of how hard they
are to see:

1. **Setting vocabulary** — findable by grep.
2. **Mechanic names carrying genre** — a track called *Corruption* presumes moral decay.
3. **Two documents describing one thing differently** — both internally coherent, so neither
   reads as wrong. Found only by reading them against each other.
4. **Stale but plausible specifications** — a code example or schema that was correct two
   decisions ago. Reads as authoritative and is not.
5. **Tone baked into a mechanic's description** rather than its vocabulary.

**Tables are where staleness hides**, because each row reads as a small factual claim rather
than an argument, and nothing about a wrong one looks wrong.

## Commits

Explain **why**, not what — the diff already says what. Name the fault that was fixed and, if
it was subtle, why it survived. Reference backlog identifiers where they apply.

Avoid backticks in commit message bodies; they are shell-interpreted and have silently eaten
words here before.

## Before proposing a rule change

The engine has been playtested exactly once, and that session corrected the resolution
mechanic three times inside two rolls — none of it visible on paper. **Prefer playing a rule
over arguing about it.** Where a mechanic is uncertain, run the numbers at the values a real
character actually has, not at the midpoint.

Rules changes apply **forward only**. History is never recomputed
([`design/09-evolution.md`](design/09-evolution.md)).
