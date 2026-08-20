# WFRP 1st edition — voice and structure

Source: *Warhammer Fantasy Roleplay* 1st edition core rules, 369pp, **image-only scan with
no text layer** — OCR'd locally at 200dpi (`--psm 3`, two-column aware). 360 of 369 pages
carry text; the remaining nine are full-page art and the blank inside cover.

This is the edition Neil holds in most affection, and it was mined for **register** more
than mechanics — 2e is a direct descendant and covers the rules
([wfrp-mechanics](wfrp-mechanics.md)). What 1e has that later editions lost is a voice.

---

## The voice — the thing worth stealing

1e describes its world in the register of a slightly weary civil servant who has seen the
paperwork. It is not grimdark posturing; it is bureaucratic, specific, dry, and all the
bleaker for it.

On the Coachman:

> "It is the Coachman's unenviable task to convey passengers and goods safely through all
> these hazards... **Few Coachmen stay in the job long enough to benefit from the Teamsters'
> Guild pension scheme**, and some take their skills into a life of adventuring."

On the Boatman:

> "...transporting passengers and goods from place to place and avoiding the unwelcome
> attentions of robbers **and Officials**."

Three things make that work, and Wyrd's `settings/reikland/voice.md` should encode all three:

1. **Institutions are named and mundane.** A Teamsters' Guild with a pension scheme.
   Toll-keepers. Officials with a capital O. The Old World is administered, and its horror
   is administered too.
2. **Danger is stated as an occupational hazard**, not a threat. Not "death stalks the
   roads" but "few stay in the job long enough to collect the pension."
3. **The joke is never at the setting's expense.** It is dry, not arch. The world is played
   entirely straight; the humour comes from how ordinary the awfulness is.

This is the corrective to the LLM failure mode in
[`../design/01-principles.md`](../design/01-principles.md) constraint 7. An inflating GM
writes "the road is fraught with peril." A 1e GM writes that the tolls went up again and the
last two coaches did not arrive.

---

## Fate points — 1e's original

Rolled at creation, and **race-weighted**, which later editions dropped:

| Race | Fate Points |
|---|---|
| Human | `D3 + 1` |
| Dwarf | `D3` |
| Halfling | `D4` |
| Elf | `D3 − 1`, minimum 1 |

The reasoning is in the fiction: *"The world is changing, Humanity is in the ascendant and
the other races are on the wane... the player who chooses to play a Human character has a
definite edge."* Fate is not a game balance dial; it is a statement about the age.

Function is as Wyrd already has it:

> "A character may expend a Fate Point in order to ignore a critical hit result which would
> otherwise have been fatal — the character is knocked unconscious rather than killed and
> **wakes up having been left for dead**, or is merely grazed by the killing blow. A
> character who falls off a cliff can expend a Fate Point in order to walk away unharmed —
> saved by a million-to-one chance such as a bush or a patch of exceptionally soft sand."

And the hard edge:

> "Once a character has spent a Fate Point, it is gone... once a character has run out, he or
> she can cheat death no longer."

Note 1e also allows Fate to be **gained and lost through divine intervention** — a hook Wyrd
should keep, since it makes the gods mechanically present without making them helpful.

---

## Career Classes and Career Exits — the lateral web

Characters begin in one of four **Career Classes** — Warrior, Ranger, Rogue, Academic — and
a **basic career** within it. Sixty-plus basic careers: Agitator, Alchemist's Apprentice,
Artisan's Apprentice, Bodyguard, Muleskinner, Noble, Outlaw, Outrider, Pedlar, Pharmacist,
Physician's Student, Pilot, Pit Fighter, Prospector, Protagonist, Raconteur, Rat Catcher,
Roadwarden, Runner, Trader, Trapper, Troll Slayer, Tunnel Fighter, Watchman, Wizard's
Apprentice, Woodsman…

The mechanism that matters is **Career Exits**: every career lists the specific careers you
may move into next.

> Boatman → *Outlaw · Seaman · Smuggler*

So advancement is a **directed graph**, not a ladder. You do not become "better"; you become
*something else*, and only the somethings your history actually permits. A Boatman cannot
become a Physician; he can become a Smuggler, because that is what the river offers a man who
knows boats and dislikes Officials.

This is the single most important structural idea in 1e for Wyrd, and it is stronger than
Warlock's flat basic/advanced split. `settings/reikland/careers.yaml` should carry **exits**
as first-class data, because:

- it makes advancement *characterful* rather than optimal — the graph is a biography
- it constrains the GM as much as the player: Wyrd cannot hand out a career that isn't a
  legal exit from where the character has actually been
- it gives the succession rules in [`../design/05-campaign.md`](../design/05-campaign.md) a
  natural source of successor plausibility — an NPC's career history says what they could
  credibly become

Warlock's careers (which are 1e's careers, lightly renamed) can be wired into this graph
directly.

---

## Insanity in 1e

Present and cheaper than 2e's: insanity points accrue from specific triggers, including
mundane ones — witnessing certain horrors, but also failure and duress. Handled under
*"Poison, Disease and Insanity"*, which tells you everything about how the edition regards
mental injury: it is in the same chapter as rot and venom, a thing that happens to bodies.

Wyrd already takes 2e's more developed version. What 1e adds is the *framing* — madness as
an ailment among ailments, treated by the same people who treat gangrene, and about as
successfully.

---

## What to do with this

- **`settings/reikland/voice.md`** should quote the Coachman and Boatman entries directly as
  its register target, along with the three rules above.
- **`careers.yaml`** should carry Career Exits as a graph.
- **Fate** should be race-weighted in the Reikland setting, per 1e, with the in-fiction
  justification intact.
- The OCR text is retained locally at
  `scratchpad/wfrp/v1-core.txt` (1.4 MB) — not committed, since it is a
  scan of a copyrighted book. Re-derive with `ocr2.sh` if needed.

## Operational note

The OCR run is worth recording. Naively parallelising `tesseract` produced **one page in six
minutes at load 17** on four cores: tesseract 5 uses OpenMP and grabs *every core per
process*, so four workers spawned sixteen threads and thrashed. With `OMP_THREAD_LIMIT=1` and
four workers, the same job runs at **~7.9 seconds per page**, finishing in about fifteen
minutes — a ~35× difference from a single environment variable.
