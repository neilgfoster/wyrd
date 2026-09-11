"""Elapsed time: the "elsewhere" `close_downtime` (#311) and `journey.resolve_leg`'s
summarised legs (#287) both deferred to (#338).

docs/design/19-campaign.md: "Game time advances only when the fiction advances it... Take the
expected value over the span. Roll those, apply them, and generate the resulting state." This
module is that operation: advancing a chronicle's calendar by an elapsed span, and computing each
active Threat's (#334) expected-value activation count and resolved effects over it -- rather
than simulating every intervening week's percentile check individually.

Two pure functions and one combining function, no I/O, matching `threat.py`/`era.py`'s own
division of labour -- a caller persists the returned calendar via `wyrd.state.save_chronicle` and
is responsible for actually applying each returned effect (prose, GM narration, same separation
`threat.py` already keeps):

- `advance_calendar` -- day/year arithmetic, reusing #335's fixed 365-day year.
- `expected_activation_count` -- the expected-value formula (`weeks * imminence / 10`, rounded).
- `advance_time` -- combines both, and (unlike `threat.check_activation`/`resolve_effects`,
  which take caller-supplied dice) owns its own seeded randomness via `rules.roll_d100`, since
  the number of rolls needed is itself computed here rather than known to the caller in advance
  (research.md) -- deterministic given a fixed seed, matching `verbs.roll`'s existing convention.

Python 3.11+, standard library only.
"""

from __future__ import annotations

from wyrd import rules, threat

_DAYS_PER_YEAR = 365
_DAYS_PER_WEEK = 7


def advance_calendar(
    calendar: dict, elapsed_days: int, days_per_year: int = _DAYS_PER_YEAR
) -> dict:
    """Advance `calendar`'s `day` by `elapsed_days`, wrapping into `year` (FR-001).

    `month` is passed through unchanged -- its semantics are not defined elsewhere in this
    codebase (spec.md's Assumptions).
    """
    total_days = calendar["day"] + elapsed_days
    years_elapsed, day = divmod(total_days, days_per_year)
    return {**calendar, "year": calendar["year"] + years_elapsed, "day": day}


def expected_activation_count(
    imminence: int, elapsed_days: int, days_per_week: int = _DAYS_PER_WEEK
) -> int:
    """The expected-value activation count over `elapsed_days` (FR-002).

    `round(weeks * imminence / 10)`, `weeks = elapsed_days // days_per_week` -- matches
    docs/design/19-campaign.md's own worked example exactly (imminence 4 over 5 weeks: `2`).
    """
    weeks = elapsed_days // days_per_week
    return round(weeks * imminence / 10)


def advance_time(
    calendar: dict, threats: list[dict], elapsed_days: int, seed: int | None = None
) -> dict:
    """Advance `calendar` and generate each Threat's expected-value activations (FR-003, FR-004).

    Returns `{"calendar": <advanced>, "activations": [{"id", "activation_count", "effects"},
    ...]}`, one activations entry per `threats` entry, in order. Each entry's `effects` list has
    exactly `activation_count` resolved entries (`threat.resolve_effects`) -- empty when the
    count is `0`. Rolls are drawn via `rules.roll_d100(seed=seed + offset)` with a running
    `offset` across the whole call, so the same `seed` reproduces identical results every time
    (this issue's own acceptance criterion) while still drawing a distinct roll for each
    activation.
    """
    new_calendar = advance_calendar(calendar, elapsed_days)

    activations = []
    offset = 0
    for entity in threats:
        threat_block = entity.get("threat", {})
        count = expected_activation_count(threat_block.get("imminence", 0), elapsed_days)
        effects = []
        for _ in range(count):
            roll_seed = None if seed is None else seed + offset
            table_roll = rules.roll_d100(seed=roll_seed)
            effects.append(threat.resolve_effects(threat_block.get("effects", {}), table_roll))
            offset += 1
        activations.append({"id": entity.get("id"), "activation_count": count, "effects": effects})

    return {"calendar": new_calendar, "activations": activations}
