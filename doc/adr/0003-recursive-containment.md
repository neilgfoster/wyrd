# ADR 0003 — Containment is recursive; the beat is the only leaf

**Status:** accepted 2026-08-21

## Context

Wyrd needs to describe stories, places and organisations at many scales — a campaign
containing adventures containing scenes; a region containing a city containing a district;
an institution containing an order containing a cell.

The obvious approach is a **fixed ladder**: name the levels, and give each its own entity
type.

## Decision

**Containment is recursive.** Three types — `place`, `organisation`, `arc` — are containers
that hold their own kind to any depth ([`../27-entities.md`](../design/27-entities.md)). `scale` is a
human-readable label, never a structural constraint.

Only the **beat** is structurally special, and not because of its position in the tree:

> **Arcs organise. Beats are played.**

An arc of one beat is still an arc; a beat is never a container.

Alongside containment, a second and independent relation: **connection**, a free graph of
conditional links. Containment is a strict tree; connection may loop.

## Alternatives rejected

**A fixed ladder** — campaign → adventure → scenario → beat, each a type. Tried, and it did
not survive contact with real material: some published adventures are a single scene, some
campaigns nest three deep, and some scenarios contain sub-scenarios. Every such case forces
an arbitrary decision about which rung something occupies, and the answer changes nothing
except how hard it is to find later.

It also caused a concrete contradiction. Two design documents ended up declaring **different
ladders** — one five rungs, one four — and neither was wrong by its own lights.

**Making the beat merely an arc with no children.** Tempting, since it would leave one type
instead of two. Rejected because it loses a real distinction: an arc has entry and exit
conditions and organises other things; a beat is where play happens. Collapsing them would
mean either arcs acquire play semantics they do not need, or beats acquire containment they
must not have.

## Consequences

- **Recombination becomes trivial**: any arc fits inside any arc, because they are the same
  shape.
- Entry and exit conditions exist at **every** level, so thread-matching can select a whole
  campaign or one situation out of it ([`../28-arcs-and-beats.md`](../design/28-arcs-and-beats.md)).
- An arc that has never been decomposed is still **selectable**, which is what makes lazy
  conversion possible.
- Entity types fell from twelve to ten, because scenario, adventure and campaign became one
  type wearing different labels.
- `wyrd doctor` must check that containment stays acyclic; nothing enforces it structurally.
