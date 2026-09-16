# Phase 0 research: Commit-back path for accepted generated content

No `NEEDS CLARIFICATION` markers remain in spec.md's Technical Context — the three decisions
below were resolved during specification (recorded there as Assumptions) and are restated here
with their rejected alternatives, per this document's own purpose.

## Decision: `sources.generated` is a sibling shape to the existing `{work, pages, licence,
path}` shape, gated by `generated: true`

**Decision**: `entity.validate_source` inspects a `sources[]` entry's `generated` field first. When
`generated is True`, it validates the new shape (`generated`, `mode`, `consumed`, all required,
no other field permitted) instead of the existing required-field set. When `generated` is absent
or falsy, behaviour is unchanged — the existing `{work, licence, path, pages?}` rules apply
exactly as before.

**Rationale**: issue #422 and spec.md FR-002 both require this to be additive, "in place of the
`{work, pages, licence}` shape a converted beat carries" for *that entry*, not a competing shape
replacing it repo-wide. A single `sources[]` list may in principle carry both an authored entry
(for a stub later hand-edited) and a generated one; gating per-entry on `generated: true` is the
only reading that keeps both live rather than forcing every entity's `sources[]` into one
vocabulary.

**Alternatives considered**:
- Add a new top-level frontmatter field (e.g. `generation: {...}`) alongside `sources` — rejected:
  spec.md FR-002 and the driving issue both specify the provenance lands inside `sources:`
  ("in place of" the authored shape), and `25-entities.md` already treats `sources` as the one
  place provenance lives.
- Require every entry in `sources[]` to be uniformly authored-or-generated for a given entity —
  rejected: nothing in `18-arcs-and-beats.md`/`25-entities.md` requires this, and it would forbid
  the case of a stub carrying an authored placeholder source alongside a later generated
  completion (out of scope to forbid).

## Decision: thread emission reuses `thread.new_thread`/`thread.touch` directly; threat emission
reuses `threat.promote` plus the same direct-imminence-mutation convention `threat.py` already
documents for an existing threat

**Decision**: `accept_result` takes two additional structured inputs beyond the `GenerationResult`
itself — a `thread_updates` list and reuses #421's own `threat_updates` list shape unchanged
(`generation_checks.py`'s `check_scale_drift`/`check_favourable_coincidence` already read this
field from the candidate) — and applies each entry by calling:
- `thread.new_thread(...)` for a `thread_updates` entry marked `action: "new"`.
- `thread.touch(existing_thread)` for one marked `action: "touch"`, where `existing_thread` is
  looked up in a caller-supplied `live_threads` mapping.
- `threat.promote(target_entity, threat_block, objective)` for a `threat_updates` entry whose
  `entity_id` is `None` (a new threat), where `target_entity` is looked up in a caller-supplied
  `live_entities` mapping by the entry's own `target_entity_id`.
- A direct `imminence`/`ambient` mutation on the existing threat-bearing entity dict (looked up
  the same way) for a `threat_updates` entry whose `entity_id` is not `None` — matching
  `threat.py`'s own documented convention that an imminence *change* to an existing threat has no
  dedicated function, "the caller ... simply lowers `imminence` on the entity dict it already
  owns" (`threat.py`'s module docstring, on fading; the same convention applies symmetrically to
  a rise).

**Rationale**: `thread.py` and `threat.py` are the two modules the driving issue names as "the
real module[s]" (confirmed by reading both in full — neither is a file called `campaign.py`).
Reusing `promote`/`new_thread`/`touch` directly, and mutating imminence the one way the module
itself documents doing it, is the only way to satisfy FR-013's "no new file, table, or field ...
separately from authored state" without inventing a fourth mutation path these two modules
deliberately don't have. `threat_updates`' shape is taken unchanged from #421 (not redefined) so
this feature and its sibling read the exact same structural contract off a candidate rather than
each inventing its own.

**Alternatives considered**:
- Add a dedicated `threat.apply_imminence_delta` function so every threat mutation this feature
  performs is a named function call — rejected: `threat.py`'s own docstring explicitly rules this
  out as a deliberate design choice ("Fading needs no dedicated function here... the caller simply
  lowers imminence"), and adding one now would be a second, competing convention for exactly the
  mutation the module already documents doing inline.
- Invent a new `thread_updates`-shaped-like-`threat_updates` field name reusing the exact same
  field names (`entity_id`, `imminence_delta`, ...) for threads too — rejected: threads and
  threats have materially different lifecycles (a thread is created or heat-touched; a threat is
  promoted onto an existing entity, or nudged), so a shared field vocabulary that means different
  things per row would be the "two documents describing one thing differently" fault class
  (CLAUDE.md's Recurring Faults #3) rather than the "no new field" concern FR-013 actually raises,
  which is about *persisted state*, not about a transient candidate-input contract.

## Decision: `accept_result` refuses to write (returns a rejection outcome) rather than raising,
symmetric with `reject_result`

**Decision**: both `accept_result` (when `result['checks']` is empty or carries any `reject`
entry) and `reject_result` (an explicit caller decline, regardless of `checks`) return a plain
`{"committed": False, "reason": ...}` dict — never an exception — and perform no I/O and no
thread/threat mutation before returning it.

**Rationale**: matches `generation.py`'s own convention (`GenerationRequestError` as a returned
value, not a raised exception) and `threat.py`'s report-don't-raise convention
(`validate_connections`). It also makes FR-015's "MUST NOT write anywhere" independently
verifiable by a test that calls the function and inspects the filesystem/state directly, rather
than needing to catch an exception first.

**Alternatives considered**:
- Raise a dedicated exception on rejection — rejected: breaks the established convention this
  codebase already uses for exactly this kind of outcome, and would force every caller into
  try/except for what is an ordinary, expected outcome (a candidate rejected by anti-inflation
  checks is not a programming error).
