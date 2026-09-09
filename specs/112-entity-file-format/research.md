# Phase 0 Research: Entity file format engine support

## Decision: Reuse `state.py`'s existing frontmatter/body split, don't reimplement it

**Decision**: `entity.py` calls `state.parse_entity`/`state.dump_entity`/`state.save_entity`/
`state.load_entity` for the file-level read/write (frontmatter + body, atomic write), and adds
validation and cross-entity resolution (containment, connections) as a layer above that.

**Rationale**: These functions already exist in `engine/wyrd/state.py` (added for the player
character and companion records) and already implement exactly the split
`docs/design/25-entities.md` describes ("a markdown file with YAML frontmatter... the body is the
prose"). Reimplementing them in `entity.py` would duplicate the restricted-YAML reader/writer and
risk the two drifting.

**Alternatives considered**:
- A separate frontmatter parser in `entity.py`: rejected — pure duplication of working code, and
  `docs/adr/*` has no decision requiring entity I/O to be self-contained; `state.py` already sits
  in `engine/`, so importing it does not cross the `engine`/`tools` boundary `CLAUDE.md` protects.
- Extending `state.py` itself with schema validation: rejected — `state.py`'s own docstring commits
  it to a deliberately minimal, format-only role; folding in the ten-type schema would grow it well
  past that stated scope and entangle chronicle-state concerns with entity-schema concerns.

## Decision: Validation is schema-shape checking, not semantic/content checking

**Decision**: `entity.py` validates field *presence*, *closed-set membership* (type, status), and
*shape* (e.g. `sources` is a list of mappings with `work`/`pages`/`licence`) — it does not validate
free-text content (e.g. that `objective.wants` reads sensibly) or evaluate conditions (`requires`,
`entry`/`exit` triggers).

**Rationale**: `docs/design/25-entities.md` is a data-format specification; the acceptance criteria
in issue #305 ask for round-tripping and rejecting *malformed* records, not for interpreting
narrative content. Condition evaluation belongs to whichever module consumes it at play time (e.g.
the arc/beat epic, #299) — this feature only has to preserve the text faithfully.

**Alternatives considered**: Validating `requires`/`entry`/`exit` as some structured expression
language — rejected as premature; no design document specifies such a grammar, and inventing one
here would be scope creep beyond what #305 asks for.

## Decision: Containment cycle detection walks each entity's `parent` chain once

**Decision**: Build a `dict[id, parent_id | None]` from the loaded set, then for each entity walk
its `parent` chain with a visited-set, raising on repetition. This is O(n) amortized total (each
edge is walked at most a constant number of times across all entities) and needs no external
library.

**Rationale**: Simple, deterministic, and matches the "check rather than assert" principle
(`docs/design/27-tooling.md`) — a straightforward graph-cycle check computed in code, not asserted.

**Alternatives considered**: Topological sort via Kahn's algorithm — equivalent correctness,
marginally more code for no benefit at this scale (hundreds to low thousands of entities).

## Decision: `[[wikilink]]` resolution strips the bracket syntax and checks membership only

**Decision**: A field value written as `[[the-old-quarter]]` (or a list of such) is read as the
literal string `the-old-quarter`; resolution to "does this id exist" is checked against the loaded
entity set at load time and reported (not silently dropped) when absent.

**Rationale**: Matches `docs/design/25-entities.md`'s stated linking convention and ADR 0011
(wikilinks in data, not prose). Reference resolution is intentionally shallow here — it answers
"is this id known", not "load the full target entity eagerly" — because eager loading would force
this feature to also own load-order/dependency concerns that belong to whichever caller assembles
a working set of entities.

**Alternatives considered**: Eager resolution to the full target entity object — rejected as
out of scope; the caller (e.g. a future session/campaign module) already has the loaded set and
can look up by id itself once this feature reports which ids exist.
