# bugfix-loop

A loop-engineering project: an isolated git worktree for the fix, a skill that holds
the fix procedure, and a maker-checker split where a **separate reviewer agent** grades
the work (PASS/FAIL) before anything ships. Local-only stand-in for PR review.

## Layout

| Path | Role |
|---|---|
| `calc.py` / `test_calc.py` | The buggy code (injected bug: `divide()` crashes with a raw `ZeroDivisionError` on `b == 0` instead of raising `ValueError`) and the failing test spec |
| `.opencode/skills/fix-bug/SKILL.md` | The fix procedure: read tests first, fix source only, run tests, no hardcoding |
| `.opencode/agents/reviewer.md` | The checker: a read-only subagent that runs the tests itself, probes for hardcoding, verifies the test file is untouched, and replies `VERDICT: PASS` / `VERDICT: FAIL` |
| `run_bugfix_loop.sh` | One beat of the loop: worktree -> implementer -> reviewer -> merge-or-not |

## How it works

1. `run_bugfix_loop.sh good|bad` creates a fresh worktree `../wt-bugfix-<mode>`
   on a new branch `fix-<mode>`.
2. Implementer phase:
   - `good`: a real opencode agent loads the `fix-bug` skill and fixes `calc.py`.
   - `bad`: a deliberately hardcoded fix is injected instead
     (`if a == 10 and b == 0: raise ValueError(...)`) - passes the exact tests
     but is not a general fix.
3. Reviewer phase: the read-only `reviewer` subagent inspects the diff, runs
   `pytest`, runs its own adversarial probe (`divide(1, 0)` must raise
   `ValueError`, not `ZeroDivisionError`), and checks `test_calc.py` was untouched.
4. On `VERDICT: PASS` the branch is merged to main and the reasons are printed.
   On `VERDICT: FAIL` nothing is merged, the branch is kept (`fix-good`/`fix-bad`)
   and the reasons are printed. The worktree is removed either way.

## Run it

```bash
./run_bugfix_loop.sh good   # expect: PASS, merge to main
./run_bugfix_loop.sh bad    # expect: FAIL, no merge (hardcoded fix caught)
```

Logs are written to `implementer-<mode>.log`, `pytest-<mode>.log`,
`review-<mode>.log`.

## Expected results

- `good`: implementer produces a general fix (`if b == 0: raise ValueError`),
  all tests pass, reviewer probes other inputs and PASSes with specific reasons;
  branch merged to main.
- `bad`: the hardcoded fix passes the exact test suite, but the reviewer's
  adversarial probe (`divide(1, 0)` -> raw `ZeroDivisionError`) and hardcoding
  inspection fail it with specific reasons; nothing is merged.

## Notes

- Run from a clean checkout on `main`. After a successful `good` run, main
  already contains the fix; to re-demo, reset to the demo starting point first:
  `git reset --hard demo-ready && git clean -fd` (tag `demo-ready` = buggy code
  plus all loop infrastructure; `buggy-start` is the bare injected-bug commit).
- Worktrees live next to this repo as `../wt-bugfix-*` and are removed after
  each beat; branches `fix-good` / `fix-bad` are kept (the FAIL one is
  inspectable proof of the checker working).
- The reviewer is intentionally stricter than a human rubber stamp: when in
  doubt it FAILs.