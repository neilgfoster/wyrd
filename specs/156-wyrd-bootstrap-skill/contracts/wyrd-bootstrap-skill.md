# Contract: `/wyrd-bootstrap` skill invocation

This feature introduces no new CLI verb or API — it is a Claude Code skill that composes
existing `wyrd.client` verbs. The "contract" here is the skill's own invocation shape and the
verb calls it is required to make, matching the format the three precedent skills
(`/wyrd-character`, `/wyrd-downtime`, `/wyrd-end-session`) already document in their own
`SKILL.md` files.

## Invocation

```
/wyrd-bootstrap
```

Invoked with no arguments, from the root of a chronicle repository where `./bootstrap` has
already run. Not invocable (per FR-002) when `chronicle.yaml` already exists, or when
`chronicle.yaml.json` does not exist.

## CLI verbs this skill calls

All located via the existing convention:

```bash
WYRD_PKG_DIR=$(find engine -maxdepth 4 -type d -name wyrd | head -1)
PYTHONPATH="$(dirname "$WYRD_PKG_DIR")" python3 -m wyrd.client <verb> [--flags]
```

| Verb | Purpose | Never |
|---|---|---|
| `create-character` | produce `pc.yaml`'s frontmatter from the player's career/advance/Loyalty/Drive/Misfortune/Fault-Line choices | recompute a skill percentage, Fate, or Stamina itself |
| `save` | validate and write the assembled chronicle state to `chronicle.yaml` | hand-write `chronicle.yaml`'s YAML directly |
| `validate` | confirm the written `chronicle.yaml` is schema-valid before committing (optional defence-in-depth; `save` already validates) | substitute for `save`'s own validation |

No verb exists (and none is added by this feature) for writing an entity/overlay file — those are
authored directly per docs/design/25-entities.md's plain frontmatter+prose schema, the same way a
human setting author writes one.

## Failure handling

- `create-character` returning a refusal/error: reported verbatim; no `pc.yaml` write, no further
  steps, no commit.
- `save` returning an `error`: reported verbatim; no commit. `chronicle.yaml.json` is left in
  place (not deleted) so a retry has the same starting point.
- Any step failing leaves the working tree exactly as `./bootstrap` left it, aside from whichever
  intermediate files were already written before the failing call — this skill does not attempt
  partial rollback of files it already wrote, since the completed-check (FR-002, presence of
  `chronicle.yaml`) only trips once `save` has actually succeeded.
