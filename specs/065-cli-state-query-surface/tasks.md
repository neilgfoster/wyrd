# Tasks: Design the CLI's state-loading and querying surface, and the three memory tiers

- [X] **T001** Read `02-architecture.md`'s current Memory tiers/Code-versus-prose sections and
      `22-state.md`'s entity model (companions, threads, threats already described as queries)
      to ground the design in existing precedent (FR-001–FR-004).
- [X] **T002** Specify `wyrd session-context`: the Always-loaded tier's query, its filters
      (player character, `with-party` companions, `open` threads by heat, recap, contract), and
      its output shape (FR-001).
- [X] **T003** Specify `wyrd get <id>` (effective-entity fetch) and `wyrd find` (generic
      type/status/tag query) for the On-demand tier (FR-002, FR-003).
- [X] **T004** Specify named convenience commands (`wyrd party`, `wyrd threads`, `wyrd threats`)
      as thin wrappers over `wyrd find`, matching `22-state.md`'s already-named query patterns
      (FR-004).
- [X] **T005** Specify `wyrd log --last N | --since <beat>` for the Archival tier (FR-005).
- [X] **T006** State the nonexistent-id-vs-zero-matches distinction explicitly (FR-006) and the
      structured-output-by-default rule (FR-007).
- [X] **T007** State the deferred Archival full-text search capability and its reason (FR-008).
- [X] **T008** Correct `22-state.md`'s player-character frontmatter example (drop `luck`, drop
      Resolve's stored `max`) since session-context returns exactly this frontmatter.
- [X] **T009** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
