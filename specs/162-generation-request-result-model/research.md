# Phase 0 research: Generation request/result data model and mode validation

No `NEEDS CLARIFICATION` markers remain in the Technical Context — this feature's shape and rules
are fully specified by specs/161-adventure-and-campaign-generation's spec.md (FR-001-006),
data-model.md, and contracts/generation-request.md, all already merged. The only decisions this
phase makes are implementation-shape choices within that existing specification.

## Decision: representation for `GenerationRequest`/`GenerationResult`

- **Decision**: plain `dict` records built by small constructor functions (`new_request`,
  `new_result`), matching the established style of every other transient/value shape in
  `engine/wyrd/` (`thread.py`'s `new_thread`, `threat.py`'s equivalents) rather than a dataclass
  or an external schema library.
- **Rationale**: `docs/design/27-tooling.md` section 6 and the existing modules are consistent —
  plain dicts constructed and validated by pure functions, stdlib only, no external validation
  library anywhere in `engine/wyrd/`. Matching this keeps the new module indistinguishable in
  style from its neighbours, which is worth more than a dataclass's marginal attribute-access
  safety.
- **Alternatives considered**: `@dataclass` — rejected; it would be internally consistent but is
  the one module in the package styled differently from its siblings, which is exactly the kind
  of local inconsistency this repo's own review passes flag. `pydantic`/`attrs` — rejected as an
  unjustified new dependency.

## Decision: how "structured rejection reason" is represented

- **Decision**: a small `GenerationRequestError` (or similarly named) exception/result carrying a
  `code` (a short machine-checkable string identifying which rule failed, e.g.
  `"missing_written_for"`, `"setting_authoring_missing_invention_permitted"`) and a `detail`
  human-readable string — returned or raised by `validate_request()`, never a bare `ValueError`
  with only prose.
- **Rationale**: contracts/generation-request.md's Error Shapes section requires "structured data
  naming which rule/precondition failed, never a bare exception" and this feature's own FR-008
  states the same. A `code` field makes this mechanically checkable by a test/caller without
  string-matching prose.
- **Alternatives considered**: returning `(bool, str)` — rejected, no closed vocabulary for the
  failure reason, so a caller could not branch on which rule failed without parsing prose.

## Decision: `validate_request` return shape on success

- **Decision**: return `None` (or the validated request unchanged) on success, raise/return the
  structured error on failure — a simple validate-and-signal function, not a builder that also
  constructs a `GenerationResult` (that belongs to the sibling generation-pipeline feature,
  FR-016-020, out of scope here).
- **Rationale**: this feature explicitly stops at validation (spec.md Assumptions) — inventing a
  richer return shape here would encroach on the sibling feature's scope.

## Decision: campaign-spine alias check as its own function

- **Decision**: expose a dedicated `is_campaign_spine_shape(request)` (or similarly named)
  function distinct from the general `validate_request()`, per the issue's explicit instruction
  ("a validation function should confirm a campaign-spine request maps to that shape") and FR-002.
- **Rationale**: keeping this as a separately callable, separately testable function makes SC-002
  ("confirmed... by a dedicated validation function") directly verifiable, rather than folding the
  check into the general validator where it could not be exercised or asserted on its own.
