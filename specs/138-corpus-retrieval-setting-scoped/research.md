# Research: Corpus retrieval is scoped to a setting, never unfiltered

No `[NEEDS CLARIFICATION]` markers remain in spec.md. One decision worth recording:

- **Decision**: `setting` is added as the **second positional parameter** on all five functions
  (after the index, before any existing optional filter), required, no default.
  **Rationale**: a required, positional-by-default parameter makes an unscoped call a `TypeError`
  at the call site, not a silently-accepted omission — the strongest structural enforcement
  Python offers for "this is never optional" (docs/design/21-parallel-chronicles.md's own MUST).
  Placing it second (right after the index) keeps every function's shape consistent and
  discoverable, rather than burying the mandatory filter after a run of optional keyword
  arguments.
  **Alternatives considered**: a keyword-only `setting` with no default (`*, setting: str`) —
  considered equivalent in strictness (still a required argument, still raises `TypeError` if
  omitted) but rejected in favour of positional placement for readability at call sites
  (`find_noun(index, "my-setting", "Osric")` reads naturally as "in this index, for this
  setting, find this name").
