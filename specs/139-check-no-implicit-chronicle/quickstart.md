# Quickstart: Check: no implicit current-chronicle global state

## Run it

```bash
cd /root/source/neilgfoster/wyrd
python3 tools/check_no_implicit_chronicle.py
```

Expected against the real repo today: exits `0`, reporting the one existing justified exception
(`resolution._open_proposals`) and that no unjustified candidate was found.

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
python3 -m unittest discover -s tools -p 'test_check_no_implicit_chronicle.py'
```

## Expected outcome

Both a passing scratch case (a justified global) and a failing scratch case (an unjustified
global) are exercised, plus a real-repo pass confirming SC-001.
