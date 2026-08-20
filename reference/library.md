# TTRPG Library Catalogue

Index of the source collection Wyrd draws on. **Metadata only** — no book content is stored
in this repo. The library lives in OneDrive and is pulled on demand.

- **Location:** `onedrive:Games/Tabletop` (rclone remote `onedrive`, personal account)
- **Generated:** 2026-08-20
- **Totals:** 8840 files · 3841 PDFs · 112 system folders · 57.5 GB

Folders nest up to 7 levels; major lines are split by edition (e.g. WFRP v1–v4).

## How to pull a file

```bash
rclone lsf "onedrive:Games/Tabletop/<folder>" --recursive       # browse — works
python3 tools/pull.py "<path under Games/Tabletop>" out.pdf     # fetch one file
```

**Do not use `rclone cat` / `rclone copy` for content.** Debian's rclone 1.60.1 (2022) fails
on OneDrive *personal* downloads with `unauthenticated` — listing uses a different code path
and works fine, which is why the catalogue above could be built. `tools/pull.py` goes
straight to the Graph `@microsoft.graph.downloadUrl` and handles token refresh.

Microsoft's refresh tokens are **single-use/rotating**, so concurrent refreshes invalidate
each other and kill the stored token. `pull.py` serialises refresh behind an `flock`; do not
work around it.

---

## Tier 1 — Rules candidates

The systems Wyrd's ruleset is built from or checked against.

### Warlock!

`Games/Tabletop/Warlock!` — 8 PDFs, 27 MB

### Warhammer Fantasy Roleplay

`Games/Tabletop/Warhammer Fantasy Roleplay` — 527 PDFs, 9141 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 2 |
| 01 - Warhammer Fantasy Roleplay v1 | 292 |
| 02 - Warhammer Fantasy Roleplay v2 | 71 |
| 03 - Warhammer Fantasy Roleplay v3 | 109 |
| 04 - Warhammer Fantasy Roleplay v4 | 20 |
| 05 - Zweihander | 2 |
| 06 - Additional Material | 7 |
| 07 - Maps | 4 |
| 08 - Warhammer Soulbound | 20 |

### Warhammer 40,000 Roleplay

`Games/Tabletop/Warhammer 40,000 Roleplay` — 148 PDFs, 5135 MB

| Sub-folder | PDFs |
|---|---|
| 01 - Dark Heresy | 40 |
| 02 - Rogue Trader | 40 |
| 03 - Deathwatch | 23 |
| 04 - Black Crusade | 10 |
| 05 - Only War | 13 |
| 06 - The Fall of Solace | 4 |
| 07 - Wrath and Glory | 18 |

### Advanced Fighting Fantasy

`Games/Tabletop/Advanced Fighting Fantasy` — 36 PDFs, 623 MB

| Sub-folder | PDFs |
|---|---|
| 01 - Advanced Fighting Fantasy - 1st Edition | 5 |
| 02 - Advanced Fighting Fantasy - 2nd Edition | 16 |
| 03 - Warhammer Fighting Fantasy Roleplay | 2 |
| 04 - Fighting Fantasy d20 | 8 |
| 05 - Stella Adventures | 5 |

### Fighting Fantasy

`Games/Tabletop/Fighting Fantasy` — 191 PDFs, 1965 MB

| Sub-folder | PDFs |
|---|---|
| 00 - Others | 93 |
| 01 - Fighting Fantasy | 66 |
| 02 - Sorcery | 5 |
| 03 - Warlock Magazine | 13 |
| 04 - Fighting Fanzine | 14 |

---

## Tier 2 — Warhammer setting sources

Not RPG rules, but the richest setting, faction and place material for both settings.

### Warhammer Fantasy Battle

`Games/Tabletop/Warhammer Fantasy Battle` — 66 PDFs, 1474 MB

| Sub-folder | PDFs |
|---|---|
| 01 - 1st Edition | 10 |
| 02 - 2nd Edition | 9 |
| 03 - 3rd Edition | 3 |
| 04 - Warhammer Armies | 16 |
| 06 - 6th Edition | 28 |

### Warhammer 40,000

`Games/Tabletop/Warhammer 40,000` — 73 PDFs, 2067 MB

| Sub-folder | PDFs |
|---|---|
| Kill Team | 29 |
| Warhammer 40,000 v1 | 12 |
| Warhammer 40,000 v2 | 6 |
| Warhammer 40,000 v5 | 21 |
| Warhammer 40,000 v8 | 5 |

### Warhammer Age of Sigmar

`Games/Tabletop/Warhammer Age of Sigmar` — 71 PDFs, 102 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 5 |
| 01 - Old World | 16 |
| 02 - Stormcast Eternals | 5 |
| 03 - Free Peoples | 11 |
| 04 - Slaves to Darkness | 13 |
| 05 - Blades of Khorne | 5 |
| 06 - Skaven | 10 |
| 07 - Brayherds | 6 |

### Mordhiem

`Games/Tabletop/Mordhiem` — 114 PDFs, 645 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 10 |
| Buildings | 1 |
| Campaigns | 10 |
| Miscellaneous | 7 |
| Optional Rules | 11 |
| Scenarios | 19 |
| Town Cryer | 30 |
| Warbands | 26 |

### Necromunda

`Games/Tabletop/Necromunda` — 10 PDFs, 67 MB

### Inquisitor

`Games/Tabletop/Inquisitor` — 7 PDFs, 10 MB

### Warhammer Quest

`Games/Tabletop/Warhammer Quest` — 9 PDFs, 64 MB

### Wyrdwars

`Games/Tabletop/Wyrdwars` — 26 PDFs, 16 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 5 |
| Warbands | 21 |

### Shadow War Armageddon

`Games/Tabletop/Shadow War Armageddon` — 10 PDFs, 61 MB

### Blood Bowl

`Games/Tabletop/Blood Bowl` — 3 PDFs, 31 MB

### Space Hulk

`Games/Tabletop/Space Hulk` — 62 PDFs, 506 MB

| Sub-folder | PDFs |
|---|---|
| 01 - Space Hulk 1st Edition | 10 |
| 02 - Space Hulk 2nd Edition | 2 |
| 03 - Space Hulk 3rd Edition | 3 |
| 04 - White Dwarf | 26 |
| 05 - Missions | 5 |
| 08 - Space Hulk Kill Team | 5 |
| 10 - Tiles And Counters | 11 |

### Space Crusade

`Games/Tabletop/Space Crusade` — 1 PDFs, 2 MB

### Coreheim

`Games/Tabletop/Coreheim` — 4 PDFs, 2 MB

---

## Tier 3 — Solo & GM-emulation toolkit

Prior art for running one player with an NPC party, and for pacing without a group.

### Mythic

`Games/Tabletop/Mythic` — 2 PDFs, 19 MB

### Scarlet Heroes

`Games/Tabletop/Scarlet Heroes` — 4 PDFs, 241 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 2 |
| 01 - Additional Content | 2 |

### Beyond the Wall

`Games/Tabletop/Beyond the Wall` — 77 PDFs, 56 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 10 |
| 01 - Playbooks | 42 |
| 02 - Scenario Packs | 10 |
| 03 - Threat Packs | 9 |
| 06 - Maps | 1 |
| 07 - Sheets | 5 |

### Sellswords and Spellslingers

`Games/Tabletop/Sellswords and Spellslingers` — 11 PDFs, 224 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 3 |
| A4 | 4 |
| Letter | 4 |

### Rangers of Shadow Deep

`Games/Tabletop/Rangers of Shadow Deep` — 3 PDFs, 65 MB

### Destiny Quest

`Games/Tabletop/Destiny Quest` — 20 PDFs, 12 MB

### Lone Wolf Adventure Game

`Games/Tabletop/Lone Wolf Adventure Game` — 21 PDFs, 195 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 8 |
| 01 - Action Charts | 8 |
| 02 - Additional Content | 5 |

---

## Tier 4 — Tone-compatible scenario donors

Different systems, right register. Mine for scenarios adaptable to Wyrd.

### Maelstrom

`Games/Tabletop/Maelstrom` — 17 PDFs, 345 MB

| Sub-folder | PDFs |
|---|---|
| 01 - Maelstrom | 13 |
| 02 - Maelstrom Domesday | 4 |

### Troika!

`Games/Tabletop/Troika!` — 4 PDFs, 32 MB

### Cairn

`Games/Tabletop/Cairn` — 13 PDFs, 190 MB

### Mausritter

`Games/Tabletop/Mausritter` — 133 PDFs, 4240 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 10 |
| Itch | 88 |
| Moonshore | 10 |
| Tomb of a Thousand Doors | 8 |
| mausritter-adventure-collection | 17 |

### Barbarians of Lemuria

`Games/Tabletop/Barbarians of Lemuria` — 3 PDFs, 23 MB

### Sharp Swords & Sinister Spells

`Games/Tabletop/Sharp Swords & Sinister Spells` — 1 PDFs, 10 MB

### Crimson Blades

`Games/Tabletop/Crimson Blades` — 2 PDFs, 32 MB

### Dark Future

`Games/Tabletop/Dark Future` — 1 PDFs, 28 MB

### Wreck Age

`Games/Tabletop/Wreck Age` — 12 PDFs, 41 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 3 |
| 01 - Additional Content | 9 |

### Atomic Highway

`Games/Tabletop/Atomic Highway` — 17 PDFs, 81 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 10 |
| 01 - Additional Content | 7 |

### Exodus

`Games/Tabletop/Exodus` — 25 PDFs, 101 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 4 |
| Scenarios | 21 |

### The End of the World

`Games/Tabletop/The End of the World` — 2 PDFs, 24 MB

### Weird West

`Games/Tabletop/Weird West` — 3 PDFs, 5 MB

### Red Sands Black Moon

`Games/Tabletop/Red Sands Black Moon` — 1 PDFs, 10 MB

### Dungeon Crawl Classics

`Games/Tabletop/Dungeon Crawl Classics` — 1 PDFs, 85 MB

### Strange Magic

`Games/Tabletop/Strange Magic` — 8 PDFs, 18 MB

### Folklore

`Games/Tabletop/Folklore` — 6 PDFs, 64 MB

| Sub-folder | PDFs |
|---|---|
| (root) | 2 |
| 01 - Additional Content | 4 |

### Deadlands

`Games/Tabletop/Deadlands` — 2 PDFs, 35 MB

---

## Tier 5 — Magazine archive

Short-form adventure and NPC material, ideal for single-session play.

### White Dwarf

`Games/Tabletop/White Dwarf` — 218 PDFs, 7511 MB

---

## Everything else

Not directly targeted for Wyrd, but present and searchable.

| System | PDFs | Size |
|---|---|---|
| A Song of Ice and Fire | 6 | 149 MB |
| Adventurers | 77 | 192 MB |
| Apocalypse World | 3 | 8 MB |
| Bag of Dungeon | 3 | 26 MB |
| Barebones Fantasy RPG | 37 | 323 MB |
| Brikwars | 1 | 7 MB |
| Castles & Crusades | 11 | 97 MB |
| Covert Ops | 19 | 75 MB |
| Crowns | 10 | 95 MB |
| Custom | 3 | 224 MB |
| D6 System | 87 | 3669 MB |
| Darkfast Dungeons | 25 | 218 MB |
| Dawn of Worlds | 1 | 1 MB |
| Descent | 18 | 294 MB |
| Dichotomy | 1 | 1 MB |
| Dragon Age | 33 | 179 MB |
| Dragon Rampant | 7 | 93 MB |
| Dump Quest | 21 | 16 MB |
| Dungeon Squad | 1 | 0 MB |
| Dungeon World | 56 | 455 MB |
| Dungeons & Dragons | 39 | 541 MB |
| Elite Dangerous | 22 | 223 MB |
| Escape the Dark Castle | 0 | 130 MB |
| Fate | 5 | 7 MB |
| Folklore Realms | 1 | 12 MB |
| Free Universal | 3 | 3 MB |
| Frostgrave | 7 | 20 MB |
| Fudge | 1 | 2 MB |
| Gurps | 2 | 18 MB |
| Hackmaster | 1 | 20 MB |
| Hakkenslash | 1 | 3 MB |
| Hero Kids | 40 | 733 MB |
| Heroes against Darkness | 1 | 32 MB |
| Hex Kit | 1 | 730 MB |
| Kings of War | 9 | 1 MB |
| Labyrinth Lord | 4 | 15 MB |
| Legend (Mongoose) | 1 | 14 MB |
| Legend (Rule of Cool) | 1 | 9 MB |
| Lost in a Fantasy World | 6 | 112 MB |
| Mecha Force | 2 | 3 MB |
| Microlite20 | 49 | 87 MB |
| Mini Gangs | 10 | 118 MB |
| Munchkin | 1 | 1 MB |
| Nuclear Renaissance | 1 | 24 MB |
| OSRIC | 3 | 214 MB |
| OneDice | 4 | 6 MB |
| OnePage | 341 | 927 MB |
| Otherworld | 3 | 44 MB |
| Pathfinder | 604 | 7891 MB |
| QUERP | 10 | 90 MB |
| Resources | 3 | 374 MB |
| Risus | 10 | 31 MB |
| Rogue Stars | 2 | 0 MB |
| Savage Worlds | 81 | 918 MB |
| Sixcess | 2 | 2 MB |
| Something Went Wrong | 1 | 0 MB |
| Songs of Blades and Heroes | 2 | 25 MB |
| Star Frontier | 44 | 237 MB |
| Star Wars | 15 | 266 MB |
| Stars Without Number | 14 | 15 MB |
| Storymasters Tales | 3 | 563 MB |
| Strongsword | 6 | 277 MB |
| The Hero's Journey | 1 | 23 MB |
| The One Ring | 39 | 679 MB |
| Tiny D6 | 42 | 223 MB |
| Traveller | 3 | 17 MB |
| Warhammer Diskwars | 4 | 78 MB |
| vs Monsters | 3 | 4 MB |

