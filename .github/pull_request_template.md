<!--
Title: say what changed, not where it lives. "Move the design documents under docs/ and settle
numbering (closes #38)" -- not the branch name, not a ticket ID with nothing else. If the title
would read the same with every word after the issue number deleted, it isn't a title yet.
-->

## What and why

<!-- What changed, and why -- the diff already says what changed in detail; this says what
     problem it solves and the reasoning behind the approach, the same "why, not what" rule
     commit messages follow. Reference the issue this closes. A reviewer should be able to
     decide whether to look closely from this section alone, before opening the diff. -->

## Verification

<!-- What you actually ran to confirm this works: `python3 tools/check_docs.py`, the relevant
     `check_*.py` script, `python3 -m pytest -q`, a manual walkthrough. State the result, not
     just the command -- "ran X, got Y" rather than "should pass X". -->

## Decisions this PR makes

<!-- Only if a real judgment call was made along the way that a future reader would want the
     reasoning for -- a genuine alternative rejected, or a design/09-evolution.md-style
     forward-only choice. Link the ADR if one was recorded. Delete this section if nothing here
     rises to that bar; most PRs won't. -->

## Checklist

- [ ] `python3 tools/check_docs.py` passes (if this PR touches `docs/`, `README.md`, or a link)
- [ ] `python3 -m pytest -q` passes
- [ ] No bulk find-and-replace without a verification grep afterward (`CLAUDE.md`)
- [ ] Referenced the issue(s) this closes/advances
