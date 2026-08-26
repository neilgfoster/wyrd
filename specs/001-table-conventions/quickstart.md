# Quickstart: validating the table conventions

**Feature**: `001-table-conventions` | **Date**: 2026-08-22

The deliverable is a design document, so validation is reading and grepping rather than running.
Every check below is mechanical except the last two, which are the ones a script cannot settle
(`CLAUDE.md`: check what can be checked, review what cannot).

## Prerequisites

Repository root, branch `001-table-conventions`. No tooling beyond `grep` and `git` — the engine
does not exist yet.

## 1. The document exists and is reachable

```bash
test -f docs/design/07-tables.md && echo present
grep -rn "03a-tables" design/ README.md
```

Expected: the file is present, and `docs/design/02-architecture.md`, `docs/design/03-rules.md`,
`docs/design/20-tooling.md` and `docs/design/26-authoring-a-setting.md` each link to it. A reader arriving at
any of the four documents that mention tables finds the conventions from there (SC-001).

## 2. The five structural questions are answered

Read `docs/design/07-tables.md` and confirm each of these is stated, not implied:

| Question | Requirement |
|---|---|
| What die, and where does the modifier come from? | FR-002 |
| Why can no total fall above the top row or below the bottom? | FR-003 |
| What happens on a duplicate, and when the table is exhausted? | FR-004, FR-004a |
| What fields does every row carry? | FR-005 |
| Where does a table live, and what is it called? | FR-008 |

Expected: a reader who has seen none of the sibling issues can answer all five without guessing
(SC-001).

## 3. The index matches the rest of the design set

```bash
grep -n "tables/" docs/design/02-architecture.md docs/design/20-tooling.md
```

Expected: both list the same five families — criticals, aftermath, transformations, afflictions,
oracles — and all five appear in the index in `docs/design/07-tables.md`. The two sets match exactly
(SC-002). `docs/design/20-tooling.md:84` omitted afflictions before this change; confirm it no longer
does.

## 4. Every rule's table reference resolves

```bash
grep -n -iE "table" docs/design/03-rules.md
```

Expected: every table named in the ruleset is a family present in the index. No rule names a table
the index does not know about (SC-005).

## 5. The index is append-only in practice

Inspect the index table in `docs/design/07-tables.md`. Expected: adding a sixth family is one new row
and touches no other line (SC-003). If a sibling would have to edit prose elsewhere to add its
family, the index is doing too much.

## 6. Nothing new was invented

```bash
grep -n -iE "version|schema_version" docs/design/07-tables.md
```

Expected: the document introduces no version, no storage location and no override key beyond those
`docs/design/19-state.md` and `docs/design/26-authoring-a-setting.md` already define (SC-007). Specifically:
no per-table version field anywhere.

## 7. No setting or system vocabulary

```bash
git diff main --unified=0 -- design/ | grep '^+' | grep -inE \
  "warhammer|d&d|dungeons|pathfinder|call of cthulhu|cthulhu|wfrp|runequest|savage worlds|gurps|traveller|shadowrun|vampire|glorantha|forgotten realms"
```

Expected: no matches. Then read the added prose for the subtler case a wordlist misses — a mechanic
name carrying genre, or a tonal register baked into an example (`CLAUDE.md` fault classes 2 and 5,
FR-016). The illustrative rows in the contract are deliberately placeholders for this reason.

## 8. The design set still agrees with itself

Read `docs/design/07-tables.md` against `docs/design/02-architecture.md`, `docs/design/20-tooling.md`,
`docs/design/22-evolution.md` and `docs/design/26-authoring-a-setting.md`. Expected: no statement in the new
document contradicts any of them, and where one did, that document was updated in the same change
(SC-006, FR-015). This is fault class 3 and grep does not find it — both documents read as coherent
on their own.
