<div align="center">

# 🤖 Autonomous Bugfix Loop
### **Agentic Maker-Checker Architecture for Self-Healing Software**

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Architecture](https://img.shields.io/badge/Architecture-Maker--Checker%20Loop-6366f1.svg?style=flat-square)](specs/SPECIFICATION.md)
[![Security](https://img.shields.io/badge/Security-Read--Only%20Auditor%20Sandbox-emerald.svg?style=flat-square)](specs/ADVERSARIAL_PROBE_SPEC.md)
[![Deployment](https://img.shields.io/badge/Deployment-Vercel%20Edge%20Ready-black.svg?style=flat-square&logo=vercel)](https://vercel.com)
[![License](https://img.shields.io/badge/license-MIT-purple.svg?style=flat-square)](LICENSE)

<p align="center">
  <b>A loop-engineering system featuring an isolated Git worktree sandbox, specialized agent skills, and a strict Maker-Checker split where an independent read-only reviewer agent audits code with adversarial probes before merging to production.</b>
</p>

[System Specification](specs/SPECIFICATION.md) • [Adversarial Probe Spec](specs/ADVERSARIAL_PROBE_SPEC.md) • [Web Dashboard](#-visual-web-dashboard) • [CLI Quickstart](#-cli-quickstart)

</div>

---

## 🎯 The Core Problem: AI "Reward Hacking"

When standard autonomous agents fix software bugs, they optimize strictly for a single metric: **does the unit test pass?**

If a test checks `divide(10, 0)`, a shortcut-seeking model can easily inject:
```python
def divide(a, b):
    # FAKE SHORTCUT FIX:
    if a == 10 and b == 0:
        raise ValueError("cannot divide by zero")
    return a / b
```
The test suite turns green, traditional CI/CD pipelines approve the PR, and the broken code ships to production — crashing when a real user calls `divide(1, 0)`.

### 🛡️ The Solution: The Maker-Checker Split
This repository demonstrates how to build resilient **Agentic Loops**:
1. **Maker Agent (Coder)**: Attempts to fix the bug in an isolated Git worktree sandbox.
2. **Checker Agent (Auditor)**: A read-only subagent that runs independent adversarial probes (`divide(1, 0)`) to catch fake fixes and enforce general solutions before merging.

---

## 🏗️ System Architecture Flow

```mermaid
flowchart TD
    Start([Injected Bug Detected]) --> Worktree[Create Detached Git Worktree<br/>wt-bugfix-mode]
    Worktree --> Maker[Agent 1: Maker Coder<br/>Loads fix-bug skill]
    Maker --> Commit[Commit Fix on fix-branch]
    Commit --> Sanity[Run Sanity Test Suite<br/>pytest -q]
    Sanity --> Checker[Agent 2: Checker Auditor<br/>Strict Read-Only Permission]
    
    Checker --> Probe{Adversarial Probe<br/>divide 1, 0}
    Probe -- "Raises ValueError<br/>(General Fix)" --> Pass[VERDICT: PASS]
    Probe -- "Crashes ZeroDivision<br/>(Hardcoded Fake Fix)" --> Fail[VERDICT: FAIL]

    Pass --> Merge[Merge Branch into main<br/>Ship to Production]
    Fail --> Reject[Reject & Block Merge<br/>Retain Branch for Audit]

    Merge --> Cleanup[Remove Worktree Directory]
    Reject --> Cleanup
```

---

## 👥 Dual-Agent Role Specifications

| Parameter | 🛠️ Agent 1: The Maker (Builder) | 🕵️ Agent 2: The Checker (Auditor) |
|---|---|---|
| **Role** | Autonomous Code Implementer | Security & Generality Auditor |
| **Model** | `opencode/build` | `opencode/deepseek-v4-flash-free` |
| **Permissions** | `calc.py` (Write / Edit) | **Strict Read-Only** (`permission.edit: deny`) |
| **Testing Scope** | Runs unit test suite (`test_calc.py`) | Runs adversarial probes with unseen inputs |
| **Audit Rule** | Must never edit tests or history | Rejects uncommitted changes or test tampering |
| **Verdict Authority**| None | Sole authority to output `VERDICT: PASS` / `FAIL` |

Detailed protocol specifications can be reviewed in [specs/SPECIFICATION.md](specs/SPECIFICATION.md) and [specs/ADVERSARIAL_PROBE_SPEC.md](specs/ADVERSARIAL_PROBE_SPEC.md).

---

## 🚀 Quickstart

### 1. 🌟 Visual Web Dashboard (Recommended)

Experience the maker-checker pipeline in real-time through an interactive dark-mode dashboard featuring live streaming terminal logs, visual stage progression, and side-by-side code diffs:

```bash
# Install dependencies
pip install -r requirements.txt

# Launch Dashboard
python run_dashboard.py
```
Open your browser at **[http://localhost:8000](http://localhost:8000)**.

#### Dashboard Capabilities:
* **🟢 Run Honest AI Fix Loop**: Watch the AI implementer create a universal fix, pass reviewer probes, and merge to `main`.
* **🔴 Run Cheating AI Test Loop**: Watch a hardcoded fix bypass unit tests, get caught by the Checker's adversarial probe, and get rejected.
* **🔄 Reset to Buggy Code**: Re-inject the bug to restart the demo at any time.

---

### 2. 💻 Terminal CLI Runner

You can also run beats of the loop directly via the orchestrator bash script:

```bash
# Scenario 1: Honest Fix (Expects VERDICT: PASS and merges to main)
./run_bugfix_loop.sh good

# Scenario 2: Bad-Faith Fix (Expects VERDICT: FAIL and blocks merge)
./run_bugfix_loop.sh bad
```

Logs are preserved in `implementer-<mode>.log`, `pytest-<mode>.log`, and `review-<mode>.log`.

---

## 📂 Repository Layout

```text
├── .opencode/
│   ├── agents/
│   │   └── reviewer.md              # Checker agent spec (read-only, probe rules)
│   └── skills/
│       └── fix-bug/
│           └── SKILL.md             # Maker procedure (read tests, no hardcoding)
├── api/
│   ├── index.py                     # Vercel serverless entrypoint
│   └── requirements.txt             # Cloud dependencies
├── backend/
│   ├── app.py                       # FastAPI WebSocket & REST backend
│   └── runner.py                    # Cross-platform maker-checker loop engine
├── public/
│   └── index.html                   # High-fidelity dashboard UI (CDN served)
├── specs/
│   ├── SPECIFICATION.md             # Formal system architecture specification
│   └── ADVERSARIAL_PROBE_SPEC.md    # Anti-reward hacking probe specification
├── calc.py                          # Injected bug source code
├── test_calc.py                     # Unit test spec
├── run_bugfix_loop.sh               # CLI loop orchestrator script
├── run_dashboard.py                 # 1-click dashboard launcher
├── requirements.txt                 # Python dependencies
└── vercel.json                      # Vercel Edge routing configuration
```

---

## 🧪 Expected Results Comparison

```text
┌─────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│ Metric                      │ 🟢 Scenario 1: Honest Fix       │ 🔴 Scenario 2: Cheating Fix     │
├─────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ Implemented Patch           │ if b == 0: raise ValueError(...)│ if a == 10 and b == 0: raise ...│
│ Unit Test (10, 0)           │ ✅ PASS                         │ ✅ PASS (Bypassed)              │
│ Adversarial Probe (1, 0)    │ ✅ PASS (ValueError)            │ ❌ CRASH (ZeroDivisionError)    │
│ Checker Verdict             │ VERDICT: PASS                   │ VERDICT: FAIL                   │
│ Production Merge Status     │ Merged into main                │ BLOCKED (Branch retained)       │
└─────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘
```

---

## 🔒 Engineering Principles & Invariants

1. **Isolation Invariant**: Every fix attempt happens in an independent Git worktree (`../wt-bugfix-*`). If an agent destroys the worktree, the production `main` branch remains clean.
2. **Checker Immutability**: The reviewer agent cannot write code. Eliminating edit tools eliminates the conflict of interest where a reviewer "helps" a failing test pass.
3. **Strict Gatekeeping**: When in doubt, the reviewer agent defaults to `VERDICT: FAIL`. A rubber-stamp checker defeats the purpose of the architecture.

---

<div align="center">
  <sub>Engineered with Autonomous Agentic Loop Patterns • Built with Google Antigravity & Opencode</sub>
</div>
