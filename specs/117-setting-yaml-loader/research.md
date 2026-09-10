# Phase 0 Research: setting.yaml loader and validator

## Unknown 1 — how does the engine expose its own version, for the `requires_engine` check?

**Decision**: Add a single `__version__ = "0.1.0"` constant to `engine/wyrd/__init__.py`, and have
`check_setting.py` import it from there.

**Rationale**: Grepped the whole `engine/wyrd/` tree — no `__version__`, `VERSION`, or equivalent
exists anywhere today. `docs/design/29-evolution.md` and `24-authoring-a-setting.md` both already
assume the engine has a version a chronicle pins against; nothing currently supplies it. `0.1.0` is
consistent with `docs/design/24-authoring-a-setting.md`'s own worked example
(`requires_engine: ">=0.1.0"`) and with semantic versioning's pre-1.0 convention for a project that
has not yet made a stability promise (CLAUDE.md: no capability lock-in stated elsewhere).

**Alternatives considered**:
- A `VERSION` file at the repo root, read at runtime. Rejected: adds a file-I/O dependency to a
  pure-function check for no benefit over a Python constant, and every other stdlib-only piece of
  this codebase (e.g. `state._SCHEMA_VERSION`) is a plain module constant.
- Deriving the version from git tags. Rejected: the repo has no tagging convention yet, and this
  would make the validator's output depend on the git history of whatever checkout it runs in —
  non-deterministic across clones, which violates docs/design/27-tooling.md's determinism
  principle.

## Unknown 2 — what syntax does `requires_engine` use, and how is it compared?

**Decision**: A minimal comparator syntax covering exactly what `docs/design/24-authoring-a-setting.md`'s
own example uses: `">=X.Y.Z"`, `"<X.Y.Z"`, `"==X.Y.Z"`, `">X.Y.Z"`, `"<=X.Y.Z"`, optionally
space-joined for a range (`">=0.1.0,<0.2.0"`). Implemented with a small stdlib tuple-comparison
function — no PEP 440 parser needed since the version space here is exactly `MAJOR.MINOR.PATCH`.

**Rationale**: The design doc only ever shows a single-sided `">=0.1.0"` example; no multi-clause
range appears anywhere in the design corpus. Keeping the comparator vocabulary small and explicit
(reject anything else as a malformed `requires_engine` field, per FR-002/FR-005's "reject
malformed" principle) avoids building an unused general-purpose version-range parser. Comma-joined
AND-of-clauses is included because it costs nothing extra and is the obvious future need (an upper
bound alongside a lower one) without speculating about syntax beyond that.

**Alternatives considered**:
- Depending on a PyPI `packaging`-style version-range parser. Rejected outright: stdlib-only,
  zero-dependency is non-negotiable (CLAUDE.md).
- Full PEP 440 syntax (pre-releases, wildcards, `~=`). Rejected as unwarranted scope — nothing in
  the design corpus uses or implies these, and the closed comparator set above already covers the
  one documented example plus the obvious range case.

## Unknown 3 — is `line` a closed vocabulary?

**Decision**: Free text (any non-empty string), not a closed engine vocabulary.

**Rationale**: `docs/design/24-authoring-a-setting.md` shows `line: fantasy` as its own worked
example without ever stating a closed list, unlike `armour`/`damage_type` which are explicitly
"the closed four" per ADR 0022. Treating `line` as free text is also the only choice consistent
with "the engine is setting-agnostic" (CLAUDE.md) — curating a fixed list of genres the engine
"knows about" would itself be exactly the kind of setting-flavoured coupling CLAUDE.md forbids.

**Alternatives considered**: A closed enum of genre labels. Rejected — no such list exists
anywhere in the design corpus, and inventing one would bake a setting-vocabulary assumption into
the engine, which CLAUDE.md explicitly forbids ("No setting or system names... Engine labels are
descriptive English").

## Unknown 4 — reuse `check_bestiary.py`'s reader, or write a new one?

**Decision**: Reuse. Import `read_yaml`/`YamlError` from `tools/check_bestiary.py`, exactly as
`tools/check_gear.py` already does (`from check_bestiary import YamlError, read_yaml`).

**Rationale**: Two independent restricted-YAML readers already exist in this repo before this
feature (`engine/wyrd/state.py`'s `parse_yaml`, and `tools/check_bestiary.py`'s `read_yaml`) —
`check_gear.py`'s existing import shows the established precedent for a *new* `tools/check_*.py`
script is to share `check_bestiary.py`'s reader rather than write a third one.

**Alternatives considered**: Writing a fresh reader in `check_setting.py`. Rejected — pure
duplication of `check_bestiary.py`'s ~70 lines for identical restricted-YAML semantics, and this
repo's CLAUDE.md already treats "two documents/pieces of code describing one thing differently" as
a recurring, hard-to-see fault class worth actively avoiding.
