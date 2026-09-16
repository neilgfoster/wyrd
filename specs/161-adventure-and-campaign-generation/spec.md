# Feature Specification: Adventure and campaign generation

**Feature Branch**: `161-adventure-and-campaign-generation`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Specify adventure and campaign generation (issue #99) — a generation
request's input contract for every named scale (beat, arc, campaign spine), anti-inflation
constraints as checkable rules, a generated arc's commit-back path that does not fork state from
the threat/thread machinery, and model tier per generation step. Must also cover invocation at
setting-authoring time (no chronicle state), not only during live play."

## Clarifications

### Session 2026-09-16

- Q: For a committed generated beat/arc, where does per-claim provenance (library/web/invented)
  live — a new structured field per claim, or a prose-level convention? → A: a prose-level
  convention inside the body text, the same inline labelling `create-setting`'s own governing rule
  already uses (e.g. "invented, per Phase 1 Q3"), not a new structured field per claim. This keeps
  the commit-back schema's only structural addition to `sources.generated` (FR-012), matching
  SC-003's "exactly one new field" claim.

## User Scenarios & Testing *(mandatory)*

<!--
  This is a design/spec-only capability: its "user" is a GM session (live play) or a
  setting-authoring session (create-setting's Phase 1 Q3 path), never a human filling a form.
  Each story below is a distinct invocation shape the generation contract must support end to
  end, from request to committed-back state.
-->

### User Story 1 - Generate the next beat during live play (Priority: P1)

A running chronicle has live threads, an active threat, and a party danger rating. Nothing in the
setting's stub inventory or the chronicle's own history offers a beat that fits what the player
just did, so the GM session requests one be generated rather than selected. The generated beat
must read like it belongs — entry/exit conditions that mesh with the live threads it consumed,
danger scaled to the party, and no invented fact that contradicts established state.

**Why this priority**: This is the case the issue exists for — a chronicle that would otherwise
stall because the library ran out of matching stubs. Without it, "select the next beat" silently
degrades to "hope the library covers this," which is exactly the failure #99 was raised against.

**Independent Test**: Given a chronicle state with at least one live thread and one active threat,
request beat-scale generation; verify the returned beat's `entry.requires_threads` names only
threads that were live in the request, its `danger` is within the danger-scaling band for the
stated party, and no named character or fact appears that was not either supplied in the request
or drawn from the setting's own entity store.

**Acceptance Scenarios**:

1. **Given** a chronicle with two live threads and no active threat, **When** beat-scale
   generation is requested, **Then** the generated beat's `entry.requires_threads` is a non-empty
   subset of those two threads and its `exit.emits_threads` references at most one genuinely new
   thread.
2. **Given** a chronicle with an active threat at imminence 4, **When** beat-scale generation is
   requested naming that threat, **Then** the generated beat's `cast`/`place` entities are drawn
   from the threat's own `clues` list or the chronicle's existing entities, never invented outside
   both.

---

### User Story 2 - Generate a campaign spine with no chronicle yet (Priority: P2)

A setting with a sparse or absent published-adventure catalogue is being authored. The
create-setting skill's Phase 1 Q3 permission ("invent original material with no basis in the
library, the web, or stated direction, as long as it stays consistent with established tone and
facts") has been granted, and the setting needs at least one top-level arc to be playable at all.
There is no chronicle, no live threads, no threat state — only the setting's own `voice.md`, tone
contract, and whatever `entities/` already exist.

**Why this priority**: without this mode, a setting with little source material has no path to a
playable campaign spine at all — the generation capability the engine already needs for live play
is the same mechanism this gap needs, and specifying it as a second, separate thing would be the
two-list drift this project's own conventions warn against.

**Independent Test**: Given a setting with `setting.yaml`, `voice.md`, and zero or more
`entities/` files, and Q3 explicitly granted, request campaign-spine-scale generation with no
chronicle reference; verify the result is a top-level arc entity consistent with the declared tone
contract, every invented claim in it is labelled `invented, per Phase 1 Q3` and traceable to no
contradiction against existing entities, and the request is rejected outright if Q3 was not
granted.

**Acceptance Scenarios**:

1. **Given** a setting with no chronicle and Q3 not granted, **When** campaign-spine-scale
   generation is requested with no other grounding, **Then** the request is refused with a
   structured reason naming the missing permission, and nothing is written.
2. **Given** the same setting with Q3 granted, **When** campaign-spine-scale generation is
   requested, **Then** the resulting arc's tone-sensitive fields (whether anything is fated about
   a future player character, whether stakes are personal or regional, mortality register) match
   the setting's declared `tone:` block exactly, and every invented name or fact in it carries the
   `invented, per Phase 1 Q3` label.

---

### User Story 3 - Generate an arc that nests beats and commits back as fact (Priority: P3)

An arc-scale request is made mid-chronicle: the current era's live threads suggest a
multi-beat situation rather than a single scene. The GM session requests arc-scale generation,
receives an arc with two or three child beats (some possibly left as unconverted stubs), and once
play actually uses it, the arc and its beats persist in the setting/chronicle exactly as an
authored, converted arc would — consuming and updating the same thread and threat records live
play already reads and writes, never a separate "generated" ledger.

**Why this priority**: this is what proves the commit-back path holds at the scale where it is
most tempting to fork — an arc has to update `threads:` (consuming some, emitting others) and
possibly a threat's `clues` progress, and a parallel bookkeeping trail here would silently
duplicate the exact machinery #99's acceptance criteria requires it not fork from.

**Independent Test**: Given a chronicle with live threads, request arc-scale generation; after the
arc is accepted, verify the setting/chronicle's thread list and threat state show only the
ordinary write path (`campaign.py`'s existing consume/emit and threat-effect application) with no
new file, field, or table introduced to hold "generated" state separately from authored state.

**Acceptance Scenarios**:

1. **Given** an arc-scale generation request naming two live threads, **When** the returned arc is
   accepted into the chronicle, **Then** those two threads are marked consumed and any
   `exit.emits_threads` on the arc or its beats are appended to the same `threads:` list authored
   content uses — not a separate structure.
2. **Given** a generated arc whose entry names an active threat, **When** the arc is accepted,
   **Then** the threat's own `clues` and `imminence` fields are read and (if the arc's fiction
   advances them) written through the same threat-state path threat activation already uses.

### Edge Cases

- What happens when a generation request at any scale cannot find enough live state (no threads,
  no threat, and — in live play — no matching setting entities) to ground a result at all? The
  request MUST fail structurally (a reported reason, nothing written) rather than falling back to
  invention beyond what the request's mode permits.
- How does the system handle a setting-authoring-time request where Q3 was granted but the
  setting has *some* `entities/` — must the generated content check consistency against them, or
  is a blank slate assumed? It MUST check: Q3's own governing rule (create-setting's Phase 1) is
  gated on consistency with *existing* facts, not just tone, so any already-established entity is
  binding on a setting-authoring-time request exactly as chronicle state is binding on a live-play
  one.
- What happens when a campaign-spine-scale request is made *during* live play, not at
  setting-authoring time? It MUST behave as User Story 3 (live-play, arc-scale, top-level) — a
  campaign spine is a top-level arc, not a different mechanism (see FR-002) — and MUST NOT invoke
  the Q3 permission, which is scoped to setting-authoring time only.
- What happens when an anti-inflation rule and a request's own tone contract would otherwise
  disagree — e.g. a request asks for danger scaled far above what `scale_drift: suppressed`
  permits? The tone contract wins; the request is narrowed to what it permits and the narrowing is
  reported, never silently honoured.

## Requirements *(mandatory)*

### Functional Requirements — the generation-request input contract

- **FR-001**: The system MUST define one generation-request shape shared by all three named
  scales (beat, arc, campaign spine), varying only in which fields are required, per FR-003 —
  never three independent request shapes, so a caller can treat scale as a parameter rather than a
  different capability.
- **FR-002**: A campaign-spine-scale request MUST be specified as a request for an **arc entity
  with no `parent`** ([`25-entities.md`](../../docs/design/25-entities.md)'s containment model —
  `parent` is the only containment field, and its absence is what makes an arc top-level) whose
  `scale` label is `campaign` (one of the arc scale labels `25-entities.md` already recognises:
  `campaign | adventure | scenario | situation`) — not a fourth structural type. This follows
  directly from recursive containment ([ADR 0003](../../docs/adr/0003-recursive-containment.md)):
  `scale` is a label, never a structural constraint, so "campaign spine" names *where in the
  containment tree, and under which existing label,* the requested arc sits, not a different shape
  of thing. `19-campaign.md`'s "Top-level arcs" section is what binds this further: each such arc
  must end with a real change to the world, recorded in the overlay.
- **FR-003**: The request contract MUST carry, for every scale:
  - `scale`: `beat` | `arc` | `campaign-spine` (a request-level convenience name for "an `arc`
    request with no `parent` and `scale: campaign`," per FR-002 — this is a request-shape alias,
    never a fourth entity `scale` label of its own)
  - `mode`: `live-play` | `setting-authoring` (FR-004/FR-005 define what each requires and
    permits)
  - `setting_ref`: the setting this request is grounded in
  - `written_for`: the party-size scaling input beats already carry
    ([`18-arcs-and-beats.md`](../../docs/design/18-arcs-and-beats.md)) — required for `beat` and
    `arc`, absent for a `campaign-spine` request made in `setting-authoring` mode (no party yet)
  - `tone_contract`: the setting's declared `tone:` block (always present; both modes read it)
- **FR-004**: A `live-play` request MUST additionally carry: the chronicle's live `threads:` list
  (by id and heat), the active `threat` blocks in scope (by entity id, imminence, and clue
  progress), the current danger rating, and the current era. Generation in this mode MUST treat
  these as the only permitted grounding beyond the setting's own entity store — it MUST NOT invent
  a thread, threat, or fact these do not support.
- **FR-005**: A `setting-authoring` request MUST additionally carry: the setting's `voice.md`
  register, the setting's existing `entities/` (whatever already exists — possibly none), and an
  explicit `invention_permitted: true` flag that MUST be present and true, and MUST be traceable
  by the caller to the create-setting skill's Phase 1 Q3 grant, or the request is rejected before
  any generation runs (see Edge Cases). This mode carries no `threads`, no `threat`, and no danger
  rating — there is no chronicle yet — and generation MUST NOT reference any of the three.
- **FR-006**: The two modes MUST differ *only* in which state exists to consume (FR-004 vs
  FR-005), never in which anti-inflation rules bind the output (FR-007 through FR-011 apply
  identically to both) — this is the explicit variant relationship the issue's own comment thread
  calls for, not two independent permission models.

### Functional Requirements — anti-inflation constraints, stated as checkable rules

- **FR-007**: Every named character, faction, or place appearing in generated content MUST be
  either (a) already present in the setting's `entities/` store, (b) named in the request's
  `threads`/`threat` state (`live-play` mode), or (c) newly invented and labelled
  `invented, per Phase 1 Q3` inline in the body prose (`setting-authoring` mode only, and only
  when FR-005's flag is set) — see Clarifications, prose-level labelling, not a structured field.
  A generated result containing any other named entity MUST be rejected before being offered for
  acceptance — this is a mechanical membership check against a closed list, not a judgment call.
- **FR-008**: Generated content MUST NOT set a `threat` block's `known_to_player` field, or any
  field read by `01-principles.md`'s `prophecy` tone value, to a state the request's own
  `tone_contract.prophecy` forbids. Under `prophecy: forbidden` a generation result naming a
  destiny, hidden bloodline, or prewritten fate for a player character MUST be rejected outright,
  checkable by a closed-vocabulary field comparison, not by re-reading the prose.
- **FR-009**: A generated arc or beat's `danger` value MUST fall inside the band the danger-scaling
  rule ([`03-rules.md`](../../docs/design/03-rules.md) §7, formalised in
  [ADR 0024](../../docs/adr/0024-a-party-is-worth-less-than-its-head-count.md)) computes for the request's stated
  `written_for` and current danger rating — never above it regardless of narrative ambition. This
  is the same arithmetic check `wyrd doctor`-class tooling already performs elsewhere, applied to
  a generation result before acceptance rather than after play discovers the mismatch.
- **FR-010**: Under `tone_contract.scale_drift: suppressed`, a generated arc or beat MUST NOT
  raise a threat's `imminence`, widen a threat's `ambient` cost beyond the requesting entity's
  existing reach, or introduce a new threat whose `connection` is anything other than a specific,
  already-established tie to the player or a companion (`19-campaign.md`'s "Threats are personal"
  — no threat with no connection). A candidate violating this MUST be rejected or automatically
  narrowed (its escalation reduced to what the tone contract permits) — the request's own
  `mode`/`tone_contract` combination decides which, and either outcome MUST be reported, never
  silently honoured as asked.
- **FR-011**: Coincidence introduced by generated content MUST NOT resolve in the player's favour
  by default — the same rule `01-principles.md` principle 4 states for live narration, restated
  here as a check against generated output: a generated beat/arc whose entry or exit conditions
  depend on an unrequested, unearned favourable coincidence (an ally who happens to be present, a
  clue that happens to surface unprompted) MUST be rejected unless the request's own state
  (FR-004/FR-005) already supports it.

### Functional Requirements — the commit-back path

- **FR-012**: A generated beat or arc, once accepted, MUST be written using the exact same entity
  schema and `status` lifecycle (`stub` → `drafted` → `complete`) authored content already uses
  ([`18-arcs-and-beats.md`](../../docs/design/18-arcs-and-beats.md)) — landing as `drafted`, since
  it did not come from decomposing a stub. Its `sources:` field MUST record provenance as
  generated rather than extracted: `{generated: true, mode: live-play|setting-authoring,
  consumed: [<thread/threat ids the request supplied>]}` in place of the `{work, pages, licence}`
  shape a converted beat carries — this is the one schema difference, and it is additive, not a
  parallel structure.
- **FR-013**: Accepting a generated beat or arc MUST consume and emit threads through the same
  `threads:` list and the same threat `clues`/`imminence` fields that authored play already
  reads and writes (`campaign.py`, per `docs/design/27-tooling.md`'s architecture) — no new file,
  table, or field may be introduced to hold "generated" thread or threat state separately from
  authored state. This is the acceptance criterion the issue states explicitly, and it is
  verifiable by inspecting the write path generation's acceptance step calls: it MUST be the
  identical function calls a beat's `exit.emits_threads` and a threat's activation already use,
  not a parallel one.
- **FR-014**: Once a generated beat or arc is accepted and reaches `status: complete` by being
  played, it is indistinguishable in every respect but `sources:` provenance from a converted
  beat or arc — `29-evolution.md`'s "the past is a fact" principle applies to it identically:
  once played, it is never regenerated, retconned, or silently altered by a later, better
  generation pass.
- **FR-015**: A generated result that is **not** accepted (the caller declines it, or an
  anti-inflation check in FR-007–FR-011 rejects it) MUST NOT be written anywhere — no draft file,
  no partial entity, no thread mutation. Generation is side-effect-free until acceptance.

### Functional Requirements — model tier per generation step

- **FR-016**: Selecting which live threads/threats a generation request should be grounded in
  (matching request state against the setting's `entities/` store and existing stub inventory)
  MUST run with no model — the same deterministic thread/hook matching
  [`18-arcs-and-beats.md`](../../docs/design/18-arcs-and-beats.md) already specifies for stub
  selection, per `27-tooling.md` §1's decision procedure (single correct answer given the state).
- **FR-017**: Computing a generated result's structural fields — `danger` (FR-009), whether an
  escalation is within `scale_drift` bounds (FR-010), `written_for` scaling, and the `status`/
  `sources:` bookkeeping (FR-012) — MUST run with no model, for the same reason: each has a single
  correct answer given the request's state, and `27-tooling.md` §5's own table already places
  arithmetic, lookup, and validation in the no-model column.
- **FR-018**: Assembling a generation result's entry/exit *shape* (which threads it should consume
  and emit, structurally) and pacing (how many child beats an arc-scale request should decompose
  into, at what length) MUST run at Haiku tier — `27-tooling.md` §5 names exactly this class
  ("matching arc hooks against live threads," "mechanical language work with a right answer") as
  Haiku's job, distinct from the no-model arithmetic above because it involves matching natural-
  language hook text rather than pure computation, and distinct from narration below because it
  has a checkable right answer.
- **FR-019**: Writing the generated beat's or arc's prose — the "what is true, who wants what, and
  what happens if nobody intervenes" body text ([`18-arcs-and-beats.md`](../../docs/design/18-arcs-and-beats.md)) —
  and any invented name/detail under FR-005's Q3 permission MUST run on the capable model
  (Sonnet/Opus tier), per `27-tooling.md` §5's explicit statement that narration, voice, and
  judgement about what a result means are "the one place not to economise." This is the only step
  in the generation pipeline that runs on the capable model.
- **FR-020**: The model tier for each generation step (FR-016–FR-019) MUST be fixed by the request
  `scale`/step, never chosen at runtime by the generating session — the same discipline
  `27-tooling.md` §5 already applies to the rest of the CLI surface: a step's tier is a property
  of what kind of work it is, verifiable by inspection, not a judgment call made per invocation.

### Key Entities *(include if feature involves data)*

- **Generation request**: the input contract of FR-001–FR-006 — `scale`, `mode`, `setting_ref`,
  `written_for` (where applicable), `tone_contract`, plus mode-specific state (`threads`/`threat`/
  `danger`/`era` for `live-play`; `voice`/existing `entities/`/`invention_permitted` for
  `setting-authoring`). Never persisted on its own — it exists only for the duration of one
  generation call.
- **Generation result**: an unaccepted candidate beat or arc, shaped exactly like the entity it
  would become (FR-012) plus a `checks:` report of which FR-007–FR-011 rules were evaluated and
  their outcome, so a rejection is explainable rather than silent. Held only until accepted or
  discarded (FR-015) — never itself a persisted entity type.
- **Committed arc/beat**: an ordinary `arc`/`beat` entity ([`25-entities.md`](../../docs/design/25-entities.md))
  once accepted, distinguished from an authored one only by its `sources:` provenance shape
  (FR-012). Consumes and mutates `threads:` and `threat` state through the existing paths (FR-013),
  never a parallel structure.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every one of the three named scales (beat, arc, campaign spine), the input
  contract fully determines what state must be supplied before generation runs — verifiable by a
  reviewer checking off FR-003 through FR-005 field-by-field against the scale being requested,
  with zero fields left ambiguous as to which mode requires them.
- **SC-002**: Every anti-inflation constraint (FR-007–FR-011) is stated as a closed-vocabulary or
  arithmetic check a script could evaluate against a generation result, with zero constraints
  expressed only as prose intention ("keep it grounded," "avoid escalation") — verifiable by
  confirming each FR names a specific field, comparison, or existing table it checks against.
- **SC-003**: The commit-back path (FR-012–FR-015) introduces exactly one new field
  (`sources.generated`) to the existing entity/thread/threat schema and zero new files, tables, or
  parallel state structures — verifiable by diffing the specified schema against
  `18-arcs-and-beats.md`/`19-campaign.md`'s existing shapes.
- **SC-004**: Every generation step (FR-016–FR-019) is assigned exactly one of the three tiers
  `27-tooling.md` §5 defines (no-model, Haiku, capable), with the capable-model tier used for
  prose/invention only — verifiable by auditing the four FRs against that table, the same audit
  method `27-tooling.md` §5 itself already prescribes for the rest of the CLI surface.
- **SC-005**: A `setting-authoring`-mode request made without `invention_permitted: true` never
  produces written output — verifiable by the FR-005/FR-015 rejection path alone, with no
  generation step downstream of it ever reached.

## Assumptions

- This is a specification-only deliverable, per the driving issue's own Definition of Done: the
  artefacts this feature produces are `spec.md`, `plan.md`, `data-model.md`, and `contracts/` under
  `specs/161-adventure-and-campaign-generation/` — no application code, no new CLI verb
  implementation. A future feature implements what this one specifies.
- "The capable model" and "Haiku" name the tiers `27-tooling.md` §5 already defines; this spec
  does not introduce a fourth tier or rename the existing two.
- The `create-setting` skill's Phase 1 Q3 gate is treated as already correctly specified by that
  skill (`wyrd-setting-template`'s `SKILL.md`) — this feature's `setting-authoring` mode consumes
  that permission as given, and does not re-specify how Q3 itself is asked or recorded.
- Danger-scaling arithmetic (FR-009) and threat activation (FR-010, FR-013) are treated as already
  specified by their own design documents/ADRs; this feature reuses them by reference rather than
  restating their formulas.
- No new persisted entity type is introduced (Key Entities above are either transient
  request/result shapes or ordinary existing entity types); this keeps the ten-type model of
  [`25-entities.md`](../../docs/design/25-entities.md) unchanged.
