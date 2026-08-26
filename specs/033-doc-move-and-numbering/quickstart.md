# Quickstart: validating the move

```bash
# Every design doc and ADR resolves under its new path
ls docs/design/ | wc -l   # expect 30
ls docs/adr/*.md | wc -l  # expect 37 (plus superseded/)

# The retargeted link/index check passes clean
python3 tools/check_docs.py

# Every tools/ script that referenced design/ still passes its own tests
python3 -m unittest discover -s tools -p 'test_*.py'

# No word-corruption from the rewrite (CLAUDE.md's own three recorded incidents)
grep -rn "diffisecty\|secture\|otherworldly power, no database" . --include="*.md" --include="*.py"
# expect no output

# History survives the move
git log --oneline --follow docs/design/01-principles.md | tail -5

# Every open issue citing design/ now cites docs/design/ or docs/adr/
gh issue list --repo neilgfoster/wyrd --state open --search "design/" --json number,title
# expect zero results (all rewritten to doc/)
```
