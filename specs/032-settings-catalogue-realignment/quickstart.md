# Quickstart

## Run the tests (no network)

```bash
python3 -m unittest tools.test_check_settings_catalogue -v
```

## Validate against the live fleet

```bash
python3 tools/check_settings_catalogue.py
```

**Expected**: exit 0, "no drift" — every live `wyrd-setting-*` repo has a catalogue entry and
every entry's `repo:` exists.

## Validate the check actually catches drift

```bash
# Temporarily break one repo: value, confirm the script reports it, then revert.
sed -i 's/wyrd-setting-tor/wyrd-setting-tor-renamed/' settings.yaml
python3 tools/check_settings_catalogue.py   # expect a dangling-entry report, exit 1
git checkout settings.yaml
```
