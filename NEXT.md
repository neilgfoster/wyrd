# Queued work

## After the corpus run completes

The OCR/extraction pipeline is processing 510 files (v1 line + White Dwarf) into
`scratchpad/corpus/txt/`. Nothing below should start while it is running — two heavy jobs
competing for the box is what caused the OCR thrashing on 2026-08-20.

1. **Clean the corpus.** `clean.py` is written and tested; run it over `txt/` to strip
   OCR noise from art pages.

2. **Build the deterministic indexes** — `documents`, `nouns`, `terms`, `tables`.
   See [design/11-corpus-index.md](design/11-corpus-index.md). All four are single passes,
   no model.

   Then the `scenarios` index, which is the big one: selection filters checkable against
   `pc.yaml`, plus `requires_threads`/`emits_threads` so the meta-campaign tree emerges from
   thread matching rather than being authored. Library-wide, not just WFRP. Haiku-tier,
   lazy, cached.

3. **Extract 2e engine data.** All four sources are digital with text layers — no OCR
   needed, the cost is parser tuning:
   - **Careers** — *Career Compendium*, 258pp. Parser proven: 230 clean records with
     entries/exits/skills/talents/trappings. **Known bugs:** career names are off by one
     against their blocks, and exit lists bleed into following prose. Validate by checking
     the graph closes — every exit must resolve to a real career node, so the data checks
     itself. Emits `settings/reikland/careers.yaml`.
   - **Gear and prices** — *Old World Armoury*
   - **Creatures** — *Old World Bestiary*
   - **Mutation and corruption tables** — *Tome of Corruption*

4. **Mine the v1 adventures** for rules that never made the core book — career expansions,
   critical variants, Chaos material. Fold into the Reikland career graph and corruption
   tables.

5. **Apply the two 40k findings**, if approved — see
   [reference/40k-engine-impact.md](reference/40k-engine-impact.md):
   - split companions into a rich narrative layer and a deliberately thin mechanical one
   - give the party track a positive direction (Cohesion), and corruption a direction as
     well as a magnitude

## Then

- Engine skeleton: `TOOLS` catalog, `describe`, state layer with atomic writes and invariant
  validation, and `roll` / `damage` / `track`. Freeze the first golden chronicle immediately
  (see [design/09-evolution.md](design/09-evolution.md)).
- Resume the Hemmelfurt playtest — day 1 of 4, four leads open, and Wendel still needs to
  know who he resembles.
