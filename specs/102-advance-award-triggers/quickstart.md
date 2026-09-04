# Quickstart: Award advances against the four session triggers

```bash
export PYTHONPATH=engine
```

Award an advance at a Rally, against a session that has awarded nothing yet:

```bash
python3 -m wyrd.client award-advance --trigger learned --advances-unspent 0
# {"awarded": true, "trigger": "learned", "record": {"triggers": ["learned"], "advances_unspent": 1}}
```

The same trigger will not pay twice in one session:

```bash
python3 -m wyrd.client award-advance --trigger learned --awarded learned --advances-unspent 1
# {"awarded": false, "refusal": "already_awarded", ...}
```

Three is the session ceiling, even though there are four triggers:

```bash
python3 -m wyrd.client award-advance --trigger endured \
  --awarded learned --awarded drove --awarded practised --advances-unspent 3
# {"awarded": false, "refusal": "session_ceiling", ...}
```

A new session clears the triggers and keeps the balance:

```bash
python3 -m wyrd.client begin-session --awarded learned --awarded drove --advances-unspent 2
# {"triggers": [], "advances_unspent": 2}
```

From Python:

```python
from wyrd import advancement

record = {"triggers": [], "advances_unspent": 0}
result = advancement.award_advance("drove", record)
record = result["record"]
```
