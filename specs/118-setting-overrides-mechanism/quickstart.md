# Quickstart: Setting Overrides Mechanism

Validates the feature end-to-end against the running engine. Run from the repo root.

## Prerequisites

```bash
cd /root/source/neilgfoster/wyrd
```

## 1. The closed set is published

```bash
PYTHONPATH=engine python3 -m wyrd.client describe --overridable
```

Expect JSON naming `taint`, `trauma`, the four `oracle-prompt-*` families and `skills`, each with
its legal kinds.

## 2. An override outside the closed set is a load error

```bash
cat > /tmp/bad-setting.yaml <<'EOF'
overrides:
  disable: [not-a-mechanism]
EOF
PYTHONPATH=engine python3 -m wyrd.client describe --setting /tmp/bad-setting.yaml
```

Expect `{"error": {"verb": "describe", "reason": "...not in the engine's overridable set"}}`.

## 3. Disabling a mechanism removes its verb from `describe`

```bash
cat > /tmp/setting.yaml <<'EOF'
overrides:
  disable: [taint]
EOF
PYTHONPATH=engine python3 -m wyrd.client describe --setting /tmp/setting.yaml --name track
```

Expect the `track` entry's `mechanisms` to read `["trauma"]` only.

## 4. Calling a disabled mechanism is a structured error

```bash
PYTHONPATH=engine python3 -m wyrd.client track --value 3 --mechanism taint --delta 1 \
  --setting /tmp/setting.yaml
```

Expect `{"error": {"verb": "track", "reason": "'taint' is disabled by the active setting"}}`.

## 5. A rename is presentation-only

```bash
cat > /tmp/rename-setting.yaml <<'EOF'
overrides:
  rename: {taint: shadow}
EOF
PYTHONPATH=engine python3 -m wyrd.client track --value 3 --mechanism taint --delta 1 \
  --setting /tmp/rename-setting.yaml
```

Expect `"mechanism": "taint"` (unchanged) and `"label": "shadow"` (presentation only).

## 6. A chronicle houserule wins over a setting override

```bash
cat > /tmp/houserules.yaml <<'EOF'
overrides:
  rename: {taint: corruption}
EOF
PYTHONPATH=engine python3 -m wyrd.client track --value 3 --mechanism taint --delta 1 \
  --setting /tmp/rename-setting.yaml --chronicle /tmp/houserules.yaml
```

Expect `"label": "corruption"`.

## Automated coverage

```bash
PYTHONPATH=engine python3 -m unittest tests.engine.test_overrides tests.engine.test_verbs \
  tests.engine.test_client tests.engine.test_state -v
python3 -m unittest discover -s tools -p 'test_check_setting.py' -v
```
