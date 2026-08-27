# Quickstart: Standing and the material economy

## Prerequisites

Python 3.11+, standard library only (`docs/design/27-tooling.md`).

## Validate a gear file

```bash
python3 tools/check_gear.py specs/023-standing-material-economy/example-gear.yaml
```

Expected: no output (or a success summary), exit 0.

## Confirm the validator catches faults

Run against a deliberately broken copy (missing field, bad armour rank, bad damage type,
unrecognised field, negative price):

```bash
python3 tools/check_gear.py specs/023-standing-material-economy/example-gear-broken.yaml
```

Expected: non-zero exit, one reported error per planted fault, each naming its entry and field.

## Read Upkeep cold

Open `docs/design/16-session.md`'s Downtime → Upkeep step with no other document open. Every term it
uses (Standing, coin) should resolve within `design/` — grep confirms no dangling reference:

```bash
grep -rn "Standing" design/
```

Every hit should be inside a document that also defines the term (`03-rules.md`), not only a use
of it.

## Run the full check suite

```bash
python3 tools/check_gear.py specs/023-standing-material-economy/example-gear.yaml
python3 tools/check_docs.py
python3 tools/backlog.py check
```

All three exit 0.
