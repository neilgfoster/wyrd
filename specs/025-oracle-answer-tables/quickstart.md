# Quickstart: validating the oracle answer tables

This feature is a design document and a data table, not runnable application code. Validation is
by script and by grep, per `CLAUDE.md`'s "deterministic over inference."

## Prerequisites

- Repo checked out on this feature's branch.
- Python 3 available (no extra dependencies).

## Verify the odds are computed, not asserted

```bash
python3 tools/check_oracle_answers.py
```

Expected: prints the row widths and total Yes/No odds for all five bands, and exits 0. A nonzero
exit means a row range in `docs/design/14-oracle-answers.md` disagrees with the maths this feature
committed to in `research.md`.

## Verify the table satisfies `docs/design/04-tables.md`'s own rules

`tools/check_oracle_answers.py` (above) already checks the numeric heart of this: ranges per band
are contiguous, cover `1d100` exactly with no gap or overlap, and the four widths sum to 100 for
every band. Read `docs/design/14-oracle-answers.md`'s table by eye against `docs/design/04-tables.md`'s
row schema to confirm every row carries `range`, `effect`, `description`, and the family's
declared `band` field, and that the key `oracle-answer` matches what `docs/design/04-tables.md`'s
index now publishes. (There is no loader to run this against yet — the engine that reads tables at
runtime is Stage 13's work, not this feature's.)

## Verify no setting or system vocabulary leaked in

```bash
grep -rniE '(d&d|dnd|pathfinder|call of cthulhu|blades in the dark|mythic|fate core|apocalypse world)' \
  docs/design/14-oracle-answers.md docs/design/04-tables.md docs/design/01-principles.md
```

Expected: no output.

## Verify the documentation graph still reaches this new file

```bash
python3 tools/check_docs.py
```

Expected: exits 0 — `docs/design/14-oracle-answers.md` is reachable from `README.md` via
`docs/design/04-tables.md`'s index, which already links every family in the table.

## Walk the scenario by hand

1. Read `docs/design/01-principles.md`'s (amended) obligation clause and confirm it names the same
   class of question `docs/design/14-oracle-answers.md` calls oracle-bound.
2. Pick an example question from the document at each of the five bands; confirm the row it
   points to and the probability shown for that row match `check_oracle_answer.py`'s output.
3. Confirm the document states, in one place, that the oracle roll's units digit is read as the
   ordinary Wyrd die, with no second complication table anywhere in the file.
