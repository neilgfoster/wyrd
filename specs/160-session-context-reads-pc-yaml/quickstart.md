# Quickstart: verify session-context resolves pc.yaml

## Prerequisites

- `PYTHONPATH=engine` (this repo's standard convention for running the engine package directly).

## Automated verification

```bash
PYTHONPATH=engine python3 -m pytest tests/engine/test_verbs.py -k pc_yaml -q
```

Expect the new regression test (added by this feature, see tasks.md) to pass: it builds a real
chronicle layout (`chronicle.yaml`, empty `setting/`/`overlay/`/`entities/` directories, and a
`pc.yaml` at the chronicle root only) and asserts `verbs.session_context(...)["player_character"]`
is non-null and matches `pc.yaml`'s frontmatter.

## Manual verification (CLI, matching how a real chronicle is queried)

```bash
tmp=$(mktemp -d)
mkdir -p "$tmp/setting" "$tmp/overlay" "$tmp/entities" "$tmp/log"
cat > "$tmp/chronicle.yaml" <<'YAML'
schema_version: 1
name: quickstart-chronicle
engine: {repo: wyrd, version: 0.0.0}
setting: {repo: wyrd-setting-quickstart, version: 0.0.0}
YAML
cat > "$tmp/pc.yaml" <<'YAML'
---
id: pc-quickstart
type: character
role: player
name: Quickstart Character
status: drafted
---
A character used only to verify session-context.
YAML

WYRD_PKG_DIR=$(find engine -maxdepth 4 -type d -name wyrd | head -1)
PYTHONPATH="$(dirname "$WYRD_PKG_DIR")" python3 -m wyrd.client session-context --chronicle-dir "$tmp"
```

**Expected**: the JSON result's `player_character` field is `pc-quickstart`'s frontmatter, not
`null`. Nothing under `"$tmp/entities"` was ever written — confirming `pc.yaml` alone is
sufficient (User Story 1, SC-001).

```bash
PYTHONPATH="$(dirname "$WYRD_PKG_DIR")" python3 -m wyrd.client get pc-quickstart --chronicle-dir "$tmp"
PYTHONPATH="$(dirname "$WYRD_PKG_DIR")" python3 -m wyrd.client find --type character --chronicle-dir "$tmp"
```

**Expected**: `get` resolves `pc-quickstart` (User Story 2, SC-002); `find --type character`
lists `pc-quickstart` among its results.

```bash
rm -rf "$tmp"
```
