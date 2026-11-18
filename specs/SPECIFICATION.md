# Technical Specification: Autonomous Maker-Checker Bugfix Loop

## 1. System Overview & Objective

The **Autonomous Maker-Checker Bugfix Loop** is an agentic software engineering system designed to eliminate single-agent hallucination and reward-hacking during automated bug repair. 

In traditional single-agent architectures, an LLM given write permission often implements lazy or hardcoded fixes to pass unit tests without truly fixing the root cause. This system solves that problem by introducing a **strict Maker-Checker split** enforced by isolated Git worktrees, role-based permission boundaries, and mandatory adversarial probing.

```
                  ┌────────────────────────────────────────┐
                  │          Injected Bug in Code          │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │     1. Isolated Worktree Sandbox       │
                  │        (git worktree add ../wt)        │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │       2. Maker Agent (Builder)         │
                  │   Loads fix-bug skill -> Fixes Source  │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │       3. Sanity Test Suite Run         │
                  │              (pytest -q)               │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │       4. Checker Agent (Auditor)       │
                  │   Read-Only Audit + Adversarial Probe  │
                  └───────────────────┬────────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
               [VERDICT: PASS]             [VERDICT: FAIL]
                         │                         │
                         ▼                         ▼
             Merge Branch into main      Block Merge & Keep Branch
             (Ship to Production)        (Inspect Agentic Failure)
```

---

## 2. Agent Specifications & Permission Boundaries

| Property | Agent 1: Maker (Builder) | Agent 2: Checker (Auditor) |
|---|---|---|
| **Role** | Code Implementer & Bug Fixer | Independent QA Auditor & Security Gate |
| **Model** | `opencode/build` | `opencode/deepseek-v4-flash-free` |
| **Workspace** | Isolated Git Worktree (`../wt-bugfix-<mode>`) | Same Isolated Git Worktree (Read-Only) |
| **Write Permission** | **ALLOWED**: `calc.py` only | **DENIED**: Read-only (`permission.edit: deny`) |
| **Test Modification** | **STRICTLY FORBIDDEN**: Never touches `test_*.py` | Verified automatically via `git diff` |
| **CLI / Bash Tools** | Sandboxed shell commands for running tests | Restricted to `pytest`, `python`, and `git` |
| **Skill Loaded** | `.opencode/skills/fix-bug/SKILL.md` | Audit rules from `.opencode/agents/reviewer.md` |
| **Output Format** | Commit message on isolated branch | Single unambiguous verdict line: `VERDICT: PASS` or `VERDICT: FAIL` |

---

## 3. Maker-Checker Protocol & State Machine

### Phase 1: Sandbox Isolation
* To protect the production `main` branch, every fix attempt is executed inside a detached Git worktree (`wt-bugfix-good` or `wt-bugfix-bad`) on an ephemeral branch (`fix-good` / `fix-bad`).
* Invariant: `main` branch working tree remains untouched until an explicit `VERDICT: PASS` is signed off by the Checker.

### Phase 2: Maker Execution (Builder Phase)
1. **Spec Reading**: The Maker loads the `fix-bug` skill and reads unit tests (`test_calc.py`) to understand expected behavior.
2. **Failure Reproduction**: The Maker executes `pytest -q` to confirm the reproduction of the injected failure.
3. **Source Repair**: The Maker patches `calc.py` strictly.
4. **Clean Commit**: The Maker commits the change ahead of `main` with a descriptive commit message.

### Phase 3: Sanity Test Verification
* The orchestrator triggers `pytest -q` inside the worktree.
* If unit tests fail at this stage, the loop immediately halts without invoking the Checker.

### Phase 4: Checker Audit (Checker Phase)
The Checker executes a sequential, deterministic 8-step audit procedure:
1. **Commit Integrity Check**: Verifies `git status --porcelain` is clean (uncommitted changes cause automatic `FAIL`).
2. **Branch Advance Check**: Verifies `git log --oneline main..HEAD` contains at least one new commit.
3. **Test File Invariance Check**: Verifies `git diff main...HEAD -- test_calc.py` is empty (modifying test specs is an automatic `FAIL`).
4. **Generality Inspection**: Scans diff for suspicious hardcoded literals (e.g. `if a == 10 and b == 0`).
5. **Adversarial Probe Execution**: Executes probe commands with unseen edge inputs (e.g., `divide(1, 0)`).
6. **Verdict Emission**: Emits `VERDICT: PASS` or `VERDICT: FAIL` with granular diagnostic citations.

### Phase 5: Gated Merge or Rejection
* **On `PASS`**: The branch is merged into `main` using `--no-ff` (`Merge fix-good (reviewer verdict: PASS)`).
* **On `FAIL`**: No merge occurs. The failed branch (`fix-bad`) is preserved for inspection and audit trails.
* **Cleanup**: Detached worktree directory is wiped regardless of outcome.

---

## 4. Observability & Dual-Engine Architecture

To make the system transparent and accessible to both technical engineers and non-technical stakeholders, the project provides a unified **Observability Dashboard**:

* **Live Local Engine (`run_dashboard.py`)**:
  - Connects via WebSockets to the Python runner.
  - Spawns real `opencode.cmd` subagents and captures stdout/stderr in real time.
* **Cloud Interactive Engine (Vercel)**:
  - Deploys as an Edge static frontend with dedicated `/api` serverless functions.
  - Automatically simulates full agentic thought process, diff visualization, and adversarial probe checks with zero server timeouts or container crashes.
