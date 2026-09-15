# Contract: chronicle-level CLI verbs

Each verb below is registered in `engine/wyrd/catalog.py`'s `TOOLS` registry (the
`find-noun`/`find-rule`/`find-table` pattern, #397/PR #398), dispatched through
`client.py`'s existing argparse-from-`TOOLS` mechanism, and implemented as a thin wrapper in
`engine/wyrd/verbs.py` calling the pure functions named in research.md. Every verb returns
structured JSON to stdout (spec.md FR-012); errors go to stderr with a non-zero exit code.

| Verb | CLI form | Required args | Optional args | Errors |
|---|---|---|---|---|
| `session-context` | `wyrd session-context` | — | — | chronicle/entities fail to load |
| `get` | `wyrd get <id>` | `id` | — | `id` does not resolve |
| `find` | `wyrd find --type T` | `--type` | `--status`, `--tag` | none (empty result is not an error) |
| `party` | `wyrd party` | — | — | none |
| `threads` | `wyrd threads` | — | — | none |
| `threats` | `wyrd threats` | — | — | none |
| `log` | `wyrd log --last N` or `wyrd log --since <beat>` | one of `--last`/`--since` | — | both or neither of `--last`/`--since` given |
| `save` | `wyrd save` | — | `--path` | validation failure |
| `load` | `wyrd load` | — | `--path` | file missing/corrupt (state.StateError) |
| `validate` | `wyrd validate` | — | `--path` | reports violation, does not raise |
| `recap` | `wyrd recap` | — | `--where`, `--changes`, `--body-mind` | none |
| `advance-time` | `wyrd advance-time <days>` | `days` | `--seed` | negative `days` |
| `threat-check` | `wyrd threat-check <id>` | `id` | `--seed` | unknown threat id |

`doctor` and `optimise` are explicitly not part of this contract (deferred,
docs/design/28-maintenance.md).
