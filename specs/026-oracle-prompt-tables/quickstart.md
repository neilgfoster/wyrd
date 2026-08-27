# Quickstart: validating the oracle prompt tables

This feature is a design document and rollable tables, not runnable application code. Validation
is by script and by grep, per `CLAUDE.md`'s "deterministic over inference."

## Prerequisites

- Repo checked out on this feature's branch.
- Python 3 available (no extra dependencies).

## Verify the tables are structurally sound

```bash
python3 tools/check_oracle_prompts.py
```

Expected: for each of the four `oracle-prompt-*` tables in `docs/design/15-oracle-prompts.md`,
prints its row count and confirms ranges are contiguous, start at 1, and the last row is open at
the top (`docs/design/04-tables.md`'s row-schema rule); confirms every row carries the `checked` extra
field; exits 0. A nonzero exit means a row range disagrees with the schema, or a row is missing
its recorded genre-neutrality check.

## Verify every row's genre-neutrality check is recorded, by eye

There is no computable "grim-and-comic" test — genre-neutrality is a qualitative reading, not a
number (`research.md`). `tools/check_oracle_prompts.py` (above) confirms every row *has* a
recorded check; read `docs/design/15-oracle-prompts.md` by eye against a grim example and a comic
example for a handful of rows per table to spot-check that the recorded checks are honest, not
merely present.

## Verify no setting or system vocabulary leaked in

```bash
grep -rniE '(d&d|dnd|pathfinder|call of cthulhu|blades in the dark|mythic|fate core|apocalypse world)' \
  docs/design/15-oracle-prompts.md docs/design/04-tables.md docs/design/24-authoring-a-setting.md
```

Expected: no output.

## Verify the documentation graph still reaches this new file

```bash
python3 tools/check_docs.py
```

Expected: exits 0 — `docs/design/15-oracle-prompts.md` is reachable from `README.md` via
`docs/design/04-tables.md`'s index, which already links every family in the table.

## Walk the scenario by hand

1. Pick one example situation per family (an NPC whose objective isn't established; a scene that
   isn't as presented; a thread due to turn; a scene needing a complication) and confirm
   `docs/design/15-oracle-prompts.md` states plainly that the GM is obliged to roll rather than
   invent in each case.
2. Roll (or pick) a row from each of the four tables and confirm its `effect` maps onto a field
   `docs/design/16-session.md` or `docs/design/19-campaign.md` / `docs/design/18-arcs-and-beats.md` already
   defines, with no new state structure invented to hold it.
3. Read `docs/design/24-authoring-a-setting.md`'s amended `extend:` override and confirm a
   setting-authored extra-rows file for one prompt table is accepted by the rules stated there
   without needing to replace the engine's own rows.
