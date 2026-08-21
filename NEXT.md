# Queued work

## Housekeeping

- `wyrd-40k` is superseded by the per-line setting repos and needs deleting.
  `gh` lacks the scope here: `gh auth refresh -h github.com -s delete_repo`
- Four transient corpus download failures to retry; five source PDFs appear genuinely
  corrupt in the collection.

## After the corpus run completes

Nothing below should start while extraction is running — two heavy jobs competing for the
machine is what caused the OCR thrashing on 2026-08-20.

1. **Clean the corpus.** `clean.py` is written and tested; run it over the extracted text to
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
