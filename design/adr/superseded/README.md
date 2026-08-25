# Superseded decision records

A record lands here when a later decision replaces it. **Nothing here is obsolete reading** — a
rejected or reversed decision explains why the current one looks obvious, and that explanation is
doing quiet work every time someone is tempted to propose the old answer again.

## The rule

- A record's **reasoning is never edited**, before or after it is superseded. Only its `Status:`
  line changes, to name the record that replaced it.
- The replacing record carries `**Supersedes:** ADR NNNN`, so the link runs both ways.
- **A record here keeps the number it was written under, permanently.** The live set in
  [`../`](../) is renumbered into a clean sequence; this archive never is. That is what lets a
  reference written years ago still resolve to the decision it meant, rather than to whatever
  record later inherited its number.
- **Nothing is ever deleted from here.**

The full rule, and the design reset that made it necessary, are in
[ADR 0012](../0012-the-design-reset-and-how-records-are-consolidated.md).

## Index

Every record in this directory must be listed below — `python3 tools/check_docs.py` fails
otherwise, the same way it checks the live index in [`../../README.md`](../../README.md).

| | | |
|---|---|---|
| — | *(none yet)* | No decision has been superseded. |
