# Feature Specification: setting.yaml loader and validator

**Feature Branch**: `315-setting-yaml-loader`

**Created**: 2026-09-10

**Status**: Draft

**Input**: User description: "setting.yaml loader and validator — parse and validate a setting's setting.yaml: identity (name, title, line), requires_engine version-compatibility check, and the version field a chronicle pins alongside the engine version. Per docs/design/24-authoring-a-setting.md's setting.yaml shape and docs/design/29-evolution.md's dual-pinning. No such loader exists yet in engine/wyrd/. Part of #298."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Loading a well-formed setting.yaml (Priority: P1)

A setting author or the engine's own bootstrap path needs to read a setting's `setting.yaml` and
get back its identity and version facts, so downstream code (chronicle bootstrap, `wyrd doctor`,
future setting-loading verbs) can rely on one validated source instead of each re-reading and
re-checking the raw file.

**Why this priority**: Every other piece of setting-loading work in #298's sibling issues (the
overrides mechanism, chronicle bootstrap) depends on there being one canonical way to read
`setting.yaml`. Without this, each caller invents its own parsing.

**Independent Test**: Can be fully tested by pointing the loader at a `setting.yaml` matching the
shape in `docs/design/24-authoring-a-setting.md` and confirming it returns the parsed identity
and version fields, with no other engine feature required.

**Acceptance Scenarios**:

1. **Given** a `setting.yaml` with all required fields present and a `requires_engine` range the
   running engine satisfies, **When** it is loaded, **Then** the loader returns the parsed
   identity (`name`, `title`, `line`), `version`, and the tone contract block.
2. **Given** a `setting.yaml` with a `requires_engine` range the running engine does not satisfy,
   **When** it is loaded, **Then** loading fails with an error naming the declared range and the
   running engine's actual version.

---

### User Story 2 - Rejecting a malformed setting.yaml (Priority: P1)

A setting author who mistypes or omits a required field in `setting.yaml` needs to find out
immediately, with a clear message naming the problem field — not discover it later as a
mysterious failure somewhere downstream in chronicle bootstrap.

**Why this priority**: This is the whole point of a *validator* rather than a bare parser — per
`docs/design/27-tooling.md`'s deterministic-over-inference principle, a missing/malformed field is
a checkable claim and must be caught by the script, not left for a human or the model to notice.

**Independent Test**: Can be fully tested by feeding the loader a `setting.yaml` missing one
required field at a time and confirming each produces a load error naming that field, independent
of any other feature.

**Acceptance Scenarios**:

1. **Given** a `setting.yaml` missing a required top-level field (`name`, `title`, `line`,
   `requires_engine`, `version`, or `description`), **When** it is loaded, **Then** loading fails
   with an error naming the missing field.
2. **Given** a `setting.yaml` whose tone contract omits a required tone key or uses a value
   outside that key's closed vocabulary (e.g. `prophecy: whenever`), **When** it is loaded,
   **Then** loading fails with an error naming the offending key and its allowed values.
3. **Given** a `setting.yaml` that is not valid YAML at all, **When** it is loaded, **Then**
   loading fails with a parse error rather than a partial or silently-defaulted result.

---

### User Story 3 - Running the validator as a standalone check (Priority: P2)

A setting author (or a CI-less pre-PR habit, mirroring `check_bestiary.py`/`check_gear.py`) wants
to validate a `setting.yaml` from the command line before committing it, without writing any code.

**Why this priority**: Lower than P1 because the loader itself (User Stories 1–2) is the load-
bearing piece other engine code depends on; the standalone script is a convenience wrapper over
the same logic, matching the existing `check_bestiary.py`/`check_gear.py` pattern named in the
issue.

**Independent Test**: Can be fully tested by running the script against a known-good and a
known-bad `setting.yaml` from the command line and checking the exit code and message, independent
of any other feature.

**Acceptance Scenarios**:

1. **Given** a valid `setting.yaml`, **When** `python3 tools/check_setting.py <path>` is run,
   **Then** it exits 0 and reports success.
2. **Given** an invalid `setting.yaml` (missing field, bad tone value, or incompatible
   `requires_engine`), **When** `python3 tools/check_setting.py <path>` is run, **Then** it exits
   non-zero and prints the specific problem.

---

### Edge Cases

- What happens when `setting.yaml` names a `line` value — is `line` a closed vocabulary or free
  text? (Resolved below: free text; the engine does not curate a list of genres.)
- How does the loader handle a `requires_engine` range that is syntactically malformed (e.g. not
  a valid version-range expression)? Treated as a validation failure, same as any other malformed
  field — not a crash.
- What happens when `version` (the setting's own version) is present but not a valid semantic
  version? Rejected the same way an out-of-range field in `check_bestiary.py` is rejected.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a loader that reads a `setting.yaml` file and returns its
  parsed identity (`name`, `title`, `line`), `requires_engine`, `version`, `description`, and tone
  contract block (`prophecy`, `victory`, `power_curve`, `scope`, `scale_drift`, `mortality`,
  `register`) as structured data.
- **FR-002**: The loader MUST reject a `setting.yaml` missing any required top-level field
  (`name`, `title`, `line`, `requires_engine`, `version`, `description`, `tone`) with an error
  naming the specific missing field.
- **FR-003**: The loader MUST reject a `setting.yaml` whose `tone` block is missing a required key
  or uses a value outside that key's closed vocabulary (`prophecy`: forbidden/rare/central;
  `victory`: mitigation/mixed/triumph; `power_curve`: flat/moderate/heroic; `scope`:
  personal/regional/world; `scale_drift`: suppressed/allowed; `mortality`: low/standard/high),
  naming the offending key and its allowed values.
- **FR-004**: The loader MUST check the setting's declared `requires_engine` range against the
  running engine's own version and reject the setting.yaml, with an error naming both values, when
  the running engine does not satisfy the range.
- **FR-005**: The loader MUST reject a `setting.yaml` that is not valid YAML with a parse error,
  rather than returning partial or defaulted data.
- **FR-006**: The loader MUST use the engine's existing restricted-subset YAML reader
  (`docs/design/27-tooling.md` — no third-party YAML dependency), not a new parser.
- **FR-007**: A standalone command-line check script (`tools/check_setting.py`) MUST be provided
  that runs the same validation against a given file path, exits 0 on success, and exits non-zero
  with the specific problem printed on failure — mirroring `tools/check_bestiary.py` and
  `tools/check_gear.py`'s existing shape and documented the same way.
- **FR-008**: Validation of `setting.yaml`'s `overrides:` block (if present) is explicitly out of
  scope for this feature; the loader neither parses nor rejects an `overrides:` key — that is the
  separate overrides-mechanism feature (#316), which depends on this one.
- **FR-009**: Entity schema validation is explicitly out of scope for this feature (already
  covered by #296).

### Key Entities

- **Setting identity**: `name`, `title`, `line`, `description` — the descriptive facts a setting
  declares about itself.
- **Engine compatibility declaration**: `requires_engine` — a version range the setting claims
  compatibility with, checked against the running engine's own version at load time.
- **Setting version**: `version` — the value a chronicle pins alongside the engine version
  (`docs/design/29-evolution.md`), independent of `requires_engine`.
- **Tone contract**: the `tone` block — `prophecy`, `victory`, `power_curve`, `scope`,
  `scale_drift`, `mortality`, `register` — the setting's declared register, each field except
  `register` drawn from a closed vocabulary the engine publishes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A setting author pointing the validator at a `setting.yaml` that matches
  `docs/design/24-authoring-a-setting.md`'s documented shape gets a pass with no false rejection.
- **SC-002**: A setting author who omits or mistypes any one required field or tone value gets a
  failure that names the specific field/value at fault, on the first run — no field's error
  message is generic enough to require re-reading the source to find the problem.
- **SC-003**: A setting declaring an engine-version range the running engine does not satisfy is
  never loaded as if it were compatible — this check is never skipped or defaulted to "pass".
- **SC-004**: The check can be run standalone from the command line with no code changes, the same
  way `check_bestiary.py`/`check_gear.py` already can.

## Assumptions

- `line` (e.g. `fantasy`) is free-text, setting-defined vocabulary, not a closed set the engine
  curates — consistent with how `availability` in `gear.yaml` is documented as setting-defined
  rather than engine-closed.
- `requires_engine` uses a PEP 440 / npm-style comparator range syntax (e.g. `">=0.1.0"`); the
  loader parses and compares it against the engine's own version string, which the engine already
  exposes somewhere (or will need a trivial `__version__` constant added if it does not yet).
- The tone contract's closed vocabularies are exactly the values already documented in
  `docs/design/24-authoring-a-setting.md`'s `setting.yaml` example and `01-principles.md`'s tone
  contract section; this feature does not invent new values.
- This loader is a pure read/validate function — it does not perform the "engine defaults →
  setting overrides → chronicle houserules" resolution (that is #316's scope), and does not touch
  chronicle state.
