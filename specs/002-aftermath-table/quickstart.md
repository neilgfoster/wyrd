# Quickstart: verifying the Aftermath table

**Feature**: 002-aftermath-table | **Date**: 2026-08-22

How to check this feature is actually done. `CLAUDE.md`: where a claim can be checked by a script,
check it — do not assert it. Run these from the repository root.

---

## 1. The ranges and the distribution

```bash
python3 specs/002-aftermath-table/check_aftermath.py
```

Exits `0` when all of these hold, and prints which failed when they do not:

- ranges contiguous from 6, non-overlapping, last row open at the top
- every reachable total lands on exactly one row
- a lasting mark is the common outcome and death the uncommon one, across drops of 1–12
- a combatant dropped by 1 or 2 cannot reach the death row, at any `mortality`
- `mortality: low` closes the death rows entirely

**This is the check that matters.** It rejected the first draft of the `mortality` design, which read
perfectly well and was wrong in two ways (see [research.md](./research.md) D2).

## 2. The document's rows match the script's

The script holds the rows separately from the prose, so they can drift. Confirm they agree:

```bash
grep -oE '^\| [0-9]+([–-][0-9]+)?\+? \|' design/03a-2-aftermath.md
grep -nE '^\s+\([0-9]+,' specs/002-aftermath-table/check_aftermath.py
```

Every range in the document must appear in `ROWS`, and vice versa. A row present in one and not the
other is exactly the staleness `CLAUDE.md` says tables breed.

## 3. Every promised outcome shape has a row

`design/03-rules.md` promises five shapes plus death. Each must be findable:

```bash
for key in out-of-action lasting-wound left-for-dead new-enemy taken \
           disfigured recurring-wound death; do
  printf '%-18s ' "$key"
  grep -qF "$key" design/03a-2-aftermath.md && echo present || echo "MISSING"
done
```

## 4. Every mechanic named is one the engine already publishes

A denylist of system names would be the obvious check and is the weaker one: it only catches the
names whoever wrote the list thought of, and it puts a list of other people's game titles into a
repository that is intended public. The **allowlist** is stronger — every capitalised mechanic in the
new document must be a label `design/03-rules.md` already publishes.

```bash
# Labels the ruleset publishes, plus the ordinary vocabulary of a design document.
grep -oE '\*\*[A-Z][a-zA-Z ]+\*\*' design/03-rules.md | tr -d '*' | sort -u > /tmp/wyrd-labels

# Capitalised terms in the new document that are not sentence-initial.
grep -oE '[a-z,] [A-Z][a-z]+' design/03a-2-aftermath.md \
  | sed -E 's/^[a-z,] //' | sort -u
```

Read the second list against the first. Anything in it that is not an engine label, a document
reference or ordinary English is the thing this check exists to find: a term that only makes sense to
someone who has read a particular book.

Then read the rows once for what no script catches — a description carrying a tonal register the
setting should own.

## 5. The index no longer says "not yet written"

```bash
grep -n 'Aftermath' design/03a-tables.md
```

The row must name the roll (`d100 + 5 × points below zero`), the uniqueness (`repeatable`), and link
to `03a-2-aftermath.md`. Every cell must match what the document actually declares — check them
against [contracts/aftermath-table.md](./contracts/aftermath-table.md), not against memory.

## 6. `03-rules.md` no longer describes an undefined table

```bash
sed -n '/Death is deferred/,/^---/p' design/03-rules.md
```

It must link to `03a-2-aftermath.md`, and must not still enumerate the five outcome shapes as a
promise — the table is where they live now. No changelog, no "previously".

## 7. Read the two documents against each other

The check no script performs, and the fault class `CLAUDE.md` ranks hardest to see: two documents
describing one thing differently, both internally coherent.

Read `design/03-rules.md` §2 and §3 against `design/03a-2-aftermath.md`, and confirm each of these
resolves to exactly one reading:

- when the Aftermath roll happens, relative to the fight and to the critical
- what a spent Fate point does to a death result
- whether a companion rolls, and what happens when they roll death
- what `mortality` changes

---

## The manual walkthrough

Four totals, resolved with the document alone. No step may need a judgement the document does not
cover.

| Case | Modifier | Total | Expected row |
|---|---|---|---|
| Dropped by 1, rolled 3 | +5 | 8 | `out-of-action` — nothing lasting |
| Dropped by 4, rolled 61 | +20 | 81 | `taken` — a thread opens |
| Dropped by 7, rolled 90 | +35 | 125 | `death` |
| Dropped by 7, rolled 90, Fate spent | +35 | 125 | `recurring-wound` — survives, not better off |

The last two are the same roll. That is the point: Fate changes which row is applied and never what
was rolled, which is what keeps `design/03-rules.md`'s natural roll rule intact.
