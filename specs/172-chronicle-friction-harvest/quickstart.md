# Quickstart: Chronicle friction harvest

## Prerequisites

- `python3` on PATH.
- `gh` on PATH and authenticated, if harvesting a chronicle repo you have not checked out locally.
- kord's `client.py` reachable (for `github-issue-dedup-check`) — already true in this repo, the
  same access `kord-template-harvest` itself relies on.

## 1. Run the tests

```bash
python3 -m unittest discover -s tools -p 'test_harvest_friction.py'
```

Expected: all pass, including the three fixture cases under `tools/fixtures/friction/`
(qualifying, color-only, malformed).

## 2. Harvest a local chronicle checkout

```bash
python3 tools/harvest_friction.py --chronicle /path/to/wyrd-chronicle-<name>
```

Expected output: a report listing, per chronicle:
- New proposals (mechanic + finding, source-attributed) ready for operator review.
- Likely duplicates (proposal + the existing issue it matches).
- Skipped malformed entries (which fields were missing).
- Entries that did not qualify (ordinary color) and, separately, entries flagged `needs_review`.

Nothing is filed. Confirm no proposal's `title`/`body` contains any text outside what the source
`log/friction.md` entry's `mechanic`/`what happened`/`what the GM did` fields already state
(SC-004) — a manual read-through is sufficient for this check.

## 3. Harvest across multiple chronicles in one pass

```bash
python3 tools/harvest_friction.py --chronicle /path/to/chronicle-a --chronicle /path/to/chronicle-b
```

Expected: each proposal names its source chronicle; a repo with no `log/friction.md` reports
"nothing to harvest" for that repo rather than erroring (FR-006).

## 4. Confirm dedup on a second run

1. Run the harvest once against a chronicle with a genuine qualifying entry; note the proposal.
2. File that proposal as a real `wyrd` issue by hand (`gh issue create`), following the reported
   title/body.
3. Run the harvest again against the same (or an equivalent) friction log.

Expected: the second run reports the entry as a likely duplicate of the issue just filed, not as
a fresh new proposal (SC-003).

## 5. Confirm the two worked examples from `docs/design/16-session.md` sort correctly (SC-002)

Using the qualifying/non-qualifying pair the design document already gives:

- *Qualifying*: "The difficulty table gave a result the GM had not expected for an opposed test
  between a 65% skill and a 40% skill — played as written, noted for review." → must appear as a
  proposal (or `needs_review`, never `does_not_qualify`).
- *Non-qualifying*: "The player described their character's coat catching on a nail on the way
  out the door." → must never appear as a proposal.

## Expected outcome

An operator can point the script at one or more chronicle checkouts and get back a reviewable,
source-attributed, dedup-checked list of candidate `wyrd` issues — with nothing filed
automatically and nothing narrative leaking into a proposal.
