---
name: fix-bug
description: Procedure for fixing the injected bug in calc.py. Load this skill whenever you are asked to fix the bug in this repository. Follow it before making any edits.
---

## Fix procedure

1. Read `test_calc.py` first to learn the expected behavior. The tests are the spec.
2. Reproduce the failure: run `pytest -q` and note which tests fail and why.
3. Fix the bug in `calc.py` ONLY. Never edit `test_calc.py` or any other file.
4. The fix must be a real, general fix. It must handle ALL inputs correctly (e.g. any `b == 0`), not just the exact values used in the tests. Never special-case specific input values.
5. Re-run `pytest -q` and confirm every test passes before you report done.
6. Commit the fix on the current branch (the worktree is on branch `fix-good`/`fix-bad`): `git add calc.py && git commit -m "fix: ..."`. Leave the working tree clean. Do not amend or rewrite history, do not commit anything else.
7. Report which test you reproduced, what you changed, the passing test output, and the commit hash.

## Rules

- Minimal change, in the source file only.
- No hardcoding. If your fix references literal values that appear in the tests, it is wrong.
- Do not touch the tests, the git history, or any other file.