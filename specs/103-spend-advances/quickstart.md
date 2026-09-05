# Quickstart: Spend advances — raise, open, change career

```bash
export PYTHONPATH=engine
```

Raise a skill the career grants, from a character view carrying one unspent advance:

```bash
python3 -m wyrd.client spend-advance --spend raise --skill blade \
  --view-json '{"career":"guard","career_history":[],"skills":{"blade":30},"advances_unspent":1}' \
  --career-json '{"id":"guard","entry":true,"skills":{"blade":70,"watch":70}}'
# {"verb": "spend-advance", "spent": true, "spend": "raise",
#  "view": {"career": "guard", ..., "skills": {"blade": 35}, "advances_unspent": 0}}
```

Open a granted skill the character has never trained — it starts at 25%:

```bash
python3 -m wyrd.client spend-advance --spend open --skill watch \
  --view-json '{"career":"guard","career_history":[],"skills":{"blade":30},"advances_unspent":1}' \
  --career-json '{"id":"guard","entry":true,"skills":{"blade":70,"watch":70}}'
```

A change to a non-entry career is refused until one of its prerequisites is complete:

```bash
python3 -m wyrd.client spend-advance --spend change_career --target guard-captain \
  --view-json '{"career":"guard","career_history":[],"skills":{"blade":70,"watch":70},"advances_unspent":1}' \
  --career-json '{"id":"guard","entry":true,"skills":{"blade":70,"watch":70}}' \
  --careers-json '[{"id":"guard","entry":true,"skills":{"blade":70,"watch":70}},
                   {"id":"guard-captain","entry":false,"prerequisites":["guard"],
                    "skills":{"blade":70,"watch":70,"command":70}}]'
# {"spent": false, "refusal": "prerequisites_unmet", ...}
```

Leaving guard complete records the completion, and the same change then succeeds:

```python
from wyrd import advancement

GUARD = {"id": "guard", "entry": True, "skills": {"blade": 70, "watch": 70}}
CAPTAIN = {"id": "guard-captain", "entry": False, "prerequisites": ["guard"],
           "skills": {"blade": 70, "watch": 70, "command": 70}}

view = advancement.new_view("guard", {"blade": 70, "watch": 70}, advances_unspent=2)
view = advancement.spend_advance(
    "change_career", view, GUARD, careers=[GUARD, CAPTAIN], target="guard"
)["view"]
# view["career_history"] == [{"career": "guard", "completed": True}]
result = advancement.spend_advance(
    "change_career", view, GUARD, careers=[GUARD, CAPTAIN], target="guard-captain"
)
# result["spent"] is True
```
