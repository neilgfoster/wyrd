# Phase 0 research: Engine scaffolding

No `[NEEDS CLARIFICATION]` markers remained after `/speckit-specify`/`/speckit-clarify` — the
Technical Context's unknowns were all already settled by existing design documents rather than
open questions for this feature. This file records those decisions and their sources so a later
reader doesn't have to re-derive them.

## Language and dependencies

- **Decision**: Python 3.11+, standard library only.
- **Rationale**: `docs/design/27-tooling.md` section 2 states this as a repo-wide constraint
  ("stdlib-only, zero-dependency, zero-backend") for everything under `engine/` — not a choice
  this feature makes, a constraint it inherits.
- **Alternatives considered**: None evaluated — the constraint is explicit and repo-wide.

## Package layout

- **Decision**: `engine/wyrd/` with `catalog.py`, `client.py`, `verbs.py`, `rules.py`,
  `state.py`, `render.py` — this feature's slice of the full shape `27-tooling.md` section 3
  specifies (that section also names `tables.py`, `calendar.py`, `campaign.py` for later
  features).
- **Rationale**: The layout, module names, and responsibilities are already specified in
  `docs/design/27-tooling.md` section 3, down to "a single tool catalog drives everything" and
  each module's one-line purpose. Following it exactly avoids inventing a competing shape a
  later feature would then have to reconcile against the design doc.
- **Alternatives considered**: A flatter `engine/` with no `wyrd/` subpackage was rejected —
  section 3's tree explicitly nests under `engine/wyrd/`.

## CLI dispatch mechanism

- **Decision**: `argparse`, built from the `TOOLS` catalog in `catalog.py` (one dict per verb;
  `client.py` iterates it to build subcommands), matching the "single tool catalog drives
  everything" principle from `27-tooling.md` section 3 — `describe` and dispatch read the same
  data so they cannot drift.
- **Rationale**: stdlib-only requirement rules out third-party CLI frameworks (click, typer).
  `argparse` is the standard library's own answer and is sufficient for a small, flat verb set.
- **Alternatives considered**: A hand-rolled `sys.argv` parser was rejected as needless
  reinvention of what `argparse` already does correctly (help text, error messages, type
  coercion).

## Dice primitive

- **Decision**: `rules.roll_d100(seed: int | None = None) -> int`, using stdlib `random.Random`
  (a locally-seeded instance, not the module-level global) so a seed never has side effects on
  unrelated calls.
- **Rationale**: `random.Random(seed)` gives exactly the reproducible-given-a-seed /
  genuinely-random-without-one behavior spec FR-001-003 require, with no dependency.
  A local instance (rather than `random.seed()` on the global) avoids one roll's seed silently
  affecting the next unrelated roll in the same process — a correctness property the spec's
  edge cases imply (rolls must not interfere with each other) even though it doesn't name it
  explicitly.
- **Alternatives considered**: `secrets` module was considered for the unseeded path (true CSPRNG
  randomness) but rejected — dice fairness only needs a good PRNG, not cryptographic
  unpredictability, and `secrets` has no reproducible-seed mode, which the seeded path needs.

## State persistence and atomic writes

- **Decision**: write-to-temp-file-then-`os.replace()` in the same directory, then load by
  reading and parsing normally. State shape for this feature is a minimal YAML-like mapping
  (see data-model.md) parsed with Wyrd's restricted internal reader, not a third-party YAML
  library.
- **Rationale**: `docs/design/27-tooling.md` section 1 explicitly rules out a third-party YAML
  dependency ("No third-party YAML dependency"); `docs/design/02-architecture.md` describes state
  as "YAML with `[[wikilink]]` frontmatter, parsed by a small internal reader." `os.replace()` is
  atomic on POSIX and Windows for same-filesystem renames, which is what FR-007's
  no-partial-write guarantee needs.
- **Alternatives considered**: `pathlib.Path.write_text()` directly onto the target path was
  rejected — a process killed mid-write would leave a truncated, unparseable file, violating
  FR-007. A full-blown YAML parser (PyYAML) was rejected — it's a third-party dependency, ruled
  out by section 2 above.

## Testing framework

- **Decision**: stdlib `unittest`.
- **Rationale**: `docs/design/27-tooling.md` section 6 states this explicitly — "stdlib
  unittest. No pytest." — and every existing test file under `tools/` already follows it.
- **Alternatives considered**: `pytest` was considered (more ergonomic fixtures/parametrization)
  but rejected — it would be the first third-party dependency in the repo, in direct conflict
  with the stated constraint.
