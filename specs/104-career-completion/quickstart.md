# Quickstart: Career completion grants Stamina and a Mark

```bash
export PYTHONPATH=engine
```

The spend that carries the last granted skill to the cap pays out. Guard grants blade and watch
at 70%; watch is already there, blade is at 65%:

```bash
python3 -m wyrd.client spend-advance --spend raise --skill blade \
  --view-json '{"career":"guard","career_history":[],"skills":{"blade":65,"watch":70},
                "advances_unspent":1,"stamina_max":6,"marks":[],"career_completed":false}' \
  --career-json '{"id":"guard","entry":true,"skills":{"blade":70,"watch":70}}'
# {"verb": "spend-advance", "spent": true, "spend": "raise",
#  "view": {..., "skills": {"blade": 70, "watch": 70}, "advances_unspent": 0,
#           "stamina_max": 7, "marks": [{"career": "guard"}], "career_completed": true}}
```

The spend before it pays nothing — a career part-finished is not a career finished:

```bash
python3 -m wyrd.client spend-advance --spend raise --skill blade \
  --view-json '{"career":"guard","career_history":[],"skills":{"blade":60,"watch":70},
                "advances_unspent":1,"stamina_max":6,"marks":[],"career_completed":false}' \
  --career-json '{"id":"guard","entry":true,"skills":{"blade":70,"watch":70}}'
# "stamina_max": 6, "marks": [], "career_completed": false
```

At the ceiling the Mark still lands and the Stamina does not:

```bash
python3 -m wyrd.client spend-advance --spend raise --skill blade \
  --view-json '{"career":"guard","career_history":[],"skills":{"blade":65,"watch":70},
                "advances_unspent":1,"stamina_max":10,"marks":[],"career_completed":false}' \
  --career-json '{"id":"guard","entry":true,"skills":{"blade":70,"watch":70}}'
# "stamina_max": 10, "marks": [{"career": "guard"}]
```

A whole chronicle, in the library, mirroring `tools/check_advancement.py`'s twelve instances:

```python
from wyrd import advancement

career = {"id": "guard", "entry": True, "skills": {"blade": 70, "watch": 70}}
careers = [career]
view = advancement.new_view("guard", {"blade": 70, "watch": 65}, advances_unspent=100)

for _ in range(12):
    view = advancement.spend_advance("raise", view, career, skill="watch")["view"]   # completes
    view = advancement.spend_advance(                                                # re-enters
        "change_career", view, career, careers=careers, target="guard"
    )["view"]
    view = {**view, "skills": {"blade": 70, "watch": 65}}   # a fresh instance to finish

print(view["stamina_max"], len(view["marks"]))   # 10 12
```

## Verify

```bash
PYTHONPATH=engine python3 -m pytest tests/engine/test_advancement.py tests/engine/test_career.py -q
python3 tools/check_advancement.py
python3 -m ruff check . && python3 -m ruff format --check .
python3 tools/check_docs.py
```

Expected: tests green; `check_advancement.py` prints the ceiling 10 and twelve Marks that the
tests assert the engine reproduces; ruff clean; docs graph whole.
