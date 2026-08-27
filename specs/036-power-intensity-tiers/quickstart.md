# Quickstart: Optional intensity tiers for a system of power

Validates the feature end-to-end using the same tooling pattern every other `tools/check_*.py`
script in this repository uses — an embedded self-test, run with no path argument.

## Prerequisites

- Python 3.11+ (standard library only — no install step)
- Repository checked out at this feature's branch

## Run the extended self-test

```bash
python3 tools/check_power_systems.py
```

**Expected outcome**: prints a line confirming the worked examples validate clean and every
rejection class fires, now including the four `intensity_tiers` malformation classes from spec.md
User Story 3 (bad `difficulty`, non-positive `cost_multiplier`, negative
`ill_omen_taint_bonus`, missing `label`). Exit code `0`.

## Validate a tiered system of power by hand

```bash
cat > /tmp/tiered-power.yaml <<'YAML'
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    resolve_cost: 1
    requires_training: true
    ill_omen_taint: 1
    intensity_tiers:
      - label: minor
        difficulty: average
        cost_multiplier: 1
        ill_omen_taint_bonus: 0
      - label: moderate
        difficulty: hard
        cost_multiplier: 2
        ill_omen_taint_bonus: 1
      - label: major
        difficulty: very hard
        cost_multiplier: 4
        ill_omen_taint_bonus: 3
YAML
python3 tools/check_power_systems.py /tmp/tiered-power.yaml
```

**Expected outcome**: `All systems of power hold. (/tmp/tiered-power.yaml)`, exit code `0` —
proves SC-001 (a setting author can express three-tiered stakes using only fields this feature
adds).

## Confirm a setting with no tiers is unaffected

```bash
cat > /tmp/plain-power.yaml <<'YAML'
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    requires_training: true
YAML
python3 tools/check_power_systems.py /tmp/plain-power.yaml
```

**Expected outcome**: validates clean exactly as it did before this feature — proves SC-002 (no
regression for a `power.yaml` with no `intensity_tiers`).

## Confirm a malformed tier is rejected

```bash
cat > /tmp/broken-tier.yaml <<'YAML'
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    requires_training: true
    intensity_tiers:
      - label: major
        difficulty: apocalyptic
        cost_multiplier: 4
        ill_omen_taint_bonus: 3
YAML
python3 tools/check_power_systems.py /tmp/broken-tier.yaml
```

**Expected outcome**: `FAILED (1):` naming `ember-craft`'s `major` tier and the invalid
`difficulty` value `apocalyptic` — proves SC-003 (a malformed tier is rejected at validation
time, with an error naming which system of power and which tier is at fault).

## Confirm the doc states the field is optional

```bash
grep -A2 "intensity_tiers" docs/design/09-systems-of-power.md | head -5
```

**Expected outcome**: prose stating `intensity_tiers` is optional and does not require any
existing declared system of power to change — proves SC-004.
