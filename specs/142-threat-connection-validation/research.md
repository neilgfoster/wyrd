# Research: Every seeded Threat carries a personal connection

No `[NEEDS CLARIFICATION]` markers remain in spec.md. One decision worth recording:

- **Decision**: `validate_connections` returns a `list[str]` of formatted problem messages
  (each naming the offending Threat's id), not a `list[dict]`/structured record.
  **Rationale**: matches `resolution._validate_proposal`'s own precedent (`ProposalError`
  naming the specific violation on the first one found) and `check_dangling_mechanics.py`'s
  `Problem` list convention — a plain string is sufficient for a caller to print, log, or count,
  and this feature's own acceptance criteria only ask for "reported by id," not a richer shape.
  **Alternatives considered**: raising `ValueError` on the first violation — rejected; FR-003
  explicitly requires reporting *every* violation in one pass, not stopping at the first, since
  a caller building a bootstrap-seed set wants the complete picture before deciding what to fix.
