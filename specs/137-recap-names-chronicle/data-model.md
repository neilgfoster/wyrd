# Data Model: Recap names its chronicle and setting

## `generate_recap` change

No new parameters — `chronicle: dict` is already accepted. Reads:

| Field | Fallback |
|---|---|
| `chronicle.get("name")` | `_RECAP_PLACEHOLDER` |
| `chronicle.get("setting", {}).get("repo")` | `_RECAP_PLACEHOLDER` |

New output section, inserted after `# Recap` and before `## Where and when`:

```
## Chronicle
<name> in <setting>
```
