<!--
Title: say what changed, not where it lives. "Move the design documents under docs/ and settle
numbering (closes #38)" -- not the branch name, not a ticket ID with nothing else. If the title
would read the same with every word after the issue number deleted, it isn't a title yet.
-->

## Summary

<!-- What changed, why, and what you actually verified -- the diff already says what changed in
     detail; this says what problem it solves, the reasoning behind the approach (the same
     "why, not what" rule commit messages follow), and what you ran to confirm it works
     ("ran python3 tools/check_docs.py, 236 documents all reachable" -- not "should pass").
     Reference the issue this closes. A reviewer should be able to decide whether to look
     closely from this section alone, before opening the diff.

     kord-pr-raise fills only this first placeholder from --summary; every later one gets
     stamped "N/A" if left as a bare comment, so put everything load-bearing here rather than
     splitting it across sections a generated PR would leave unfilled. -->

## Decisions this PR makes

<!-- Only if a real judgment call was made along the way that a future reader would want the
     reasoning for -- a genuine alternative rejected, or a design/09-evolution.md-style
     forward-only choice. Link the ADR if one was recorded. Delete this section if nothing here
     rises to that bar; most PRs won't -- an empty/deleted section is fine, a stamped "N/A" one
     reads as "I checked and there's genuinely none," so only leave it in if that's true. -->

## Checklist

- [ ] `python3 tools/check_docs.py` passes (if this PR touches `docs/`, `README.md`, or a link)
- [ ] `python3 -m pytest -q` passes
- [ ] No bulk find-and-replace without a verification grep afterward (`CLAUDE.md`)
- [ ] Referenced the issue(s) this closes/advances
