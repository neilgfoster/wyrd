# Queued work

## Housekeeping

- `wyrd-40k` is superseded by the per-line setting repos and needs deleting.
  `gh` lacks the scope here: `gh auth refresh -h github.com -s delete_repo`
- Four transient corpus download failures to retry; five source PDFs appear genuinely
  corrupt in the collection.

## Corpus — extraction finished 2026-08-21

**Complete and parked. Deliberately not taken further** — the plan is to review this output
and build a setting from it *after* the engine exists.

Output is committed to the private research repo under `corpus/` — it lives there rather
than in a setting repo because 209 of the 443 documents are a magazine run spanning several
settings ([design/02-architecture.md](design/02-architecture.md)). 443 documents, 80.5 M characters. Two known gaps recorded in its
README: 10 failures, and **57 files skipped by a slug-collision bug** in the pipeline's
resumability check.

When picked up:

1. **Fix the slug collision** — hash the full path into the output name — and re-run for the
   missing 57. The pipeline is resumable, so only those are fetched.
2. **Retry the 5 transient download failures.**
3. **Clean the corpus.** `clean.py` is written and tested; run it over the extracted text to
   strip OCR noise from full-page art.

2. **Build the deterministic indexes** — `documents`, `nouns`, `terms`, `tables`
   ([design/11-corpus-index.md](design/11-corpus-index.md)). Four single passes, no model.

   Then the `arcs` index, which is the large one: selection inputs checkable against the
   player character, plus `requires_threads` / `emits_threads` so the campaign tree emerges
   from thread matching rather than being authored. Library-wide. Haiku-tier, lazy, cached.

3. **Extract setting data.** All sources are digital with text layers — no OCR needed, the
   cost is parser tuning:
   - **Careers** — done for one setting (201 records). Known gaps recorded in the file.
   - **Gear and prices**, **creatures**, **transformation and taint tables** — same shape.

4. **Mine the older adventure lines** for rules that never made their core books, and fold
   what is generalisable into the engine rather than a setting.

5. **Decide the two open engine questions**, both raised by reading the 40k line:
   - split companions into a rich narrative layer and a deliberately thin mechanical one
   - give the party track a positive direction, and Taint a direction as well as a magnitude

## Then

- **Engine skeleton** — the `TOOLS` catalog, `describe`, the state layer with atomic writes
  and invariant validation, and `roll` / `damage` / `track`. Freeze the first golden
  chronicle immediately ([design/09-evolution.md](design/09-evolution.md)).
- **A journey subsystem.** One planned setting needs travel played rather than narrated. Per
  the hard rule, that goes in the **core**, generalised — not in the setting.
- **Resume the playtest.** Its chronicle lives in its own repository.
