# Implementation Plan: Career skill cap is one flat value, not a per-skill dict

**Branch**: `158-career-flat-cap` | **Date**: 2026-09-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/158-career-flat-cap/spec.md`

## Summary

`engine/wyrd/career.py`'s `effective_cap` and `career_complete` index `career["skills"]` as a
`{skill: cap}` dict, but every real setting's `careers.yaml` (and docs/design/03-rules.md's flat
70% rule) encode `skills` as a plain list of names with one flat cap applying to all of them. Fix
both functions to membership-test the list and apply a single named cap constant, correct the
now-stale "higher of the two" docstring language, fix the existing tests' synthetic
`{skill: cap}` fixtures to the real list shape, and add a regression test loaded from a real
setting's `careers.yaml`.

## Technical Context

**Language/Version**: Python 3.11, standard library only (engine/wyrd)

**Primary Dependencies**: none beyond the existing engine package; test loads real setting YAML
via PyYAML if already a project dependency, otherwise parses the specific fixture fields needed
without a new dependency (checked during implementation)

**Storage**: N/A (in-memory dicts/lists)

**Testing**: stdlib `unittest`, no pytest (docs/design/27-tooling.md section 6);
`tests/engine/test_career.py` and `tests/engine/test_advancement.py`

**Target Platform**: engine library, setting-agnostic

**Project Type**: library (engine/wyrd)

**Performance Goals**: N/A — pure logic fix, no performance-sensitive path

**Constraints**: ruff clean (line length 100, E/F/I/UP, target 3.11); no setting names leak into
`docs/design/`; rules.py constant, not a magic number, per issue's own suggested approach

**Scale/Scope**: two functions in `engine/wyrd/career.py`, their call sites in
`engine/wyrd/advancement.py` (unchanged signatures, just correct data now), one new named constant
in `engine/wyrd/rules.py`, and test fixture updates in `tests/engine/test_career.py` and
`tests/engine/test_advancement.py`

## Constitution Check

No `.specify/memory/constitution.md` gates apply beyond this repo's own CLAUDE.md rules (ruff
clean, Spec Kit gate for a capability change, deterministic-over-inference). This is a bug fix
restoring already-documented behavior — no new design decision is introduced, so no ADR is
warranted (CLAUDE.md's two-part ADR test: no real alternative is being rejected here, the fix
brings the code into line with an existing, undisputed design document).

## Project Structure

### Documentation (this feature)

```text
specs/158-career-flat-cap/
├── plan.md              # This file
├── tasks.md             # Phase 2 output (kord-feature-tasks)
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
engine/wyrd/
├── career.py            # effective_cap, career_complete: fix to flat-cap-over-list semantics
├── rules.py             # add CAREER_SKILL_CAP = 70 (or similarly named) constant
└── advancement.py        # unchanged signatures; verified against the fixed helpers

tests/engine/
├── test_career.py        # fix {skill: cap} fixtures to list-of-names shape; add real-setting test
└── test_advancement.py   # fix any {skill: cap} fixtures found there
```

## Approach

1. Add a named constant to `rules.py` (e.g. `CAREER_SKILL_CAP = 70`) with a docstring pointing at
   docs/design/03-rules.md section 6.
2. Rewrite `effective_cap(skill, career, ancestry=None)` to return `rules.CAREER_SKILL_CAP` if
   `skill` is a member of `career["skills"]` or (when given) `ancestry["skills"]`, else `None`.
   Correct its docstring to drop the "higher of the two" language.
3. Rewrite `career_complete(skills, career)` to read `career["skills"]` as a list and check
   `skills.get(name, 0) >= rules.CAREER_SKILL_CAP` for every name in it, preserving the existing
   empty-list-never-complete guard.
4. Grep `engine/wyrd/advancement.py` for any other direct indexing of `career["skills"]` as a
   dict (issue's own audit already found none beyond the two functions it names) and confirm no
   further call site needs changing.
5. Fix `tests/engine/test_career.py`'s and `tests/engine/test_advancement.py`'s `{skill: cap}`
   fixtures (e.g. `CAREER`, `GUARD`, `SOLDIER`, `GUARD_CAPTAIN`, ancestry fixtures) to the real
   list-of-names shape, adjusting each test's expected cap-related assertions to use the flat
   constant instead of the old per-skill numbers.
6. Add a new test that loads a real career entry from
   `wyrd-setting-darkfuture/setting/careers.yaml` (path resolved relative to the sibling checkout;
   skip gracefully with a clear message if that checkout isn't present in the environment running
   the test) and calls `effective_cap`/`validate_allocation`/`career_complete` against it,
   confirming no `TypeError` and correct flat-cap behavior.
7. Run `ruff check .` and `ruff format --check .` and the full `unittest` suite for
   `tests/engine/test_career.py` and `tests/engine/test_advancement.py` (plus the whole engine
   suite as a sanity check).

## Risks / Open Questions

- The sibling setting checkouts (`wyrd-setting-darkfuture`, `wyrd-setting-titan`) live outside
  this repo's own checkout tree, at a fixed relative path in this development environment
  (`/root/source/neilgfoster/wyrd-setting-darkfuture`). The regression test must not hard-fail in
  an environment where that checkout is absent (e.g. a bare clone of just `wyrd`) — it should skip
  with a clear reason rather than error, so CI-less local runs elsewhere don't break. This is
  a plain-file existence check, not a network fetch or hidden dependency.
