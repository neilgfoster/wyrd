# Quickstart: Succession: successor selection and inheritance

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import succession

candidates = [
    {"id": "a-rival-merchant", "entanglement": "rival"},
    {"id": "the-inquisitor", "entanglement": "investigating"},
    {"id": "an-old-companion", "entanglement": "companion"},
]

ranked = succession.rank_candidates(candidates)
assert [c["id"] for c in ranked] == ["the-inquisitor", "a-rival-merchant", "an-old-companion"]

proposal = succession.propose_successors(ranked)
assert len(proposal) == 3

inherited = succession.inherit(
    {
        "threads": ["the-one-who-paid"],
        "enemies": ["the-drowned-count"],
        "skills": {"athletics": 40},  # never inherited
        "reputation": "a notorious killing",
    },
    inherited_holding={"id": "the-mill"},
)
assert "skills" not in inherited
assert inherited["threads"] == ["the-one-who-paid"]
assert inherited["predecessor_reputation"] == "a notorious killing"
assert inherited["holding"] == {"id": "the-mill", "encumbered": True}

recorded = succession.record_predecessor("died", fact="killed in the flood", rumour="taken, some say")
assert recorded["status"] == "died"
assert recorded["fact"] != recorded["rumour"]
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_succession -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test in
`tests/engine/test_succession.py`, including the closed-vocabulary rejection and each of the
three predecessor outcomes.
