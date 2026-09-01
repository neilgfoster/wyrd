# Quickstart: Character creation procedure

## Prerequisites

- #221-#231 already merged.
- Run from a scratch directory with `PYTHONPATH=<repo>/engine`.

## 1. A valid creation produces a complete character

```bash
python3 -m wyrd.client create-character \
  --path aria.md --name "Aria Nightingale" \
  --career-json '{"skills": {"stealth": 55, "swordplay": 45}, "entry_point": true}' \
  --actions-json '[{"action":"open","skill":"stealth"},{"action":"open","skill":"swordplay"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"swordplay"},{"action":"raise","skill":"swordplay"}]' \
  --loyalty "the-old-guard" --mortality standard --fault-line "She trusts no one, because the guild sold her out once."
```

Expected: `valid: true`, `frontmatter.stamina` is `{current: 6, max: 6}`, `frontmatter.fate`/
`fortune` are 3, `frontmatter.skills` is `{"stealth": 45, "swordplay": 35}`.

## 2. The file on disk is a valid character entity

```bash
python3 -m wyrd.client character-load --path aria.md
```

Expected: loads without error, identical frontmatter to what creation reported (SC-005).

## 3. A rejected allocation writes nothing

```bash
rm -f bad.md
python3 -m wyrd.client create-character \
  --path bad.md --name "X" \
  --career-json '{"skills": {"stealth": 55}, "entry_point": true}' \
  --actions-json '[]' \
  --loyalty "x" --mortality standard --fault-line "x"
ls bad.md 2>&1  # expect: No such file or directory
```

Expected: `valid: false`, and `bad.md` was never created (SC-003).

## 4. Mortality drives Fate/Fortune

Repeat step 1 with `--mortality low` and `--mortality high`; expect Fate/Fortune 2 and 4
respectively (SC-001).

## Running the automated suite

```bash
python3 -m unittest discover -s tests/engine
```
