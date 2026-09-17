# Phase 0 Research: Session friction capture

No unresolved `NEEDS CLARIFICATION` markers remain in plan.md's Technical Context — this is a
documentation-only feature with no technology stack to select. The one substantive open question
(file location) was already resolved during `/speckit-clarify` and is recorded in spec.md's
Clarifications section. This file records that decision's rationale for traceability, plus the
two format/triage choices the spec itself settles.

## Decision: friction log location

- **Decision**: `log/friction.md`, inside each chronicle repo's existing `log/` directory.
- **Rationale**: `docs/design/23-chronicle-bootstrap.md`'s post-bootstrap layout already puts
  session logs under `log/`. Placing the friction log alongside them keeps all per-session
  written artifacts in one directory rather than splitting root-level files (`chronicle.yaml`,
  `recap.md`) further, and reads naturally as "another kind of log," not a new top-level concern.
- **Alternatives considered**:
  - Root-level `friction.md` (rejected by clarification answer — would sit apart from the other
    per-session logs `log/` already holds).
  - A frontmatter field inside each session's own log file (rejected in the same clarification
    question — would force the harvest step, #95, to scan every session file rather than read one
    fixed path per chronicle).

## Decision: entry format

- **Decision**: A short, human-authored Markdown entry per friction moment — not YAML/JSON —
  appended to `log/friction.md`, containing the three fields spec.md's FR-003 requires (mechanic
  implicated, what happened, what the GM did).
- **Rationale**: The GM authors this mid-beat; requiring a schema to be satisfied in the moment
  would violate FR-002's "no more GM attention than reading a Wyrd die" bar. Markdown is already
  this repo's format for every other authored artifact (`CLAUDE.md`, `docs/design/*`, chronicle
  logs and recap). The harvest step (#95) is responsible for whatever parsing its own
  implementation needs; this spec commits only to a stable minimum shape, not a machine schema.
- **Alternatives considered**: A structured YAML/JSON log entry per occurrence — rejected as
  disproportionate ceremony for a note that must cost seconds, and inconsistent with every other
  chronicle-authored file being prose-first Markdown.

## Decision: triage line

- **Decision**: The three-condition test in spec.md's FR-004 (unpredicted reading of a documented
  mechanic; a correctly-applied mechanic producing a result that felt wrong; an undocumented case
  forcing improvisation).
- **Rationale**: Directly reuses issue #94's own three named categories ("a mechanic that read one
  way... a table producing an outcome that felt wrong... a GM having to improvise") rather than
  inventing a new taxonomy, and each condition is checkable at the moment of play without
  requiring the GM to weigh anything beyond what already happened.
- **Alternatives considered**: A severity/impact score per moment — rejected as more ceremony than
  a binary "does this qualify" check, and epic #93's own scope note warns against a harvest that
  "files everything," which a low bar for what counts as an entry would only push further downstream.

**Output**: All Technical Context unknowns resolved; no outstanding `NEEDS CLARIFICATION` markers.
