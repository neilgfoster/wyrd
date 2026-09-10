# Quickstart: Lazy Conversion Lifecycle

```python
from wyrd import entity

# Stub sufficiency -- summary is the entity's body text, per 18-arcs-and-beats.md's stub example
frontmatter = {
    "id": "beat-ambush", "type": "beat", "name": "Ambush at the Ford",
    "setting": "example", "status": "stub",
    "tags": ["combat", "travel"],
    "sources": [{"work": "Corpus Vol. 3", "licence": "internal", "path": "corpus/vol3.md"}],
}
body = "A river crossing goes wrong."
entity.check_stub_sufficiency(frontmatter, body)  # {"valid": True}

# Source record schema (pages required once past stub)
entity.validate_source({"work": "Corpus Vol. 3", "licence": "internal", "path": "corpus/vol3.md"},
                        status="stub")      # {"valid": True} -- pages not required yet
entity.validate_source({"work": "Corpus Vol. 3", "licence": "internal", "path": "corpus/vol3.md"},
                        status="drafted")   # {"valid": False, "error": "..."} -- pages required

# Legal transitions
entity.legal_transition("stub", "drafted")     # {"valid": True}
entity.legal_transition("stub", "complete")    # {"valid": False, "error": "skips a state"}
entity.legal_transition("complete", "stub")    # {"valid": False, "error": "moves backward"}

# Stub ratio report
entities = {"a": {"status": "stub"}, "b": {"status": "drafted"}, "c": {"status": "complete"}}
entity.status_counts(entities)
# {"stub": {"count": 1, "proportion": 0.333...}, "drafted": {...}, "complete": {...}}
```
