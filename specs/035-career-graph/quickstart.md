# Quickstart: Career graph — skill counts and succession

Documentation-only feature; there is no running system to start. This is the validation guide
for the decisions this feature makes.

## Prerequisites

- A checkout of this repository on branch `035-career-graph`.
- `python3` available (for `tools/check_docs.py`).

## Validate the doc graph stays whole

```bash
python3 tools/check_docs.py
```

Expected: passes with no dead links — in particular, the cross-reference from
`docs/design/11-character-creation.md` to the career graph must resolve to real content in
`docs/design/24-authoring-a-setting.md` (FR-007, SC-003).

## Worked example: prove the shape resolves eligibility and completion unambiguously

This is the manual proof for SC-001 and SC-002 — write it out on paper (or as a scratch
`careers.yaml` fragment) and confirm every step below is answerable with no guessing.

1. Declare three careers per the shape in [`data-model.md`](data-model.md):
   - `apprentice`: `entry: true`, `skills: [craft, appraise]`
   - `sailor`: `entry: true`, `skills: [rope, navigate]`
   - `master`: `entry: false`, `prerequisites: [apprentice, sailor]`, `skills: [craft, appraise, teach]`
2. **A new character at creation** may choose `apprentice` or `sailor` (both entry careers) but
   not `master` (neither listed prerequisite is complete for a character who does not exist
   yet) — SC-002 resolves this to a clear "no."
3. **A character who has spent advances** opening `craft` and `appraise` under `apprentice`,
   but not yet raised both to `apprentice`'s cap, has `apprentice` **in progress**, not
   complete. `master` is still not eligible (`sailor` was never started either) — SC-002 again
   resolves to "no," not "maybe."
4. **A character who has raised both `craft` and `appraise` to `apprentice`'s cap** has
   completed `apprentice`: they gain the +1 maximum Stamina bonus (once), and `master` is now
   eligible — SC-002 resolves to "yes," even though `sailor` was never touched. This is OR
   semantics: completing *any one* listed prerequisite is enough (a **specialist** path).
5. **A different character instead completes `sailor`** (never touching `apprentice` at all) —
   `master` is eligible for them too, by the same rule. Two characters can each become eligible
   for `master` by completely different routes, which is the mechanism a **generalist** career
   path relies on: nothing in the graph forces every character reaching `master` through the
   same ladder.
6. **Confirm SC-004**: check that `docs/design/24-authoring-a-setting.md`'s prose description of
   `careers.yaml`'s expected shape names exactly the fields in this worked example (`entry`,
   `skills`, `prerequisites`) — no field appears in one document and not the other.

## Expected outcome

Every step above has exactly one correct answer, reachable without inventing a rule not already
stated in `docs/design/24-authoring-a-setting.md` or `docs/design/11-character-creation.md`.
