# Phase 1 Data Model: Award advances against the four session triggers

## Constants

| Name | Value | Source |
|---|---|---|
| `TRIGGERS` | `("learned", "drove", "practised", "endured")` | docs/design/03-rules.md §6 trigger table |
| `SESSION_ADVANCE_CEILING` | `3` | docs/design/03-rules.md §6, "1-3 per session" |

The trigger keys are lowercase forms of the design document's own labels. The engine names no
further trigger, and a setting cannot add one — the vocabulary is closed, the same way
`character.WOUND_EFFECT_KEYS` is.

## The award record

```yaml
triggers: []          # trigger keys already awarded this session, in award order
advances_unspent: 0   # the character's balance, carried across sessions
```

`advances_unspent` is the field docs/design/22-state.md already documents on the player
character; this record is the in-flight view of it plus the current session's used triggers. This
feature never writes a state file — the caller persists the returned record.

## `advancement.award_advance(trigger, record)`

Returns a new record on success; never mutates its argument.

**Success**: `{"awarded": True, "trigger": <key>, "record": {"triggers": [...], "advances_unspent": N+1}}`

**Refusal**: `{"awarded": False, "refusal": <key>, "error": "<prose>", "record": <unchanged>}`

| `refusal` | When |
|---|---|
| `unknown_trigger` | `trigger` is not one of the four |
| `already_awarded` | that trigger is already in `record["triggers"]` |
| `session_ceiling` | the session has already awarded `SESSION_ADVANCE_CEILING` advances |

Checked in that order: an unknown trigger is a caller mistake and is reported as one even at the
ceiling, and a repeat is reported as a repeat even at the ceiling — the more specific fault wins,
so a caller is never told "that is all this session pays" about a typo.

## `advancement.begin_session(record)`

Returns `{"triggers": [], "advances_unspent": <unchanged>}`. Awards do not carry across a session
boundary; the balance does.

## Verb and CLI surface

| Verb | CLI | Arguments |
|---|---|---|
| `award_advance` | `wyrd award-advance` | `--trigger`, `--awarded` (repeatable, the triggers already used), `--advances-unspent` |
| `begin_session` | `wyrd begin-session` | `--awarded` (repeatable), `--advances-unspent` |

The CLI passes the record in as flags rather than reading a state file, matching every other verb
in `client.py`: the engine computes, the caller persists.
