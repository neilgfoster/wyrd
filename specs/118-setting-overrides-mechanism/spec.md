# Feature Specification: Setting Overrides Mechanism

**Feature Branch**: `118-setting-overrides-mechanism`

**Created**: 2026-09-10

**Status**: Draft

**Input**: User description: GitHub issue #316, "Setting overrides mechanism (disable, rename, retune, extend)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The engine publishes what a setting may override (Priority: P1)

A setting author needs to know, before writing `setting.yaml`, exactly which mechanisms may be
disabled, renamed, retuned or extended. Today that set exists only in design prose
(`docs/design/24-authoring-a-setting.md`, `docs/design/27-tooling.md`); nothing in the engine
answers the question in a form a tool can check.

**Why this priority**: every other story depends on this closed set existing — an override
cannot be validated against a set that has no machine-readable form.

**Independent Test**: run `describe --overridable` against the engine with no setting loaded and
confirm it returns structured JSON naming each overridable mechanism, its kind (disable, rename,
retune, extend), and — where relevant — what depends on it.

**Acceptance Scenarios**:

1. **Given** the engine with no setting loaded, **When** `describe --overridable` is run, **Then**
   it returns structured JSON listing the closed overridable set.
2. **Given** the published overridable set, **When** a setting's `overrides:` block names a
   mechanism not in that set, **Then** loading the setting fails with a clear error naming the
   offending key — never a silent no-op.

---

### User Story 2 - A setting can disable, rename, retune and extend (Priority: P1)

A setting author writes an `overrides:` block in `setting.yaml` (per
`docs/design/24-authoring-a-setting.md`'s example) and expects each of the four kinds to take
effect: a disabled mechanism disappears from the resolved configuration and from `describe`; a
rename changes only presentation; a retuned table replaces the engine's own; an extended list
gains the setting's rows without losing the engine's.

**Why this priority**: this is the mechanism itself — the reason the issue exists. Without it,
`overrides:` is parsed (per #315) but inert.

**Independent Test**: load a setting whose `overrides:` block disables one mechanism, renames
another, retunes a table and extends a list; confirm the resolved configuration reflects all four
changes and that internal state keys are unaffected by the rename.

**Acceptance Scenarios**:

1. **Given** a setting that disables Taint, **When** the configuration is resolved, **Then** Taint's
   verbs are absent from `describe` and calling one anyway is a structured error, not a silent
   no-op.
2. **Given** a setting that renames Taint to Shadow, **When** output is rendered, **Then** the
   presented label reads "Shadow" while the underlying state field and verb names remain `taint`.
3. **Given** a setting that retunes a table, **When** that table is consulted, **Then** the
   setting's replacement is used in place of the engine default.
4. **Given** a setting that extends a list (e.g. careers), **When** that list is resolved, **Then**
   it contains the engine's own entries plus the setting's, with none lost.

---

### User Story 3 - Three layers resolve in a fixed order, each only narrowing (Priority: P2)

A chronicle may declare its own `houserules.yaml`, layered on top of a setting's overrides, on
top of engine defaults. The resolution order is fixed: engine defaults → setting overrides →
chronicle houserules, last wins — and each layer may only narrow what the previous allowed, never
widen it (re-enabling something a setting disabled is not permitted at the houserules layer).

**Why this priority**: without a defined and enforced load order, two authors reasoning about the
same setting could disagree about which value actually applies at the table — this is the
mechanism's correctness guarantee, but it builds on Stories 1 and 2 existing first.

**Independent Test**: construct a setting override and a conflicting chronicle houserule for the
same mechanism, resolve, and confirm the houserule wins; then construct a houserule that tries to
re-enable something the setting disabled, and confirm that load fails rather than widening scope.

**Acceptance Scenarios**:

1. **Given** a setting override and a chronicle houserule that both name the same mechanism,
   **When** the configuration is resolved, **Then** the houserule's value is the one in effect.
2. **Given** a setting that disables a mechanism, **When** a chronicle houserule attempts to
   re-enable it, **Then** resolution fails with a clear error rather than silently widening scope.
3. **Given** no chronicle houserules at all, **When** the configuration is resolved, **Then** the
   result is exactly the setting-overridden configuration with no further change.

---

### Edge Cases

- What happens when an `overrides:` block disables a mechanism while another part of the same
  setting (e.g. a table) still depends on it? The setting must fail to load — this is a
  contradiction, not a runtime surprise (per `docs/design/27-tooling.md` section 4).
- What happens when a rename maps two different engine mechanics to the same presented label?
  Ambiguous presentation is a setting-authoring concern, not one this mechanism must detect;
  each mechanic's rename is independent and the mechanism does not need to reject collisions,
  but each rename is validated against the closed set on its own.
- What happens when `overrides:` is entirely absent from `setting.yaml`? Resolution proceeds with
  the engine defaults unchanged — the block is optional.
- What happens when a chronicle has no `houserules.yaml` at all? Resolution stops at the
  setting-overridden layer, per Story 3's third acceptance scenario.
- What happens when an `extend` names a list the closed set does not recognise as extendable?
  Load error, same as any override naming something outside the closed set.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST publish a closed, machine-readable set of overridable mechanisms via
  `describe --overridable`, each entry naming the mechanism, which override kind(s) apply to it,
  and any other mechanism it depends on.
- **FR-002**: The engine MUST reject, as a load error, any override (in a setting's `overrides:`
  block or a chronicle's `houserules.yaml`) that names a mechanism outside the published closed
  set.
- **FR-003**: The engine MUST support `disable` overrides: a disabled mechanism's verbs are absent
  from `describe`, invoking one anyway is a structured error, and any rule the setting retains that
  depends on the disabled mechanism is itself a load error.
- **FR-004**: The engine MUST support `rename` overrides as presentation-only: rendered output uses
  the setting's word, while every internal identifier (state field, verb name) is unaffected.
- **FR-005**: The engine MUST support `retune` overrides: a named table is replaced wholesale by
  the setting's own file, loaded by the same name the engine used.
- **FR-006**: The engine MUST support `extend` overrides: a setting's rows are appended to the
  engine's own list (careers, gear, creatures, or table rows), never replacing what the engine
  already provides.
- **FR-007**: The engine MUST resolve configuration in the fixed order engine defaults → setting
  overrides → chronicle houserules, with the last layer to touch a given mechanism winning.
- **FR-008**: The engine MUST reject, as a load error, any layer that attempts to widen what an
  earlier layer already narrowed (e.g. a houserule re-enabling a mechanism a setting disabled).
- **FR-009**: The engine's `describe` output, once a setting (and optionally a chronicle) is
  loaded, MUST reflect the resolved configuration — a disabled mechanism's verbs do not appear.
- **FR-010**: The override mechanism MUST remain purely declarative: a setting supplies only data
  recognised by the closed set, never code, and there is no hook or plugin path through which a
  setting could run its own logic.

### Key Entities

- **Overridable set**: the closed, engine-published list of mechanisms that may be disabled,
  renamed, retuned or extended, together with each entry's kind(s) and dependencies.
- **Override layer**: one of the three ordered inputs to resolution — engine defaults, a setting's
  `overrides:` block, a chronicle's `houserules.yaml` — each expressed in the same shape.
- **Resolved configuration**: the single configuration produced by applying all three layers in
  order; what `describe` reflects and what the chronicle records at bootstrap.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A setting author can determine, from `describe --overridable` alone, every mechanism
  eligible for override and its kind, without reading engine source.
- **SC-002**: An override naming something outside the closed set fails to load 100% of the time,
  with an error identifying the offending key — never a silent no-op or warning.
- **SC-003**: For any mechanism a setting renames, no stored state key or verb name changes, in
  100% of cases — verified by comparing engine identifiers before and after applying a rename.
- **SC-004**: Given the same setting and chronicle houserules, resolution produces the same
  configuration every time (deterministic, no reliance on load order beyond the fixed three
  layers).

## Assumptions

- This feature builds directly on #315 (`setting.yaml` loader), which already parses and passes
  through the `overrides:` block unvalidated; this feature adds the validation and resolution that
  block was deliberately left without.
- Chronicle `houserules.yaml` is assumed to use the same `overrides:`-block shape as a setting's
  own overrides (disable/rename/retune/extend), consistent with `docs/design/24-authoring-a-setting.md`
  describing it as "loaded after engine defaults, exactly like a chronicle's houserules.yaml" —
  i.e. the two are structural peers in the same pipeline.
- `conversion.yaml` (a separate concern, #317) and the content rules for what a replacement table
  may contain (`docs/design/04-tables.md`) are out of scope here, per the source issue.
- The initial overridable set is seeded from mechanisms already implemented in the engine as of
  this feature (e.g. Taint, Trauma, careers, skills, tables already named in design docs); adding a
  wholly new engine mechanism later also means adding its entry to this closed set, which is not
  this feature's job to anticipate.
