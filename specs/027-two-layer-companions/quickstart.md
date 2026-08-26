# Quickstart: verifying two-layer companions and a positive party track

This feature has no runtime to launch — verification is document review plus a checker script.

## Prerequisites

- Repo checked out at branch `027-two-layer-companions`.
- Python 3 on `PATH` (stdlib only).

## Run the new check

```bash
python3 tools/check_companion_layers.py
```

Expected: exits 0 and reports the mechanical-layer field count, the party-size bound it was
checked against, and confirmation that no field appears on both layers and that `03-rules.md`
names no mechanical field absent from `04-session.md`'s list.

## Run the repo-wide checks that must stay green

```bash
python3 tools/check_docs.py
grep -riE '\b(setting-or-system-term-placeholder)\b' design/ || true   # manual scan, see below
```

There is no single fixed vocabulary list to grep automatically (per prior features in this repo);
manually re-read the two amended documents for any term that only makes sense to someone who has
read a specific published book, per `CLAUDE.md`.

## Manual review checklist

1. Read `docs/design/16-session.md`'s companion section end to end. Confirm exactly one mechanism is
   presented as "what a well-functioning party earns" (SC-002) — Bond's completed positive
   effect — with no second competing candidate left standing.
2. Read `docs/design/03-rules.md`'s companion/succession passage and `docs/design/16-session.md`'s
   companion record side by side. Confirm every field name is used in the same sense in both
   (SC-004).
3. Confirm `docs/adr/0034-bond-is-the-positive-party-track.md` exists, is dated, and states the
   rejected alternative.
4. Confirm no new numeric competence/capability field was introduced for companions anywhere in
   the diff (`git diff main -- design/ | grep -i companion`).

## Expected outcome

All of the above pass, matching the spec's acceptance criteria:
- [ ] Companions have two defined layers.
- [ ] A functioning party has a mechanical expression (Bond's completed effect) — or an ADR says
      why not (not applicable here; the effect is defined).
- [ ] A full party can be run without per-companion bookkeeping (verified by the field-count bound
      in `data-model.md`).
