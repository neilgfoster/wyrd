# CLI Contract: Setting Overrides Mechanism

Extends `specs/075-engine-scaffolding/contracts/cli.md`'s existing `describe`/verb-dispatch
contract. Structured JSON is the default; `--format text` renders each shape below to one line.

## `describe --overridable`

```
python3 -m wyrd.client describe --overridable
```

Output:

```json
{"verb": "describe", "overridable": [
  {"name": "oracle-prompt-complication", "kinds": ["extend", "tables"], "depends_on": []},
  {"name": "skills", "kinds": ["extend"], "depends_on": []},
  {"name": "taint", "kinds": ["disable", "rename"], "depends_on": []},
  {"name": "trauma", "kinds": ["disable", "rename"], "depends_on": []},
  ...
]}
```

`--name` is ignored when `--overridable` is given -- the two are mutually exclusive concerns.

## `describe [--name <verb>] [--setting <path>] [--chronicle <path>]`

`--setting` loads a `setting.yaml`, resolves its `overrides:` block against the engine defaults,
and filters the returned catalog by the result. `--chronicle` layers a further `houserules.yaml`
on top (requires `--setting` to be meaningful, though it is accepted alone -- resolved as
`engine -> chronicle` if `--setting` is omitted).

Success: identical shape to plain `describe`/`describe --name`, but `tools` (or the single named
entry) reflects the resolved configuration -- a wholly-disabled tool is absent; a partially
disabled one has its `mechanisms` (and any `mechanism` input enum) narrowed.

Failure (an override names something outside the closed set, or a layer widens what an earlier
layer disabled):

```json
{"error": {"verb": "describe", "reason": "setting: 'not-a-mechanism' is not in the engine's overridable set"}}
```

## `track --value <int> --mechanism <name> --delta <int> [--setting <path>] [--chronicle <path>]`

Success:

```json
{"verb": "track", "mechanism": "taint", "label": "taint", "value": 4, "delta": 1}
```

`label` is `mechanism` unless a layer renamed it, in which case `label` carries the setting's
word while `mechanism` -- and every other engine-internal reference -- stays the identifier.

Failure shapes (both exit 0, per the CLI contract's "structured error, not a traceback" rule):

- `mechanism` not in `overrides.TRACKABLE_MECHANISMS`:
  `{"error": {"verb": "track", "reason": "'skills' is not a trackable mechanism"}}`
- `mechanism` disabled by the resolved configuration:
  `{"error": {"verb": "track", "reason": "'taint' is disabled by the active setting"}}`
- An override in `--setting`/`--chronicle` fails to load (outside closed set, or widens an
  earlier layer): `{"error": {"verb": "track", "reason": "<OverrideError message>"}}`
