"""Generation request/result data model and mode validation (#420).

specs/161-adventure-and-campaign-generation (#99, merged) specifies adventure/campaign generation
at any scale. This module implements its first, foundational layer -- FR-001 through FR-006 --
the `GenerationRequest`/`GenerationResult` shapes and mode validation, as pure, side-effect-free
functions. No persistence, no anti-inflation checks (FR-007-011), no commit-back (FR-012-015),
and no content generation (FR-016-020) -- those are separate, dependent sibling features.

Two transient shapes, matching `thread.py`/`threat.py`'s own division of labour: plain `dict`
records built and validated by pure functions, stdlib only.

- `new_request` -- builds a `GenerationRequest` dict from its fields (FR-001, FR-003).
- `is_campaign_spine_shape` -- confirms a `campaign-spine`-scale request maps to "an `arc` request
  with no `parent` and `scale: campaign`," not a fourth structural type (FR-002).
- `validate_request` -- the mode/scale validation gate (FR-003-FR-006): returns `None` when the
  request is well-formed, or a `GenerationRequestError` naming exactly which rule failed.
- `new_result` -- builds a `GenerationResult` dict (FR-007's shape only; `checks` is never
  populated by this module).

Every rejection is a `GenerationRequestError` (`code` + `detail`), never a bare exception or an
unexplained boolean, per FR-008 and contracts/generation-request.md's Error Shapes section.

Python 3.11+, standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass

SCALES = ("beat", "arc", "campaign-spine")
MODES = ("live-play", "setting-authoring")

# Fields that belong exclusively to a `live-play` request's additional state (FR-004).
_LIVE_PLAY_FIELDS = ("threads", "threat_state", "danger_rating", "era")

# Fields that belong exclusively to a `setting-authoring` request's additional state (FR-005).
_SETTING_AUTHORING_FIELDS = ("voice", "existing_entities", "invention_permitted")


@dataclass(frozen=True)
class GenerationRequestError:
    """A structured rejection reason (FR-008): a closed `code` plus a human-readable `detail`."""

    code: str
    detail: str


def new_request(
    *,
    scale: str,
    mode: str,
    setting_ref: object,
    tone_contract: object,
    written_for: int | None = None,
    threads: list | None = None,
    threat_state: list | None = None,
    danger_rating: object | None = None,
    era: object | None = None,
    voice: object | None = None,
    existing_entities: list | None = None,
    invention_permitted: bool | None = None,
) -> dict:
    """Build a `GenerationRequest` record (FR-001, FR-003).

    Every field is stored as given, including `None` for an omitted optional field -- this
    constructor does not validate; call `validate_request` on the result for that (FR-003-FR-006).
    """
    return {
        "scale": scale,
        "mode": mode,
        "setting_ref": setting_ref,
        "tone_contract": tone_contract,
        "written_for": written_for,
        "threads": threads,
        "threat_state": threat_state,
        "danger_rating": danger_rating,
        "era": era,
        "voice": voice,
        "existing_entities": existing_entities,
        "invention_permitted": invention_permitted,
    }


def is_campaign_spine_shape(request: dict) -> bool:
    """Confirm `request` maps to "an `arc` request with no `parent`, `scale: campaign`" (FR-002).

    A `campaign-spine`-scale request never carries a `parent` field (recursive containment, ADR
    0003, makes the absence of `parent` what makes an arc top-level) -- this function checks that
    invariant explicitly rather than treating `campaign-spine` as a fourth structural type.
    Returns `False` for a request whose `scale` is not `campaign-spine` at all.
    """
    if request.get("scale") != "campaign-spine":
        return False
    return request.get("parent") is None


def _missing_field_error(field: str) -> GenerationRequestError:
    return GenerationRequestError(code=f"missing_{field}", detail=f"'{field}' is required")


def validate_request(request: dict) -> GenerationRequestError | None:
    """Validate `request` against FR-003 through FR-006. `None` means the request is well-formed.

    Checked in order: the always-required base fields (FR-003), `written_for`'s conditional
    requirement (FR-003), which mode-specific state block is present and whether it carries only
    fields belonging to its own mode (FR-006), then that block's own required fields and rules
    (FR-004 for `live-play`, FR-005 for `setting-authoring`).
    """
    scale = request.get("scale")
    mode = request.get("mode")

    if scale not in SCALES:
        return GenerationRequestError(
            code="invalid_scale", detail=f"'scale' must be one of {SCALES}, got {scale!r}"
        )
    if mode not in MODES:
        return GenerationRequestError(
            code="invalid_mode", detail=f"'mode' must be one of {MODES}, got {mode!r}"
        )
    if request.get("setting_ref") is None:
        return _missing_field_error("setting_ref")
    if request.get("tone_contract") is None:
        return _missing_field_error("tone_contract")

    # written_for: required for beat/arc always, and for campaign-spine except in
    # setting-authoring mode (data-model.md; spec.md Edge Cases: campaign-spine in live-play
    # behaves as an ordinary live-play arc request, so written_for is required there too).
    written_for_required = not (scale == "campaign-spine" and mode == "setting-authoring")
    if written_for_required and request.get("written_for") is None:
        return _missing_field_error("written_for")

    foreign_fields = _SETTING_AUTHORING_FIELDS if mode == "live-play" else _LIVE_PLAY_FIELDS
    for field in foreign_fields:
        if request.get(field) is not None:
            return GenerationRequestError(
                code="foreign_mode_field",
                detail=f"'{field}' belongs to the other mode and must not be set for {mode!r}",
            )

    if mode == "live-play":
        return _validate_live_play_state(request)
    return _validate_setting_authoring_state(request)


def _validate_live_play_state(request: dict) -> GenerationRequestError | None:
    """FR-004: required live-play state, plus the "some grounding exists" edge case."""
    if request.get("danger_rating") is None:
        return _missing_field_error("danger_rating")
    if request.get("era") is None:
        return _missing_field_error("era")
    threads = request.get("threads") or []
    threat_state = request.get("threat_state") or []
    if not threads and not threat_state:
        return GenerationRequestError(
            code="no_grounding_state",
            detail="a live-play request must supply at least one of 'threads' or 'threat_state'",
        )
    return None


def _validate_setting_authoring_state(request: dict) -> GenerationRequestError | None:
    """FR-005: required setting-authoring state, and the Q3-grant rejection rule."""
    if request.get("voice") is None:
        return _missing_field_error("voice")
    if request.get("existing_entities") is None:
        return _missing_field_error("existing_entities")
    if request.get("invention_permitted") is not True:
        return GenerationRequestError(
            code="invention_not_permitted",
            detail=(
                "'invention_permitted' must be present and true, traceable to create-setting's "
                "Phase 1 Q3 grant, or the request is rejected before any generation runs"
            ),
        )
    return None


def new_result(candidate: dict, checks: list | None = None, consumed: list | None = None) -> dict:
    """Build a `GenerationResult` record (FR-007's shape only).

    `checks` and `consumed` default to empty lists -- this module never populates them with real
    anti-inflation outcomes; that is a sibling feature's job (FR-007-011).
    """
    return {
        "candidate": candidate,
        "checks": checks if checks is not None else [],
        "consumed": consumed if consumed is not None else [],
    }
