# Research: Corpus index retrieval queries (wyrd find)

No `[NEEDS CLARIFICATION]` markers remain in spec.md. One decision worth recording:

- **Decision**: `find_doc`'s `work`/`issue` filters match against a document record's `system`/
  `edition` fields respectively, with no import of `corpus_document.py` needed — this module
  reads the shape, not the producing function.
  **Rationale**: the design document's own worked retrieval example (`wyrd find doc --work
  "<periodical>" --issue 98`) uses field names (`work`, `issue`) that don't literally appear on
  #354's `build_document_record` output (`system`, `edition`) — but its own worked scenario
  record example (`system: "a periodical"`, `edition: "98"`) is the same document the retrieval
  example describes, confirming `work` means `system` and `issue` means `edition` in this
  codebase's actual schema.
  **Alternatives considered**: adding `work`/`issue` as new fields alongside `system`/`edition`
  on the document record itself — rejected as scope creep into #354's already-merged schema for
  a naming-only concern this query layer can resolve on its own side.
