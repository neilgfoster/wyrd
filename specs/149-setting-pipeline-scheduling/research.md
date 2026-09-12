# Phase 0 Research: Setting build pipeline — scheduled execution and web augmentation policy

## Decision 1: Scheduling mechanism

**Decision**: Recommend GitHub Actions' `schedule` (cron) trigger, defined inside the setting
repository itself, running against that repository's own `library/` and writing to that
repository's own `index/`.

**Rationale**: Issue #102 itself names "running pipeline passes as a GitHub Action in the setting
repo" as the option to evaluate. Every `wyrd-setting-<name>` repo is already a private GitHub
repository (CLAUDE.md's repository table); GitHub Actions' `schedule` trigger runs entirely
inside that repository's own runner and permission boundary, so no source material or derived
index ever crosses a repository boundary — the constraint issue #102's own Definition of Done
states explicitly ("copyrighted source material never leaves the private setting repo it lives
in"). No new infrastructure (a shared runner, an external cron service) is needed.

**Alternatives considered**:
- *A shared/central runner in this repo (`wyrd`) that pulls from setting repos*: rejected outright
  — this repo is intended public (CLAUDE.md), and any mechanism that reads a private setting
  repo's `library/` from here would move copyrighted material across the repository boundary the
  moment it ran, which is exactly what CLAUDE.md forbids.
- *A long-running external service/daemon*: rejected — the engine has no server component
  anywhere else in its design (`02-architecture.md`), and introducing one only for scheduling
  would be new infrastructure for a problem GitHub Actions' own built-in cron already solves.
- *No scheduling at all — every run stays attended*: considered seriously, since issue #102
  explicitly allows "an explicit decision against one, with the reason recorded" as a valid
  outcome. Rejected in favour of a scoped recommendation, because unlike scheduling itself, the
  *reason* to stay attended (the scenario index's model call) applies only to one of five index
  builders, not the whole pipeline — so a blanket "never schedule" verdict would block automation
  three of five of the deterministic steps do not need to wait on. The design instead partitions
  the pipeline rather than making a single yes/no call across all of it (see Decision 2).

## Decision 2: Which pipeline steps run unattended

**Decision**: Pass 0's catalogue, gap-survey and idempotence pass (#100), plus the four
deterministic corpus indexes (`documents`, `nouns`, `terms`, `tables` — `26-corpus-index.md`'s own
"Build and maintenance" table already marks these "trivial" or "one pass, deterministic") are safe
to run unattended on a schedule. The fifth index, `scenarios.json`, keeps its existing **lazy,
on-first-need** build (`26-corpus-index.md`: "The expensive one is lazy — an adventure gets its
thematic record the first time anything asks for it, not up front") and is explicitly excluded
from the scheduled run.

**Rationale**: `26-corpus-index.md` already documents the scenario index as the one index needing
a model call (Haiku-tier, per `27-tooling.md`), everything else being deterministic and cheap.
Deterministic-over-inference (`27-tooling.md`) argues for keeping the model call attended (or at
minimum outside blind scheduled automation) since its output is cached forever and regenerated
only on schema change — a bad or drifted generation from an unattended run would be expensive to
notice and to unwind, whereas the four deterministic indexes are cheap to regenerate and easy to
diff against a prior run.

**Alternatives considered**:
- *Schedule the scenario index too, behind a budget/rate cap*: rejected for this feature — adds a
  new operational knob (a per-run budget) issue #102 never asked for, and the risk/benefit is
  asymmetric: the index is explicitly lazy and cached forever already, so there is no backlog
  pressure forcing it onto a schedule.
- *Exclude Pass 0 from the scheduled run too, treating it as always-attended*: rejected — Pass 0's
  own design (#100/specs/147) is explicitly deterministic, signal-based classification with no
  model call anywhere in it, and its own Definition of Done calls for it to be "cheap enough to
  re-run whenever material is added" — which is exactly the property that makes it schedule-safe.

## Decision 3: What "public source" means, and when it may supplement the library

**Decision**: A public source is in-bounds for supplementing a Pass 0 gap only when it carries a
clear, checkable provenance of its own that does not depend on anyone's private library already
existing — a public-domain text, an author's or publisher's own freely and openly published
material (errata, an SRD, a glossary released under an open licence), or broadly attested common
knowledge (folklore, real-world reference facts with an independently checkable source). "Found on
the open internet" alone is explicitly **not** sufficient — a source must be traceable to a
specific, cite-able origin, the same bar `nouns.json`/`terms.json` already hold internal corpus
references to.

**Rationale**: Issue #102 asks for "an explicit, provenance-tracked rule," not a blanket
allow/deny. The dividing line above is the one CLAUDE.md's own repository-boundary logic already
implies: the constraint that exists is about *copyrighted, privately-sourced* material never
leaving its repo, not about the setting being permitted no other input at all. A source whose own
licence or origin is independently public and checkable introduces no risk to that boundary,
while an arbitrary web page (unknown licence, unknown authority) both risks a copyright problem
of its own and cannot be checked later, which the provenance schema below exists specifically to
avoid.

**Alternatives considered**:
- *Forbid public augmentation entirely*: rejected — issue #102's own Goal states the pipeline
  "has an explicit, provenance-tracked rule for when public sources may supplement," which
  presumes the answer is not a flat no; a flat no also fails to use the Pass 0 gap report
  (#100) for anything once a gap is found.
- *Allow any web source, tracked only by URL*: rejected — a URL alone is not a checkable
  provenance record once the page changes or disappears (an edge case this spec names
  explicitly), and does not establish that the source was actually licensed to be used this way.

## Decision 4: Provenance record shape

**Decision**: A minimal record — `{"origin": "library" | "public", "reference": str | None}` —
where `reference` is required (non-empty) when `origin == "public"` and must be `None` when
`origin == "library"` (a library-sourced fact's provenance is the setting's own `documents.json`
entry it was already extracted from — no second reference needed). Modeled as a pure builder
function, `build_provenance_record(*, origin, reference=None) -> dict`, raising `ValueError` on
either half of that constraint being violated — the same "pure, no-I/O, raises on bad input"
shape every sibling `corpus_*` builder already uses.

**Rationale**: FR-007 requires this repo to define a *shape*, not an end-to-end implementation
against a live source — matching `corpus_document.py`/`corpus_terms.py`'s own precedent of a pure
record builder a setting repo's own tooling calls with data it already has. A closed two-value
`origin` vocabulary (mirroring `AUTHORITY_TIERS`' closed vocabulary in `setting_pass0.py` and
`WORLD_BUILDING_CATEGORIES` in `corpus_pipeline.py`) keeps the field checkable by a validator
rather than free text.

**Alternatives considered**:
- *A richer schema (source type, licence, retrieval date, confidence)*: rejected for this pass —
  nothing in issue #102's acceptance criteria asks for more than "which source it came from,
  public or library," and a setting repo's own tooling remains free to extend the record with
  additional fields beyond this minimal, required pair; over-specifying now risks the same
  "reads as authoritative and isn't" staleness CLAUDE.md warns against for specifications that
  outrun what was actually decided.
- *A single free-text `source` string instead of a closed `origin` + `reference` pair*: rejected —
  a free-text field cannot be validated deterministically for "names a specific reference," which
  is exactly the SC-003 requirement ("zero derived facts carry an unattributed 'public' tag").
