# Phase 0 Research

## Decision: a one-off migration script, not a new permanent tool

**Decision**: Write a script under a scratch location (not committed to `tools/`) that performs
every `git mv` from `data-model.md`'s mapping and rewrites every relative link it finds inside
the moved files, using the mapping as its only source of truth. Run once, then discarded.

**Rationale**: This move happens exactly once — the whole point of settling the numbering
convention is that it does not need doing again. A permanent script for a one-time migration
would be dead code the moment it finishes, and `docs/design/27-tooling.md`'s "stdlib only" principle
governs *engine* tooling, not a throwaway repo-surgery script. `tools/check_docs.py`, which does
need to keep running, is retargeted rather than replaced.

**Alternatives considered**: a committed `tools/migrate_doc_layout.py` (rejected — nothing calls
it a second time; it would be the same kind of dead tooling the repo has otherwise avoided).

## Decision: rewrite links by matching whole path tokens, not substring find-replace

**Decision**: For every markdown link (display text plus target path) or bare `design/....md`
reference, resolve
`path` relative to the file it's found in, look it up in the old→new mapping, and substitute the
new path re-relativized to the (possibly also moved) containing file's new location. A path that
doesn't appear in the mapping is left untouched and flagged for manual review.

**Rationale**: `CLAUDE.md` records three word-corruptions from blind substitution
(`diffisecty`, `secture`, "daemon" → "otherworldly power, no database"). Token-level matching
against a closed, known mapping cannot produce a partial-word match the way a regex substitution
over raw text can.

**Alternatives considered**: `sed -i 's#design/#docs/design/#g'` (rejected outright — this is
exactly the operation CLAUDE.md's incident log warns against, and it can't handle the ADR
renumbering-free-but-directory-change or the design-doc renumbering at all).

## Decision: open-issue line-number citations are flagged, not silently rewritten

**Decision**: An open issue citing `docs/design/24-authoring-a-setting.md:157` gets its path rewritten
to `docs/design/24-authoring-a-setting.md` but the update explicitly notes the line number may no
longer point at the same content, rather than either stripping it or assuming it still holds.

**Rationale**: This move renumbers files but does not touch their content, so most line numbers
probably still hold -- but "probably" is not "computed," and docs/design/27-tooling.md's own
deterministic-over-inference principle says not to assert what wasn't checked. Flagging costs one
sentence per issue; asserting a wrong line number costs someone's trust in the citation.

**Alternatives considered**: silently keeping the line number (rejected -- asserts something
unverified); silently stripping it (rejected -- discards real information for issues where the
content genuinely didn't move).

## Decision: specs/ gets a path-only repair, not a blanket exemption

**Decision**: Every `design/...` path token inside `specs/*/*.{md,py}` is rewritten to its new
location via the same closed old→new mapping used everywhere else; nothing else in any `specs/`
file is touched.

**Rationale**: The initial Clarifications answer ("leave `specs/` alone entirely") conflicted
with a pre-existing, deliberate rule already encoded in `tools/test_check_docs.py`
(`test_dead_link_inside_specs_is_still_caught`): `specs/` is exempt from the *reachability*
check, but never from the *dead-link* check. A `specs/*/*.md` reference to a since-renamed
`design/` path is real link rot by that check's own definition, and there is no way to leave it
unrepaired without either permanently failing `check_docs.py` or weakening a check that predates
this feature and exists to catch a real class of fault (a typo'd or genuinely broken link inside
a spec). A pure path-token substitution — the same posture as the ADR-link decision — resolves
this without touching a spec's prose or reasoning, which is what "historical record" actually
protects.

**Alternatives considered**: leaving `specs/` fully untouched and accepting ~127 permanent dead-
link reports (rejected — makes `tools/check_docs.py` no longer a trustworthy "all checks passed"
signal, exactly the erosion CLAUDE.md's own tooling principles exist to prevent); narrowing the
existing dead-link check to exempt only `design/`-shaped links inside `specs/` (rejected — a
special case future readers would have to learn, for no benefit over just repairing the 1,148
tokens directly).

## Decision: the ADR-link-repair policy becomes its own ADR, not a footnote

**Decision**: FR-012 -- a new `docs/adr/0038-....md` records "an ADR's reasoning is immutable; a
relative path inside it is repaired like any other link" as a permanent, citable policy.

**Rationale**: The issue itself calls this "the load-bearing decision in this issue" and notes it
"has not been asked before." `docs/README.md`'s own rule (an ADR earns its record when a real
alternative was rejected and someone would plausibly propose it again) applies exactly here --
CLAUDE.md's own "never edited" rule is the rejected-alternative-if-taken-literally case, and
future path repairs (the next time something moves) would otherwise re-ask this exact question.

**Alternatives considered**: a note in `CLAUDE.md` instead (rejected -- `CLAUDE.md` governs how
Wyrd is built, not why a specific tension in its own rules resolved one way; this is precisely
what `docs/README.md`'s ADR criteria describes).
