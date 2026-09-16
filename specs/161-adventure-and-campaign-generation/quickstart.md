# Quickstart: validating this specification

This feature ships no code (see plan.md's Summary), so there is nothing to run. What follows is
how a *future implementing feature* would validate that it satisfies this spec — kept here so
that feature's own quickstart isn't invented from scratch.

## Validating the specification itself (do this now)

1. Read `spec.md`'s three acceptance criteria against the corresponding FRs:
   - Input contract per scale → FR-001–FR-006, `data-model.md`'s `GenerationRequest` table.
   - Anti-inflation as checkable rules → FR-007–FR-011, each naming a specific field/comparison.
   - Commit-back path, no fork → FR-012–FR-015, `data-model.md`'s "Committed entity" section,
     `contracts/generation-request.md`'s `accept` behaviour (same functions, not equivalent ones).
2. Run `python3 tools/check_docs.py` and `python3 -m ruff check . && python3 -m ruff format
   --check .` — this feature added no `docs/design/` files and no Python, so both should report
   no new findings; confirms the spec-only deliverable didn't accidentally touch either surface.

## Validating a future implementation against this spec

1. **Scale coverage** (SC-001): for each of `beat`, `arc`, `campaign-spine`, construct a
   `GenerationRequest` per `data-model.md` and confirm the implementation rejects one missing a
   required field for that scale/mode combination.
2. **Anti-inflation checks** (SC-002): construct one `GenerationRequest`/candidate pair per
   FR-007–FR-011 designed to violate exactly that rule, and confirm `generate` returns a
   `GenerationResult` whose `checks` list marks it `reject` for that rule and no other.
3. **Commit-back, no fork** (SC-003): before and after calling `accept` on an accepted result,
   diff the chronicle's `threads:`/threat entity files; confirm the only change matches an
   ordinary authored beat's consume/emit, and confirm (by reading source, not just output) that
   `accept`'s implementation calls the existing `campaign.py` functions rather than new ones.
4. **Model tiering** (SC-004): audit the implementation's four processing steps
   (`contracts/generation-request.md`'s `generate` Processing list) against
   `27-tooling.md` §5's table — confirm steps 1/2/5 make no model call, step 3 calls only the
   Haiku-tier agent, and step 4 is the only call to the capable model.
5. **Setting-authoring gate** (SC-005): call `generate` with `mode: setting-authoring` and
   `invention_permitted` absent; confirm a structured error is returned and no entity, thread, or
   file is written anywhere.
