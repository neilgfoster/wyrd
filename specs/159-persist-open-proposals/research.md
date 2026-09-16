# Phase 0 Research: Proposals survive across separate CLI invocations

## Decision 1 — Where a proposal's full contents live on disk

**Decision**: One JSON file per open proposal, named `<proposal_id>.json`, under a fixed,
cwd-relative directory `log/proposals/` — a sibling of the chronicle's existing `log/` directory
(docs/design/22-state.md's directory tree). The directory is an optional keyword parameter
(`proposals_dir`, default `DEFAULT_PROPOSALS_DIR = pathlib.Path("log/proposals")`) threaded
through `propose`/`propose_batch`/`commit`/`discard`/`reroll`, mirroring exactly how `state.py`
already defaults `DEFAULT_CHRONICLE_PATH`/`DEFAULT_STATE_PATH` to a cwd-relative path and lets a
caller (or a test) override it.

**Rationale**:
- `resolution.py`'s own functions take entity file paths (`actor`, `target`), never a "chronicle
  root" argument, and `commit`/`discard`/`reroll` take only a bare `proposal_id` — there is no
  path available at those call sites to derive a chronicle root from (`_find_chronicle_root`
  exists but only runs *after* a proposal is already loaded, when validating it against chronicle
  entities). A fixed, overridable, cwd-relative default is the only way to find the same file from
  a wholly separate process without inventing a proposal_id-to-chronicle-directory registry.
  Every real CLI invocation already runs with cwd set to the chronicle directory (that's what lets
  `chronicle.yaml`'s own default relative path resolve correctly today), so this is not a new
  convention — it is the same one, applied to one more file.
- A JSON file per proposal (rather than one shared file holding every open proposal) means
  `commit`/`discard` never need to read-modify-write a file some other in-flight proposal might
  also be about to touch, and deleting the file *is* invalidating the id — no separate "open"
  flag to keep in sync with the file's own existence.
- Reusing `state.write_text_atomic` (rather than `character.save_entity`/`state.save_chronicle`,
  which validate YAML entity/chronicle schemas that a proposal record is neither) is the direct
  reuse the issue asks for: same atomic-write guarantee, applied to `json.dumps`'s output instead
  of `dump_yaml`'s.

**Alternatives considered**:
- *Embed the full proposal in `chronicle.yaml`'s `pending.rolled` field.* Rejected: `pending.rolled`
  already has a settled, narrow shape (docs/design/22-state.md: "the one place an open proposal
  lives" for *session-interruption* purposes) — it is read by `chronicle.resume_state` as a bare
  id to report back to the operator, not as a data structure a cascade's `steps`/`mutations`/
  `depends_on` graph would need to be unpacked into and back out of every Rally/read. Overloading
  it would also mean every chronicle-state read (`wyrd doctor`, any status query) parses a
  proposal's internal shape whether or not one is even open.
- *One shared `log/proposals.json` holding every open proposal, keyed by id.* Rejected: forces
  every `propose`/`commit`/`discard`/`reroll` call to read-modify-write the *whole* file even when
  only one proposal is involved, and reintroduces exactly the "more than one thing touching the
  same file" hazard atomic writes exist to avoid when nothing requires it — FR-009 (one open
  proposal per actor) already bounds the *count* of files that can accumulate.
- *Derive the directory from the actor's own entity path at `propose` time, and have `commit`/
  `discard`/`reroll` search for the file by id.* Rejected: `commit`/`discard`/`reroll` have no
  actor path to search from either — this doesn't remove the need for a fixed, known location,
  it just relocates the guess to "search everywhere," which is worse, not better.

## Decision 2 — Proposal id generation must survive a fresh process's own counter reset

**Decision**: Generate `proposal_id` as `f"p-{uuid.uuid4().hex[:12]}"` instead of the current
`itertools.count(1)`-based `f"p-{next(_proposal_ids)}"`.

**Rationale**: `_proposal_ids = itertools.count(1)` is a module-level counter that restarts at 1
every time the Python process starts. Once persistence makes a proposal file outlive its
process, two *separate* `propose` invocations (the exact scenario this feature exists for) would
both mint `p-1` as their first id in their own process, and the second `propose`'s on-disk write
would silently clobber the first's still-open file. A random, collision-resistant id removes the
need to coordinate a shared counter across processes at all — the correctness property this
feature is about (a separate process can always find *its own* proposal) doesn't need sequential,
human-countable ids, and no existing test or design document requires that format (`grep` across
the design docs and tests confirms every proposal id shown is illustrative, e.g. `p-8f2c`,
`p-3a91`, never asserted against a literal `p-1`/`p-2`).

**Alternatives considered**:
- *A counter persisted alongside the proposal files (e.g. a `log/proposals/.next-id` file).*
  Rejected: adds a second file with its own read-modify-write race for no benefit over a random id
  — nothing in the design ever reads a proposal id as an ordered sequence, so there is nothing a
  monotonic counter buys that a random id doesn't already give more simply.
- *Keep the counter, reset the risk by clearing `log/proposals/` at the start of every process.*
  Rejected: this would discard a still-legitimately-open proposal from an earlier session the
  moment any new CLI invocation runs, defeating the feature outright.

## Decision 3 — In-process behaviour, unchanged

**Decision**: `_open_proposals`, the in-process dict, is removed entirely rather than kept
alongside the new disk-backed store. Disk is the single source of truth for every open
proposal, in-process or not.

**Rationale**: Keeping both would mean every `commit`/`discard`/`reroll` has to decide which of
two sources to trust when they disagree (e.g. a test that pokes `_open_proposals` directly, or a
crash between writing the disk record and updating the dict) — a second state to keep consistent
is exactly the class of bug this issue exists to fix, one layer up. Reading from disk on every
call is cheap (one small JSON file) and is already the same cost `character.load`/`load_chronicle`
pay on every call for the same reason. FR-010 (no behavioural regression for same-process callers)
is satisfied because from a caller's point of view nothing observable changes — `propose` still
returns the same shape, `commit`/`discard` still raise the same error for the same inputs — only
*where* the interim state briefly lives changes.

**Alternatives considered**:
- *Keep `_open_proposals` as a fast path, fall back to disk on a miss.* Rejected: two sources of
  truth that can each be independently stale (a disk file deleted by an unrelated process, or an
  in-process dict from a long-lived embedding that never persisted) is worse than one slightly
  slower one, for a file small enough that the read cost is not a real concern (`propose`/`commit`
  already do at least one YAML entity load and one atomic write of their own per call).

## Decision 4 — Staleness/cleanup policy

**Decision**: Reuse `docs/design/22-state.md`'s already-specified policy unchanged — no new
staleness rule invented for this feature:
- A Rally already unconditionally calls `chronicle.discard_at_rally` then `resolution.discard`
  on whatever id it names (`engine/wyrd/rally.py`'s `apply_rally`, already implemented) — this
  will start working correctly the moment `discard` can actually find the file, with zero changes
  to `rally.py` itself.
- "One open proposal per actor" (FR-009) is enforced the same way partial reroll already treats
  independent branches: `propose_batch` continues to be the single call that creates a fresh
  proposal; nothing in scope changes when a second, unrelated `propose` call is made for an actor
  who already has one open — this is deliberately unenforced defensively in code today under
  #235/#328's own scoping (no call site currently exists that would trigger it, since
  `chronicle.record_rolled` is not yet wired into `propose` by anything — a pre-existing gap
  outside this issue's stated scope, not introduced by it). This feature does not add that
  wiring; FR-009 is satisfied vacuously today the same way it already was before this feature,
  and is called out in Assumptions rather than silently ignored.

**Rationale**: The issue's own scope list explicitly says to check docs/design/22-state.md rather
than invent a second policy, and that document already answers the question in full under
"Transaction lifecycle." Re-deciding it here would be exactly the kind of drift CLAUDE.md warns
against (two documents describing one thing differently).
