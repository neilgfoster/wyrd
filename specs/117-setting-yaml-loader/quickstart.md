# Quickstart: setting.yaml loader and validator

## Prerequisites

Python 3.11+, no dependencies to install (stdlib only). Run from the repo root.

## Validate a good setting.yaml

```bash
cat > /tmp/setting.yaml <<'EOF'
name: example-setting
title: Example Setting
line: fantasy
requires_engine: ">=0.1.0"
version: 0.1.0
description: "A minimal setting used to validate the setting.yaml checker."
tone:
  prophecy: forbidden
  victory: mitigation
  power_curve: flat
  scope: personal
  scale_drift: suppressed
  mortality: high
  register: "one line naming the voice"
EOF
python3 tools/check_setting.py /tmp/setting.yaml
```

**Expected**: exits 0, reports success (matches `check_bestiary.py`'s success output shape).

## Validate a broken setting.yaml (missing field)

```bash
cat > /tmp/setting-bad.yaml <<'EOF'
name: example-setting
title: Example Setting
line: fantasy
requires_engine: ">=0.1.0"
version: 0.1.0
tone:
  prophecy: forbidden
  victory: mitigation
  power_curve: flat
  scope: personal
  scale_drift: suppressed
  mortality: high
  register: "one line naming the voice"
EOF
python3 tools/check_setting.py /tmp/setting-bad.yaml
```

**Expected**: exits non-zero, reports `description` as the missing field.

## Validate an incompatible requires_engine

```bash
sed 's/requires_engine: ">=0.1.0"/requires_engine: ">=99.0.0"/' /tmp/setting.yaml > /tmp/setting-incompatible.yaml
python3 tools/check_setting.py /tmp/setting-incompatible.yaml
```

**Expected**: exits non-zero, reports the declared range (`>=99.0.0`) against the running engine's
actual version (`0.1.0`).

## Validate a bad tone value

```bash
sed 's/prophecy: forbidden/prophecy: whenever/' /tmp/setting.yaml > /tmp/setting-bad-tone.yaml
python3 tools/check_setting.py /tmp/setting-bad-tone.yaml
```

**Expected**: exits non-zero, reports `tone.prophecy` and its allowed values
(`forbidden | rare | central`).

## Every failure is reported, not just the first (matches check_bestiary.py's design)

Combine two problems in one file (missing `description` AND a bad `tone.prophecy` value) and
confirm both appear in the output, not just the first one encountered.
