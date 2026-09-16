# Quickstart: verify a proposal survives across separate CLI invocations

## Prerequisites

- A chronicle directory (or, for a minimal check, any directory containing at least one entity
  file `wyrd propose` can target) as the current working directory for both commands below.
- `engine/` on `PYTHONPATH` (as the repo's own tests already require).

## Run

```bash
cd <chronicle-or-scratch-dir>
PYTHONPATH=<repo>/engine python3 -m wyrd.client propose \
  --actor entities/senna-vask.md --mechanic exposure --skill bargaining --tier moderate --seed 20260852
# → prints {"verb": "propose", "proposal_id": "p-...", "roll": {...}, "mutations": [...], "steps": [...]}
# note the proposal_id from the output, e.g. p-3a91f0c218ab
```

Then, as a **second, separate** process (this is the property under test — not two calls in one
Python session):

```bash
PYTHONPATH=<repo>/engine python3 -m wyrd.client commit p-3a91f0c218ab
# → {"verb": "commit", "proposal_id": "p-3a91f0c218ab", "mutations": [...]}
```

## Expected outcome

- `entities/senna-vask.md`'s `taint` field on disk reflects the staged mutation, exactly as it
  would had `commit` been called in the same process as `propose`.
- Re-running `commit p-3a91f0c218ab` a third time fails with
  `{"error": {"verb": "commit", "reason": "no open proposal: p-3a91f0c218ab"}}` — the id no
  longer resolves, whether the failure comes from a third process or the second one again.
- The equivalent sequence with `discard` in place of `commit` leaves `taint` untouched.

## Automated version

`tests/engine/test_resolution.py`'s new cross-process regression test runs exactly this sequence
via `subprocess.run` (two genuinely separate `python3 -m wyrd.client` invocations, not two
in-process calls) — see spec.md User Story 1's Independent Test.
