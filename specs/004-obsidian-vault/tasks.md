# Tasks: Obsidian vault and the README as hub

**Feature**: 004-obsidian-vault | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 1 — The vault

- [x] T001 `.obsidian/app.json` with `useMarkdownLinks: true`, `newLinkFormat: "relative"`.
- [x] T002 `.obsidian/appearance.json` and `.obsidian/core-plugins.json`, machine-independent.
- [x] T003 Extend `.gitignore` for the remaining per-machine vault artefacts.

## Phase 2 — Record the decision

- [x] T004 ADR 0011 — markdown in prose, wikilinks in data, and why the obvious answer is wrong.

## Phase 3 — Repair the four stale claims

- [x] T005 `README.md` design index gains `03a-2-aftermath`.
- [x] T006 `README.md` repositories table uses `wyrd-setting-<name>`.
- [x] T007 `README.md` Status: remove the dead `playtest/` link and the false "Design complete".
- [x] T008 `design/README.md` ADR index gains 0009 and 0010.
- [x] T009 `README.md` links `specs/` and `tools/` so the tree is discoverable.

## Phase 4 — The guard

- [x] T010 `tools/check_docs.py`: reachability, dead links, ADR index, wikilink-in-prose.
- [x] T011 `tools/test_check_docs.py` — construct each failure class in a temp tree; call the real
      functions, never a restatement of them.
- [x] T012 Run against the repo; confirm zero exit and that each check fails when planted.

## Phase 5 — Ship

- [x] T013 Commit referencing #39, open the PR.
