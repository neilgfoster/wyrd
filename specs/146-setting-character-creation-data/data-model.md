# Phase 1 Data Model: Setting-Level Character Creation Data

Five setting-data file shapes. `careers.yaml` is included because it is validated by this
feature's script even though its shape was already documented (`docs/design/24-authoring-a-setting.md`);
its schema is unchanged, restated here only for the validator's reference.

## `careers.yaml` (existing shape, newly validated)

```yaml
careers:
  - id: guard              # str, kebab-case, unique across the file
    entry: true             # bool
    skills: [blade, watch]  # list[str], non-empty
    # prerequisites: absent when entry: true
  - id: guard-captain
    entry: false
    prerequisites: [guard, soldier]   # list[str], non-empty when entry: false; OR semantics
    skills: [blade, watch, command]
```

**Rules**: `id`/`entry`/`skills` required on every entry. `entry: true` ⇒ no `prerequisites` key.
`entry: false` ⇒ `prerequisites` present, non-empty. Every `prerequisites` entry names an `id`
present elsewhere in the same file. At least one entry has `entry: true`. The `prerequisites`
graph is acyclic (a career is unreachable only if every path through its prerequisites
eventually requires itself). No duplicate `id`.

## `loyalties.yaml` (new)

```yaml
loyalties:
  - id: the-crown
  - id: the-old-faith
relations:
  - a: the-crown
    b: the-old-faith
    kind: strained          # strained | irreconcilable
```

**Rules**: `loyalties` non-empty, each entry has a unique `id`. `relations` may be empty or
absent (a setting with a single Loyalty declares no relations, per §4). Each relation's `a`/`b`
both name a declared Loyalty `id`, `a != b`, and `kind` is one of the two ADR 0015 relations. No
unordered pair `(a, b)` appears more than once (a pair declared as `{a: x, b: y}` and again as
`{a: y, b: x}` is the same duplicate).

## `drives.yaml` / `misfortunes.yaml` (new, same shape)

```yaml
drives:            # or `misfortunes:` in misfortunes.yaml
  - id: find-the-sister
    text: "Find my sister, wherever the roads have taken her."
```

**Rules**: non-empty list. Each entry has a unique `id` and a non-empty `text`. Content of `text`
is never validated — free prose, per Assumptions in `spec.md`.

## `names.yaml` (new)

```yaml
cultures:
  - id: riverfolk
    given: [Mara, Toln, Isbet]
    family: [Ashwell, Dray]
    place: [Ottersmere, Cray's Ford]
```

**Rules**: `cultures` non-empty. Each culture has a unique `id` and at least one of
`given`/`family`/`place` present and non-empty (a culture that names no one at all fails §4's "at
least enough to name a person" requirement).

## `ancestries.yaml` (new, optional)

```yaml
ancestries:
  - id: hill-kin
    skills: [climb, forage]
```

**Rules**: file itself is optional; absence is not an error. When present, `ancestries`
non-empty, each entry has a unique `id` and a non-empty `skills` list — the same shape as a career
entry minus `entry`/`prerequisites` (an ancestry is never an entry point and has no prerequisite
chain, per §3 and ADR 0040).

## Validator output contract

`tools/check_character_creation_data.py <setting-dir>` reports one line per failure, naming the
file and the specific problem (mirrors `check_bestiary.py`), and a summary of which files were
found/validated/absent-and-optional. Exit code 0 only when every present-and-required file is
free of failures; a required file missing entirely is itself a failure. `--format json` mirrors
`check_setting.py`'s existing flag for machine consumption.
