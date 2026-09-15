# Quickstart: validating this feature

## Part 1 — `downtime`/`rally` CLI verbs (this repo)

```bash
cd /root/source/neilgfoster/wyrd/.claude/worktrees/agent-a5bb521872f8e7655
PYTHONPATH=engine python3 -m wyrd.client downtime --action upkeep --destination away --standing 3 --coin 5 --trade standing
# {"verb": "downtime", "action": "upkeep", "standing": 2, "coin": 5, "trade": "standing"}

PYTHONPATH=engine python3 -m wyrd.client downtime --action upkeep --destination home --standing 3 --coin 5
# {"verb": "downtime", "action": "upkeep", "standing": 3, "coin": 5, "trade": "none"}

PYTHONPATH=engine python3 -m wyrd.client downtime --action rest --stamina-max 8
# {"verb": "downtime", "action": "rest", "stamina": 8}

PYTHONPATH=engine python3 -m wyrd.client downtime --action mend --wound-id w1 \
    --wounds-json '[{"id": "w1", "effect": {"skill": -10}, "recurring": false, "closed": null}]'
# {"verb": "downtime", "action": "mend", "success": true, "closed": false, "wounds": [...]}

PYTHONPATH=engine python3 -m wyrd.client rally --strain 2 --stamina 3 --stamina-max 8 \
    --advancement-record-json '{"triggers": [], "advances_unspent": 0}'
# {"verb": "rally", "strain": 1, "stamina": 4, "award": null, "pending": null}
```

Run the unit suite:

```bash
cd /root/source/neilgfoster/wyrd/.claude/worktrees/agent-a5bb521872f8e7655
PYTHONPATH=engine python3 -m unittest tests.engine.test_verbs -v
python3 -m ruff check .
python3 -m ruff format --check .
```

## Part 2 — the three skills (`wyrd-chronicle-template`, separate PR)

Manual walkthrough inside a bootstrapped chronicle (no automated harness — that repo has none):

1. `/wyrd-character` — confirm it shows the current sheet, and (with an unspent advance present
   in `pc.yaml`) offers to spend it; verify the resulting `pc.yaml` matches what
   `wyrd spend-advance` alone would produce for the same input.
2. `/wyrd-downtime` — walk Destination, Upkeep (away from home), the Undertaking choice (try
   Mend against a named wound), and confirm `pc.yaml`'s `standing`/`coin`/`wounds`/`stamina`
   match the `downtime`/`rally` verb outputs for the same inputs.
3. `/wyrd-end-session` — confirm `recap.md` matches `wyrd recap`'s own text for the current
   `chronicle.yaml`, and that `git log` shows a new commit covering the changed files.
