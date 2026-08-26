# Tasks: Oracle answer tables

**Input**: Design documents from `/specs/025-oracle-answer-tables/`
**Prerequisites**: plan.md, research.md, data-model.md, quickstart.md (all present)

Single-threaded, ordered — each task depends on the ones before it landing in the same document.

- [X] **T001** Write `tools/check_oracle_answers.py`: compute row widths/odds per likelihood band,
  assert contiguous 1–100 coverage and the claimed probabilities, matching
  `tools/check_affliction.py`'s style (module + `if __name__ == "__main__"`). *(Already written
  and passing during planning — this task confirms it stays where the plan places it.)*
- [X] **T002** Write `doc/design/12-oracle-answers.md`:
  - What an oracle is (ADR 0005 framing) and the obligation clause (which questions are
    oracle-bound vs. an ordinary GM decision).
  - The roll declaration block (`key`, `die`, `modifier`, `uniqueness`, `extra row fields`),
    matching the format used in `doc/design/10-transformations.md` / `03a-4-afflictions.md`.
  - The `oracle-answer` table: 5 bands × 4 rows, with the odds table from `research.md` embedded
    and attributed to `tools/check_oracle_answers.py`.
  - The Wyrd-die relationship statement (reused verbatim, no new mechanism).
  - The recording section (beat-log entry shape from `data-model.md`).
  - The "what a setting may replace" section, mirroring `03a-4-afflictions.md`'s closing section.
- [X] **T003** Amend `doc/design/01-principles.md` so the GM contract states the oracle obligation,
  agreeing with T002's wording rather than restating it differently.
- [X] **T004** Amend `doc/design/07-tables.md`'s index row for Oracles: link
  `03a-5-oracle-answers.md`, state the roll (`d100`), keep uniqueness `repeatable`.
- [X] **T005** Check `doc/design/02-architecture.md:91` and `doc/design/20-tooling.md:84` against the
  final filename and layout; amend only if either has gone stale.
- [X] **T006** Run verification: `python3 tools/check_oracle_answers.py`; grep `design/` for
  setting/system vocabulary; `python3 tools/check_docs.py` for reachability.
- [X] **T007** `ruff check . && ruff format --check .` and `python3 -m pytest -q` (repo-wide
  gate before PR).
