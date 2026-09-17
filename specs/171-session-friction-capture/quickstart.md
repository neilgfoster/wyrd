# Quickstart: Session friction capture

Validation guide for the convention this feature specifies. There is no running system to start
— the "feature" is a documented convention plus a design-document edit. Validate as follows.

## Prerequisites

- A checkout of this repo with the edited `docs/design/16-session.md`.
- `python3` on PATH (for `tools/check_docs.py`).

## 1. Confirm the doc edit is internally consistent and reachable

```bash
python3 tools/check_docs.py
```

Expected: exits 0 (or reports only pre-existing, unrelated issues) — confirms
`docs/design/16-session.md` stays reachable from `README.md` and introduces no dead links.

## 2. Confirm the convention reads correctly against spec.md's acceptance scenarios

Read the new section of `docs/design/16-session.md` and check by hand against spec.md's User
Stories:

- **File location** (FR-001): the document names `log/friction.md` inside a chronicle repo's
  `log/` directory as the friction log's location.
- **Entry format** (FR-002/FR-003): the document gives the three required fields (mechanic/table
  implicated, what happened, what the GM did) and shows one complete worked example.
- **Triage line** (FR-004): the document states, verbatim or in equivalent plain language, the
  three qualifying conditions and gives one example each of a qualifying friction note and a
  non-qualifying color note (per issue #94's acceptance criteria).
- **Solo play** (FR-005/User Story 3): nothing in the wording assumes a second real participant.
- **Setting-agnostic** (FR-009): grep the new section for any setting name or borrowed term.

```bash
grep -niE "setting-name-placeholder" docs/design/16-session.md   # replace with a real setting name check if one is known
```

(In practice: visually confirm no setting vocabulary appears — there is no closed list to grep
against, since the whole point is that none should be there.)

## 3. Worked-example self-check (SC-004)

Take two invented moments and check which the documented triage line accepts:

1. **Qualifying**: "The difficulty table gave a result the GM had not expected for an
   opposed test with a 65% skill against a 40% skill — the GM ruled it as written but noted the
   surprise." → Should be recorded per the triage line's second condition (a correctly-applied
   mechanic producing a result that felt wrong).
2. **Non-qualifying**: "The player described their character's coat catching on a nail on the
   way out the door." → Should NOT be recorded — ordinary narrative color, no rules question
   involved.

Confirm the documented triage line, read literally, sorts these two the same way.

## Expected outcome

`tools/check_docs.py` passes, and a reader unfamiliar with this issue can, from
`docs/design/16-session.md` alone, state where a friction note goes, what it contains, and
whether a given moment warrants one — without needing to read spec.md or issue #94.
