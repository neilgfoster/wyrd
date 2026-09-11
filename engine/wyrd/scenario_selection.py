"""Scenario selection: the next scenario is picked, not scripted (#339).

docs/design/19-campaign.md, "Scenario selection": at the start of an arc, or when a scenario
closes, the GM reads live threads by heat, matches against candidate scenarios' declared hooks,
scales the pick to the current danger rating, and records what it was adapted from. Candidate
`scenarios/*/scenario.yaml` files themselves live in a setting repo (this repo's own CLAUDE.md:
"no catalogue of a personal library" enters the engine) -- this module operates on an
already-loaded list of scenario dicts a caller supplies.

Four pure functions, no I/O, matching the epic's existing division of labour:

- `rank_by_heat` -- threads sorted by heat, descending, stable (FR-001).
- `select_scenario` -- the candidate whose hooks match the most total live-thread heat, ties
  broken deterministically (FR-002, FR-003, FR-004).
- `scale_encounters` -- reuses `adversary.scaled_count` unchanged; no new scaling formula
  (FR-005).
- `record_source` -- attaches `source: {adapted_from, changed}` (FR-006).

Python 3.11+, standard library only.
"""

from __future__ import annotations

from wyrd import adversary


def rank_by_heat(threads: list[dict]) -> list[dict]:
    """`threads` sorted by `heat` descending, stable on ties (FR-001)."""
    return sorted(threads, key=lambda t: t["heat"], reverse=True)


def select_scenario(threads: list[dict], candidates: list[dict]) -> dict | None:
    """The candidate whose hooks match the greatest total live-thread heat (FR-002).

    A thread "matches" a candidate when the two `hooks` lists share at least one entry --
    counted once per thread, regardless of how many hooks overlap. Ties broken by earliest
    position in `candidates` (FR-003). Returns `None` when every candidate's total is `0`, or
    when either input list is empty (FR-004).
    """
    best: dict | None = None
    best_score = 0
    for candidate in candidates:
        candidate_hooks = set(candidate.get("hooks", []))
        score = sum(
            thread.get("heat", 0)
            for thread in threads
            if candidate_hooks & set(thread.get("hooks", []))
        )
        if score > best_score:
            best_score = score
            best = candidate
    return best


def scale_encounters(scenario: dict, danger: int, party: int) -> dict:
    """Scale `scenario`'s `encounters` through `adversary.scaled_count`, unchanged (FR-005).

    Each encounter gains a `scaled_count` key; its own `written_count` is left untouched for
    reference. Every other field of `scenario` and of each encounter is unchanged.
    """
    written_for = scenario["written_for"]
    encounters = [
        {
            **encounter,
            "scaled_count": adversary.scaled_count(
                encounter["written_count"], danger, party, written_for
            ),
        }
        for encounter in scenario.get("encounters", [])
    ]
    return {**scenario, "encounters": encounters}


def record_source(scenario: dict, adapted_from: str, changed: str) -> dict:
    """Attach `source: {adapted_from, changed}` to `scenario` (FR-006), other fields unchanged."""
    return {**scenario, "source": {"adapted_from": adapted_from, "changed": changed}}
