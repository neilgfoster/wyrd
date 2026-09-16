# Implementation Plan: Adventure and campaign generation

**Branch**: `161-adventure-and-campaign-generation` | **Date**: 2026-09-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/161-adventure-and-campaign-generation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

This is a **specification-only** feature (see spec.md's Assumptions, and issue #99's own
Definition of Done: "Capability change: Spec Kit cycle, `specs/` committed"). The deliverable is
the design artefacts under `specs/161-adventure-and-campaign-generation/` — no CLI verb, no
`engine/wyrd/*.py` module, no data files. A later feature implements what this one specifies,
the same separation `24-authoring-a-setting.md` already draws between a spec and the code that
satisfies it.

The primary decision recorded here: generation is not a new mechanism but an **assembly step**
in front of mechanisms the engine already has — thread/threat matching
([`18-arcs-and-beats.md`](../../docs/design/18-arcs-and-beats.md),
[`19-campaign.md`](../../docs/design/19-campaign.md)), danger scaling
([ADR 0024](../../docs/adr/0024-a-party-is-worth-less-than-its-head-count.md)), and the entity
schema itself ([`25-entities.md`](../../docs/design/25-entities.md)). The two invocation modes
(`live-play`, `setting-authoring`) are one request shape with different available state, per
spec.md FR-006, not two designs.

## Technical Context

**Language/Version**: N/A for this feature — no code is written. A future implementing feature
would follow the engine's existing constraint: Python 3.11+, stdlib only
([`27-tooling.md`](../../docs/design/27-tooling.md) §2).

**Primary Dependencies**: N/A — no application code in this feature. The *design* depends on
existing engine modules by reference only: `campaign.py` (threads/threats), `rules.py`/`tables.py`
(danger scaling), `state.py` (entity read/write) — per `27-tooling.md` §3's module map. This
feature specifies which of those an implementation must call, not new dependencies.

**Storage**: N/A for this feature. The commit-back path (FR-012–FR-015) specifies writing through
the existing YAML entity store ([`22-state.md`](../../docs/design/22-state.md)) — no new storage
mechanism.

**Testing**: N/A for this feature — there is no code to test yet. `data-model.md` and
`contracts/` are written so a future implementing feature's tests (stdlib `unittest`, per
`27-tooling.md` §6) can be derived directly from them without re-deriving the contract.

**Target Platform**: N/A — unchanged from the engine's existing target (stdlib-only, any Python
3.11+ runtime).

**Project Type**: Design specification (Spec Kit artefacts only) — no source tree changes.

**Performance Goals**: N/A for this feature. A future implementation inherits the engine's
existing performance posture (deterministic steps run inline; the one capable-model step per
FR-019 is the same latency class the GM session's own narration already is).

**Constraints**: The two hard constraints this plan must satisfy, both non-negotiable per the
issue and `CLAUDE.md`: (1) setting-agnostic — no setting vocabulary anywhere in the generation
contract; (2) no fork of the threat/thread machinery — the commit-back path must be additive to
`campaign.py`'s existing state, never a parallel structure (spec.md FR-013, SC-003).

**Scale/Scope**: One generation request at a time, at one of three named scales (beat, arc,
campaign spine — the last a request-shape alias per FR-002/FR-003). No batch generation, no
multi-request planning, is in scope (see spec.md's "Out of scope: the GM's moment-to-moment
narration during play" and the issue's own scope line).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are evaluated against `CLAUDE.md` and the accepted
ADRs, not a separate constitution document:

- **Nothing unpublishable enters this repository.** PASS — this feature specifies a contract in
  the abstract; it names no source, no extracted text, no personal-library catalogue anywhere in
  `spec.md`, `plan.md`, `data-model.md`, or `contracts/`.
- **No setting or system names in `docs/design/`/`README.md`; engine labels are descriptive
  English.** PASS — checked directly: the spec and this plan use only generic labels (`beat`,
  `arc`, `campaign`, `threat`, `thread`, `live-play`, `setting-authoring`) already established by
  existing design documents, none borrowed from a source system. This feature's own artefacts
  live under `specs/`, not `docs/design/`, so the gate does not literally apply to them, but the
  contract they specify is written to hold when it eventually *is* reflected in `docs/design/` by
  an implementing feature.
- **Tone is a setting property, never baked into a mechanic** ([ADR 0004]). PASS — the generation
  contract reads `tone_contract` from the request (spec.md FR-003) and enforces whatever it
  declares (FR-008, FR-010); it hard-codes no register or tone of its own.
- **Anything with a correct answer is computed, not inferred** ([ADR 0005]). PASS — this is the
  organizing principle behind FR-016/FR-017 (no-model steps) and the whole anti-inflation
  section (FR-007–FR-011), each stated as a closed-vocabulary or arithmetic check rather than a
  narrative judgment call.
- **Rule changes apply forward only; history is never recomputed.** PASS — FR-014 states this
  explicitly for generated content once played: never regenerated or retconned.
- **Design documents are rewritten in place; ADRs are never edited.** N/A to this plan directly
  (this feature produces `specs/` artefacts, not a `docs/design/` rewrite) — noted for the
  implementing feature that will eventually update `18-arcs-and-beats.md`/`19-campaign.md` to
  describe generation as a present capability rather than leaving this spec as the only record
  (per `CLAUDE.md`'s "Where a spec and a design document disagree" rule).
- **Capability changes go through the Spec Kit cycle, with `specs/<feature>/` committed.** PASS —
  this is exactly that cycle, and this directory is what gets committed.

No violations. Complexity Tracking is not filled in below.

## Project Structure

### Documentation (this feature)

```text
specs/161-adventure-and-campaign-generation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── generation-request.md   # Phase 1 output — the request/result contract
└── checklists/
    └── requirements.md  # Spec Quality Checklist (from /speckit-specify)

(tasks.md is Phase 2 output — /speckit-tasks — not created by this command)
```

### Source Code (repository root)

No source code changes in this feature. Nothing under `engine/`, `tools/`, or `docs/design/` is
modified by this plan — this is deliberate (see Summary): the deliverable is the specification
itself, per the issue's own Definition of Done.

**Structure Decision**: Design-artefact-only structure — the standard `specs/<feature>/` layout
Spec Kit already provides, with `contracts/` holding one document (the generation request/result
contract) rather than per-endpoint files, matching this feature's own project type (a
specification for an internal engine mechanism, not a library/CLI/service with multiple external
interfaces).

## Complexity Tracking

*No Constitution Check violations — this section is not filled in.*
