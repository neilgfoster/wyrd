# Implementation Plan: Obsidian vault and the README as hub

**Branch**: `004-obsidian-vault` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Commit a minimal `.obsidian/` configuration, record the link policy as an ADR, repair the four stale
claims in the README pair, and add `tools/check_docs.py` so the staleness cannot return silently.

The load-bearing choice: **markdown links in prose, `[[wikilinks]]` in entity data.** Obsidian reads
markdown links natively; GitHub does not read wikilinks at all, and this repo is intended public. The
vault config is set so Obsidian *creates* markdown links, which makes the policy the default rather
than something to remember.

## Technical Context

**Language**: Python 3.11+, stdlib only. `unittest` (`design/07-tooling.md` §6).

**Placement**: `tools/check_docs.py`, beside `tools/backlog.py`. Same shape: a `check` that prints
what is wrong and exits non-zero.

**No network.** Unlike `backlog.py` this reads only the filesystem, so its tests need no fixtures.

## Constitution check

| Gate | How this satisfies it |
|---|---|
| Deterministic over inference (§1) | Reachability and link resolution have correct answers → script. |
| Stdlib only (§2) | `pathlib`, `re`, `argparse`. |
| Nothing unpublishable | Vault config carries no paths or library references. |
| Substrates untouched | Nothing under `.kord/`, `.specify/`, `.github/ISSUE_TEMPLATE/`. |
| Documents describe the present | The README's false status claim is corrected, not annotated. |

## Design

### The reachability model

```
README.md  ──links──►  design/01..16, design/README.md, settings.yaml, specs/
                            │
              design/README.md ──links──► every design/adr/NNNN-*.md
```

Reachability is transitive from `README.md`. A document is reachable if some chain of relative
markdown links leads to it. This is why the ADR index matters mechanically and not only as
courtesy: it is the only edge from the hub to the individual records.

**Scope of the requirement.** Every `design/**.md` must be reachable. `specs/**` is exempt at file
level — a spec is the record of one past change, not current design, and requiring an index entry per
spec file would be noise that rots. `specs/` is linked as a directory so the tree stays discoverable.
Dead-link checking, by contrast, applies everywhere including `specs/`.

### The four checks

1. **Unreachable** — a `design/**.md` no chain from `README.md` reaches.
2. **Dead link** — a relative target that does not exist on disk. Anchors are stripped before
   resolving; external schemes are skipped.
3. **Unindexed ADR** — a file in `design/adr/` absent from `design/README.md`.
4. **Wikilink in prose** — `[[...]]` in a document that is not illustrating entity data.

Check 4 needs care: `design/14-entities.md`, `06-state.md`, `07-tooling.md` and `08-maintenance.md`
legitimately contain wikilinks, either inside fenced YAML examples or as inline code describing the
convention. So the rule is **wikilinks are allowed inside fenced code blocks and inline code spans,
and nowhere else** — which is exactly where they appear today, and is checkable without an allowlist
of files that would itself go stale.

### Vault configuration

Three small files, all machine-independent:

- `app.json` — `useMarkdownLinks: true`, `newLinkFormat: "relative"`. This is the policy, enforced by
  the tool rather than by memory.
- `appearance.json` — theme left to the reader's own setting.
- `core-plugins.json` — a minimal set; no community plugins, which would not be installed anyway.

`.gitignore` already excludes `.obsidian/workspace*`. It gains the other per-machine artefacts.

## Steps

1. `.obsidian/` config; extend `.gitignore`.
2. ADR 0011 — the link policy.
3. Repair `README.md` (four faults) and `design/README.md` (ADR index).
4. `tools/check_docs.py`.
5. `tools/test_check_docs.py` — `unittest`, against a temporary tree so each failure class is
   constructed rather than restated.
6. Run against the repo; confirm green.

## Risks

**Check 4 could misfire** on a future document that discusses wikilinks in prose rather than in code.
The fenced/inline-code rule is the mitigation, and the failure mode is a loud false positive rather
than a silent miss — the right direction for a guard.

**The README becomes the bottleneck for adding a document.** That is the intent: a document nothing
links to is a document nobody reads.
