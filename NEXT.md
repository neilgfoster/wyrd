# Queued work

## Housekeeping

- **`wyrd-<sf-setting>` needs deleting** — superseded by wyrd-darkheresy / wyrd-onlywar /
  wyrd-roguetrader. `gh` lacks the `delete_repo` scope here:
  `gh auth refresh -h github.com -s delete_repo`
- Four transient corpus PULLFAILs to retry; five White Dwarf PDFs (#005, #034, #077, #079,
  #080) appear genuinely corrupt in the source collection.


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
   thread matching rather than being authored. Library-wide, not just the source system. Haiku-tier,
   lazy, cached.

3. **Extract 2e engine data.** All four sources are digital with text layers — no OCR
   needed, the cost is parser tuning:
   - **Careers** — *Career Compendium*, 258pp. Parser proven: 230 clean records with
     entries/exits/skills/talents/trappings. **Known bugs:** career names are off by one
     against their blocks, and exit lists bleed into following prose. Validate by checking
     the graph closes — every exit must resolve to a real career node, so the data checks
     itself. Emits `settings/reikland/careers.yaml`.
   - **Gear and prices** — *world Armoury*
   - **Creatures** — *world Bestiary*
   - **Mutation and corruption tables** — *Tome of Corruption*

4. **Mine the v1 adventures** for rules that never made the core book — career expansions,
   critical variants, the corrupting power material. Fold into the starting region career graph and corruption
   tables.

5. **Apply the two the science-fiction line findings**, if approved — see
   [reference/the science-fiction line-engine-impact.md](https://github.com/neilgfoster/wyrd-research/blob/main/reference/the science-fiction line-engine-impact.md):
   - split companions into a rich narrative layer and a deliberately thin mechanical one
   - give the party track a positive direction (Cohesion), and corruption a direction as
     well as a magnitude

## Then

- Engine skeleton: `TOOLS` catalog, `describe`, state layer with atomic writes and invariant
  validation, and `roll` / `damage` / `track`. Freeze the first golden chronicle immediately
  (see [design/09-evolution.md](design/09-evolution.md)).
- Resume the the town playtest — day 1 of 4, four leads open, and the PC still needs to
  know who he resembles. Chronicle now lives at `neilgfoster/wyrd-chronicle-hemmelfurt`
  (private).

## Now that Wyrd is a generic engine

- Corpus text commits into the relevant **setting** repo (private), with indexes beside it.
- Beat conversion is **on demand** — when a campaign needs a stub, convert it and commit back.
- Character/location/faction stubs still to be seeded from the corpus concordance once the
  indexes exist.
- The engine has no journey subsystem; `wyrd-tor` will need one, and per the hard rule it
  goes in the **core**, generalised, not in the setting.
