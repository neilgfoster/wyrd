# Research: Chronicle friction harvest

No `NEEDS CLARIFICATION` markers remain in the Technical Context — this section records the
decisions taken and the alternative each rejected.

## Decision: How the harvest reads a chronicle repo's `log/friction.md`

**Decision**: Accept either a local filesystem path to a chronicle repo checkout, or an
`owner/repo` slug read via `gh api repos/<owner>/<repo>/contents/log/friction.md` (base64-decoded)
when no local checkout exists — mirroring `tools/backlog.py`'s existing `gh` subprocess pattern.

**Rationale**: An operator running the harvest from the `wyrd` meta repo will not always have
every chronicle repo checked out locally. `gh api` read access requires no local clone and no new
dependency beyond the `gh` CLI already assumed elsewhere in this repo's tooling (issue #95's own
Definition of Done explicitly allows `gh`/`kord` client calls where cross-repo access requires
them).

**Alternatives considered**:
- *Local checkout only*: simpler, but forces the operator to `git clone` every chronicle before
  harvesting, re-introducing exactly the manual friction issue #95 exists to remove.
- *A dedicated cross-repo library*: rejected as premature — one `gh api` call per repo is the
  entire cross-repo surface this feature needs; a library would add indirection with no present
  second caller.

## Decision: Triage implementation

**Decision**: Encode `docs/design/16-session.md`'s "What qualifies" three conditions as an
explicit, named Python predicate (`is_engine_gap(entry) -> bool | None`, returning `None` for "not
enough signal to decide" so those entries can be reported separately rather than silently
defaulted either way), not a free-text prompt to an LLM.

**Rationale**: `CLAUDE.md`'s "Deterministic over inference" rule, and the existing `dangling
mechanic` / `no_setting_vocabulary` checkers in `tools/` already establish the pattern of a
checkable predicate over prose rather than a model judgment call for this repo's own tooling.
Because the triage line is about substance ("did this touch a mechanic", "was there a gap"), a
literal keyword rule cannot fully replace judgment — so the predicate flags an entry as
"qualifies" (mechanic-shaped language plus a concrete finding), "does not qualify" (only if the
entry's `what happened`/`what the GM did` text names no rule, table, or mechanic at all), or
"needs review" for everything in between, and only "qualifies" entries proceed automatically to a
proposal — "needs review" entries are reported, not silently discarded, so a genuine gap is never
lost to an over-eager filter.

**Alternatives considered**:
- *Full LLM triage per entry*: rejected — this script is meant to be a small, deterministic
  `tools/` script, run in a plain Python environment without model access, consistent with every
  sibling checker in `tools/`.
- *Accept every entry as a candidate, let dedup/operator review filter*: rejected — this would
  defeat FR-002 entirely and flood proposals with narrative color, the exact failure the spec's
  Edge Cases and SC-002 guard against.

## Decision: Duplicate detection

**Decision**: Shell out to kord's `client.py github-issue-dedup-check --repo neilgfoster/wyrd
--text "<proposal title+body>"` for each surviving candidate, exactly as `kord-template-harvest`
already does for its own synthesized suggestions (specs/057-harvest-dedup in the kord repo).

**Rationale**: Reusing an existing, deterministic primitive is both `CLAUDE.md`'s own rule and
avoids re-implementing keyword/skill-name/file-path overlap matching that already exists and is
tested elsewhere. It also keeps this feature's own footprint to a thin caller, matching the
"Deterministic over inference" note under "Recurring faults worth checking for."

**Alternatives considered**:
- *No dedup at all*: rejected — User Story 3 and FR-004/FR-010 exist specifically because a
  re-invocable harvest without dedup degrades into a duplicate generator, the exact failure mode
  `kord-template-harvest`'s own dedup step was added to prevent.
- *A local "already proposed" ledger file*: rejected per FR-010's own reasoning — a local ledger
  can drift from what is actually filed/closed on the board; the dedup check against live issues
  is the single source of truth.

## Decision: Where the script lives and how it is invoked

**Decision**: `tools/harvest_friction.py`, invoked as
`python3 tools/harvest_friction.py --chronicle <path-or-owner/repo> [--chronicle ...]`, printing a
human-readable report of proposals (new + likely-duplicate) to stdout; no flag files anything to
GitHub itself.

**Rationale**: Matches every existing `tools/*.py` script's shape (a CLI entry point under
`if __name__ == "__main__":`, testable functions importable by `tools/test_harvest_friction.py`)
and issue #95's explicit "Python 3.11+, stdlib only, consistent with `tools/`'s existing scripts"
constraint.

**Alternatives considered**:
- *A new `.claude/skills/` skill instead of a `tools/` script*: rejected — the issue asks for "a
  repeatable harvest step" analogous to `kord-template-harvest`'s deterministic Python core, not
  a model-driven skill; a plain script is more testable and matches the repo's own convention of
  putting checkable logic in `tools/` and letting a skill (if ever wanted) wrap it later.
