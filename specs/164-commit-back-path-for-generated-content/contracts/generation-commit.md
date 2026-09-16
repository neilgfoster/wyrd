# Contract: the commit-back functions

`engine/wyrd/generation_commit.py` — two public functions, `accept_result` and `reject_result`,
plus a private thread/threat dispatch helper. Neither public function raises for a well-formed
`result` (matching `generation.py`/`generation_checks.py`'s report-don't-raise convention);
malformed structural input (e.g. a `thread_updates`/`threat_updates` entry naming an id absent
from the caller-supplied lookup maps) raises `ValueError`, matching `thread.py`/`threat.py`'s own
validation style for exactly this class of caller error.

```python
def can_commit(result: dict) -> bool:
    """True only when result['checks'] is non-empty and every entry's outcome is 'pass' or
    'narrowed' (data-model.md's Commit outcome). False for an empty checks list (FR-006: treated
    as not yet evaluated) or any 'reject' entry."""

def reject_result(result: dict) -> dict:
    """FR-005 (the explicit-decline half). Always returns {"committed": False, "reason":
    "declined"} -- never inspects result['checks'], never performs I/O, never calls a thread/
    threat mutation function, regardless of what result itself contains."""

def accept_result(
    result: dict,
    *,
    entity_id: str,
    entity_type: str,          # "arc" or "beat" only (FR-012)
    name: str,
    setting: str,
    mode: str,                 # generation.MODES: "live-play" | "setting-authoring"
    body: str,
    path: pathlib.Path,
    parent: str | None = None,
    entry: dict | None = None,
    exit: dict | None = None,
    tags: list[str] | None = None,
    thread_updates: list[dict] | None = None,
    threat_updates: list[dict] | None = None,
    live_threads: dict[str, dict] | None = None,
    live_entities: dict[str, dict] | None = None,
) -> dict:
    """FR-012/FR-013 (the accept half). When can_commit(result) is False, returns {"committed":
    False, "reason": "checks_failed", "detail": [...]} with no I/O and no mutation (FR-015's
    'checks reject it' half) -- entity_type/name/setting/body/path/parent/entry/exit/tags are not
    even inspected in that case.

    Otherwise:
    1. Builds frontmatter via entity.py's common schema: id, type (must be 'arc' or 'beat'),
       name, setting, status: 'drafted' (never 'stub' -- FR-012), tags, sources (exactly one
       entry of data-model.md's generated shape: {generated: true, mode: the caller-supplied
       mode, consumed: result['consumed']} -- mode is a caller-supplied argument, not read off
       result, since a GenerationResult does not itself carry the originating request's mode),
       parent, entry, exit.
    2. Validates the built frontmatter with entity.validate and, if entry/exit are given,
       arc_selection.validate_entry_exit -- a build that fails either is a caller error
       (ValueError), not a silent partial write.
    3. Writes the entity via state.save_entity(frontmatter, body, path) -- the same function
       every other entity write in this codebase uses.
    4. Applies every thread_updates entry (data-model.md) via thread.new_thread or thread.touch,
       and every threat_updates entry via threat.promote (entity_id is None) or a direct
       imminence/ambient mutation on the looked-up entity (entity_id is not None) -- in that
       order, after the entity file is already on disk, so a mutation failure never leaves a
       half-written entity with no corresponding file.
    5. Returns {"committed": True, "path": path, "entity": frontmatter, "threads": <updated
       live_threads>, "entities": <updated live_entities>} -- the caller owns persisting any
       thread/threat entity file changes this step produced; accept_result itself only writes the
       one new arc/beat file (matching every other engine/wyrd/* module's pure-data-in,
       pure-data-out contract for anything beyond the one file write FR-012 itself requires).

    Never mutates or reopens an existing entity file (FR-014, FR-007 of this feature's own spec):
    accept_result only ever writes to `path`, which the caller is responsible for choosing as a
    fresh, not-yet-existing location.
    """
```

## Error shapes

| Condition | Behaviour |
|---|---|
| `result['checks']` empty, or contains a `reject` entry | `accept_result` returns `{"committed": False, "reason": "checks_failed", ...}` — no exception, no I/O |
| caller calls `reject_result` | always `{"committed": False, "reason": "declined"}` — no exception, no I/O, regardless of `result`'s own content |
| `entity_type` not `"arc"`/`"beat"` | `ValueError` — a caller error, since #422 scopes this feature to those two types only |
| built frontmatter fails `entity.validate`/`arc_selection.validate_entry_exit` | `ValueError` naming the specific problem — no partial write |
| a `thread_updates`/`threat_updates` entry names an id absent from `live_threads`/`live_entities` | `ValueError` — see data-model.md's Validation rules |

## Consumer contract

The (not-yet-built) generation pipeline (#422's sibling) calls `can_commit`/`accept_result`/
`reject_result` directly once it has assembled a `GenerationResult` and run it through
`generation_checks.run_checks`. This feature does not itself decide *when* a result is offered
for acceptance versus decline — that UX/orchestration decision belongs entirely to that sibling
feature.
