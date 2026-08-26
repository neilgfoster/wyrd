# Quickstart: The dangling-mechanic check

## Prerequisites

- Python 3.11+ (stdlib only, no install step — `docs/design/20-tooling.md` section 2)
- A checkout of this repo with `design/` present

## Run the check

```bash
python3 tools/check_dangling_mechanics.py
```

Expected on a clean tree (end of the design programme, spec SC-002):

```text
tools/check_dangling_mechanics.py: N mechanic definitions, M references, 0 dangling
```

Exit code `0`.

## Run the check's own tests

```bash
python3 -m unittest discover -s tools -p 'test_*.py'
```

This runs `tools/test_check_dangling_mechanics.py` alongside every other `tools/test_*.py`
module already in the repo. Confirms:

- Each of the six historical dangling-mechanic instances (spec FR-005/User Story 2) fails
  independently when reconstructed as a fixture.
- A planted dangling reference in a fresh two-document fixture is caught (spec acceptance
  scenario, User Story 1).
- A clean tree with a heading-only, table-row-only, and glossary-entry-only definition each
  passes (proves FR-001 covers all three definition shapes, not headings alone).
- A reference inside a fenced code block or inline code span is not flagged (FR-010).

## Validate against a planted failure by hand

```bash
mkdir -p /tmp/dangling-demo/design
cat > /tmp/dangling-demo/design/01-example.md <<'EOF'
# Example

This document uses the Fictional Widget mechanic without ever defining it.
EOF
# Point the check at a scratch tree instead of the repo's own design/ for this manual demo —
# adjust the script's root resolution or copy it alongside the scratch tree as needed.
```

(The scripted equivalent of this manual walkthrough is exactly what
`tools/test_check_dangling_mechanics.py`'s planted-reference test automates — this section is
for a contributor who wants to see the failure shape without reading the test module.)

## Machine-readable mode

```bash
python3 tools/check_dangling_mechanics.py --format json | python3 -m json.tool
```

See [`contracts/cli.md`](contracts/cli.md) for the full output shape and exit-code contract.
