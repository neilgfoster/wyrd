# Phase 0 Research: Related settings — shared worlds and kindred tone

No NEEDS CLARIFICATION markers remain in the Technical Context — this is a schema-and-checker
addition inside a well-established repo pattern (`docs/design/*.md` + `settings.yaml` +
`tools/check_*.py`), so nothing needed external research. The decisions below record the choices
made and why, since they are exactly the kind of design fork the issue asked to have weighed
rather than assumed.

## Decision: relation storage shape

**Decision**: A new top-level `relations:` list in `settings.yaml`, sibling to the existing
`settings:` list. Each entry is a flat mapping: `a`, `b` (setting ids), `kind`
(`same-world` | `kindred-tone`). The existing `group:` field on a setting entry is retired in
favour of `same-world` relations — a setting's memberships in a shared world become derivable by
scanning `relations:` for entries naming it, rather than living as a second, independent list.

**Rationale**: `CLAUDE.md`'s own recurring fault (drift between two lists of one fact) is exactly
what would happen if `group:` (same-world) stayed on the setting entry while a new kindred-tone
list lived elsewhere. One list, one entry shape, one place a relation is recorded — satisfies FR-001
and FR-002's "single place" requirement outright, and keeps the existing restricted-subset YAML
parser (flat `- key: value` mappings, no nested lists) usable without extending it to parse nested
sequences.

**Alternatives considered**:
- *Per-setting `kin: [...]` field on each setting entry.* Rejected: this is exactly the
  two-places problem — a relation between A and B would need to be written once under A and, to
  stay consistent, again under B; the existing catalogue-drift class this repo has already been
  burned by twice (settings.yaml stale on two separate axes, per `check_settings_catalogue.py`'s
  own docstring).
- *Two separate lists (`same_world_groups:`, `kindred_settings:`).* Rejected: the issue explicitly
  says a relation declared in two places is two lists of one fact; two different top-level lists for
  the two relation *kinds* isn't the same failure mode as duplicating one relation, but it does
  needlessly duplicate the parsing/validation logic for what is structurally identical data (a pair
  plus a kind). A single `relations:` list with a `kind:` field carries the same information with one
  parser path and one consistency check, and reads as one coherent concept (kinship) rather than two
  unrelated catalogue sections.
- *Deriving same-world groups from repo-name convention* (`wyrd-setting-wh40k-*` implies group
  `wh40k`). Rejected: the issue's own "Current state" section calls this out as exactly the current,
  broken state — "the only evidence... is in repository names." A convention is not a declaration
  and can't be validated for correctness the way an explicit relation can.

## Decision: symmetry representation

**Decision**: A relation is recorded once, as an unordered pair (`a`/`b` field names carry no
directional meaning), and is read as implying both directions. The checker treats `{a: X, b: Y}`
and `{a: Y, b: X}` as the same relation and flags a duplicate if both appear.

**Rationale**: FR-004 requires that declaring A related to B not silently omit that B is related to
A. Storing one directionless entry per pair makes this true by construction — there is no second
statement that could go stale relative to the first.

**Alternatives considered**: Storing the relation on both settings' own entries (two statements,
checked for agreement). Rejected for the same drift reason `group:` retirement rejects it.

## Decision: assert vs. derive kinship

**Decision**: Kinship is always author-asserted, never derived from the tone contract.

**Rationale**: Already the spec's FR-003 and the plan's Constitution Check — restated here because
it is the one fork the issue asked to be weighed explicitly. The tone contract's seven dimensions
(`prophecy`, `victory`, `power_curve`, `scope`, `scale_drift`, `mortality`, `register`) are each a
small closed set of categorical values (see `docs/design/24-authoring-a-setting.md` and ADR 0004),
not a scalar. Any automatic "kindred" threshold would require inventing a distance function over a
mixed categorical space — precisely the kind of fabricated precision `docs/design/27-tooling.md`'s
deterministic-over-inference principle warns against when a script would be *asserting* a metric
that has no principled derivation, not *checking* one that already exists. Author judgement, backed
by a checker that validates the declaration's *structure* (not its truth), is the honest fit.

## Decision: provenance stamp shape for a borrowed entity

**Decision**: A borrowed entity carries `borrowed: {from_setting: <id>, from_entity: <id>,
relation: same-world|kindred-tone, on: <date>}`, documented in `docs/design/24-authoring-a-setting.md`
as a schema entities MUST carry when they originate from a related setting rather than from source
material — parallel to, and distinguishable from, the existing `converted: {rules, on}` stamp used
for entities converted from a published system.

**Rationale**: FR-006 requires the same provenance discipline already required of conversion. Reusing
the existing `converted:` stamp's shape (a small mapping recorded on the entity) rather than inventing
a new provenance mechanism keeps the two provenance stories consistent — a reader who understands one
understands the other. Naming the relation type on the stamp (`relation:`) lets a later reader tell
at a glance whether the entity was carried over as-is (same-world) or reskinned (kindred-tone)
without re-consulting `settings.yaml`.

**Alternatives considered**: Reusing `converted:` itself for borrowed entities (treating the source
setting as if it were a "published system"). Rejected: it would conflate two different provenance
claims — "derived from someone else's book" versus "derived from a sibling Wyrd setting" — and FR-007
requires that borrowing with no declared kinship fall back to *ordinary conversion*, which only makes
sense if borrowed-with-kinship and converted-from-source are distinguishable stamps.
