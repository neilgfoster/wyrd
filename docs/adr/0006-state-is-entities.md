# ADR 0006 — State is entities; there is no second storage model

**Status:** accepted 2026-08-21
**Depends on:** [0003](0003-recursive-containment.md)

## Context

A chronicle holds two apparently different kinds of thing: the **world** — characters,
places, organisations — and the **player's state** — their character, companions, threads,
threats.

The obvious split is to store them differently: a vault of entity files for the world, and a
handful of typed state files for whatever the engine reads every session.

## Decision

**Everything is an entity.** A markdown file with YAML frontmatter, in one of ten types
([`../27-entities.md`](../design/27-entities.md)). The player's character is a `character` with
`role: player`. Threads are entities. A threat is an *aspect* on an entity.

What differs is not format but **where a file lives and when it loads**
([`../19-state.md`](../design/19-state.md)). Only `chronicle.yaml` is not an entity, because it
describes the chronicle rather than anything in the world.

The always-loaded tier is chosen **by query, not by manifest** — companions are
`role: companion` with `status: with-party`, hot threads are `heat >= 3`.

## Alternatives rejected

**Separate typed state files** — `pc.yaml`, `party.yaml`, `threads.yaml`, `threats.yaml`.
This is what was written first, and it survived several review passes before the
contradiction surfaced: two design documents described the same chronicle **two different
ways**, and six others referenced the losing one. Nothing caught it because both readings
were internally coherent.

The deeper fault is that the split is arbitrary. A companion is a character; a character the
player has not met is also a character; the only real difference is how often each is read.
Encoding *how often* as *what format* guarantees the two drift apart.

**A manifest for the always-loaded tier.** Rejected because a manifest is one more thing that
must be kept true. A query cannot fall out of date.

## Consequences

- One parser, one validator, one set of invariants.
- The party is a query, not a file — a companion leaving is a status change, not a move
  between documents.
- Chronicle overlays work uniformly, including promoting a bystander into a nemesis
  ([`../18-campaign.md`](../design/18-campaign.md)).
- `thread` had to become a tenth entity type. It was used in fifteen documents while absent
  from the type list — the same class of fault, found the same way.
- Everything is an Obsidian vault by construction rather than by effort.
