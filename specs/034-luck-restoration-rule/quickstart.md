# Quickstart: validating the Luck restoration rule

This feature is documentation-only — there is no code to run. Validation is reading the changed
text against the acceptance scenarios in [spec.md](./spec.md) and running the repo's existing
document checks.

## Prerequisites

- A checkout of this branch (`034-luck-restoration-rule`).

## Steps

1. **Read the rule in isolation** (SC-001): open `docs/design/03-rules.md` §1 (Luck) alone, with
   no other document open. Confirm you can answer: "A character spent Luck last arc — do they
   have it back now?" without inferring anything.
2. **Cross-check against the campaign structure** (spec.md Acceptance Scenario 2): open
   `docs/design/19-campaign.md` and confirm the "arc" the Luck rule resets on is the same
   top-level arc boundary that document defines — not a different or unstated notion of "arc."
3. **Run the document graph check**:

   ```bash
   python3 tools/check_docs.py
   ```

   Expect a clean pass — no broken links, no orphaned document, no ADR index gap (SC-002).
4. **Confirm the decision is recorded as an ADR** (SC-003): `docs/adr/` contains a new, numbered,
   dated entry for this decision, distinct from the `03-rules.md` prose it justifies, and the ADR
   index (checked by `tools/check_docs.py`) lists it.

## Expected outcome

`docs/design/03-rules.md` §1 states the restoration rule explicitly; `tools/check_docs.py` passes;
one new ADR exists under `docs/adr/` recording the decision and the rejected alternative.
