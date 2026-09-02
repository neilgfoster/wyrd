# Contract: CLI surface

Matches `docs/design/02-architecture.md`'s existing CLI sketch exactly.

```text
wyrd propose --actor A --mechanic M [--skill S] [--target T] [--difficulty D] [--declaration-bonus N]
    -> prints JSON: {"proposal_id": ..., "roll": {...}, "mutations": [...]}

wyrd commit <proposal-id>
    -> applies exactly the staged mutations, atomically; prints the applied mutations
    -> error, non-zero exit, if <proposal-id> does not resolve to an open proposal

wyrd discard <proposal-id>
    -> writes nothing; prints confirmation
    -> error, non-zero exit, if <proposal-id> does not resolve to an open proposal
```

## Library contract (`engine/wyrd/resolution.py`)

```python
def propose(
    actor: str,
    mechanic: str,
    skill: str | None = None,
    target: str | None = None,
    difficulty: str = "average",
    declaration_bonus: int = 0,
    *,
    state_path: pathlib.Path = ...,
    seed: int | None = None,
) -> dict:
    """Returns {"proposal_id": str, "roll": dict, "mutations": list[dict]}.
    Writes nothing. Raises ValueError for an unknown mechanic or missing entity."""

def commit(proposal_id: str, *, state_path: pathlib.Path = ...) -> dict:
    """Applies the proposal's staged mutations atomically; invalidates the id.
    Returns {"proposal_id": str, "mutations": list[dict]}.
    Raises KeyError if proposal_id does not resolve to an open proposal."""

def discard(proposal_id: str) -> dict:
    """Writes nothing; invalidates the id. Returns {"proposal_id": str}.
    Raises KeyError if proposal_id does not resolve to an open proposal."""
```

`seed` is exposed for reproducible tests (mirrors `rules.roll_d100`'s own `seed` parameter);
omitted in real play, where the platform's default randomness is used.
