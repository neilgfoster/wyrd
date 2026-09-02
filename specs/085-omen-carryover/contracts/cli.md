# Contract: no signature changes

`propose`, `propose_batch`, `reroll`, `commit`, `discard` all keep their exact existing
signatures (#235/#236/#237). This feature changes *behavior* only: a request now reads and
applies its actor's pending Omen automatically, and the proposal's `mutations`/`steps` may
include a `pending_omen` `set` mutation and Omen-consumption `depends_on` edges that weren't
possible before. No new CLI subcommand, verb, or catalog entry — this is not a capability a
caller invokes directly, it's a rule `propose`/`propose_batch`/`reroll` now apply on their own,
per `docs/design/31-action-resolution.md`.
