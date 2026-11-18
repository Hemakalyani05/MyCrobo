# 🛡️ CodeSentinel AI
### Architecture-Agnostic AI Code Security & Quality Review Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg)](https://react.dev)
[![Tests](https://img.shields.io/badge/Tests-11%20Passed-emerald.svg)](backend/tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **CodeSentinel AI** is an autonomous, architecture-agnostic AI Code Security and Quality Review Agent. It audits software repositories across programming languages and frameworks, detects critical vulnerabilities, eliminates AI-generated slop, uncovers implementation gaps, catches technical debt, and synthesizes ready-to-apply unified diff patches.

---

## 🌟 Hackathon Requirements Matrix

| Hackathon Requirement | What It Means | How CodeSentinel AI Delivers |
|---|---|---|
| **Simple Agent** | Autonomous / semi-autonomous AI agent | Orchestrates multi-step scanning, context aggregation, false-positive filtering, scoring, and patch generation with real-time SSE streaming. |
| **Security** | Vulnerabilities & risky practices | Detects OWASP Top 10: SQL Injection, Command Injection, XSS, Hardcoded AWS/Stripe/JWT secrets, Path Traversal, Insecure Deserialization, Weak Cryptography, Permissive CORS. |
| **Slop** | Unnecessary, redundant, or AI-generated code | Uncovers echo/tautological comments, conversational AI markers, redundant try/catch re-raises, duplicate module imports, and nested type casting bloat. |
| **Coding Gaps** | Missing validations, errors & tests | Detects swallowed exceptions (`except: pass`, empty `catch {}`), ignored Go errors (`_ = db.Query`), sensitive endpoints lacking authentication decorators, and unhandled promises. |
| **Loose Ends** | Unfinished features, TODOs & stubs | Identifies prioritized `TODO`/`FIXME`/`HACK` comments, stubbed functions (`raise NotImplementedError`, `pass`), and abandoned debugging statements (`breakpoint()`, `debugger;`, `print`). |
| **Architecture Agnostic** | Works across tech stacks & languages | Automatically identifies 30+ languages (Python, JS/TS, Go, Java, Rust, C/C++, PHP, Ruby), detects frameworks (FastAPI, React, Express, Gin, Spring Boot), and parses manifests without configuration. |

---

## 🚀 Key Differentiators

1. **Hybrid Architecture (Deterministic + AI Agent):**
   Does not rely purely on an LLM or just a regex scanner. Combines high-speed deterministic AST and manifest analyzers with an AI reasoning agent that evaluates contextual exploitability.
2. **False-Positive Reduction:**
   Multi-file awareness prevents flagging test mock files or sanitized variables, ensuring developers only see actionable alerts.
3. **Automated Unified Diff Patch Generation:**
   Every verified finding is paired with a ready-to-review unified diff patch (`--- a/file\n+++ b/file`).
4. **1-Click Live File Patching:**
   Developers can click **"Apply Fix to File"** in the UI to instantly write the patch to disk.
5. **Zero-Config Offline Mode:**
   Includes a built-in expert heuristic reasoning engine that works 100% out of the box with **zero external API keys**, alongside support for **Google Gemini 2.5 Flash**, **OpenAI GPT-4o**, and **Local Ollama**.
6. **Multi-Format Export:**
   Export audit findings as **Standalone Interactive HTML**, **GitHub Markdown**, or **Machine-Readable JSON**.

---

## 🏛️ System Architecture

```
                                  ┌─────────────────────────────────────────┐
                                  │       CodeSentinel AI Web UI            │
                                  │ React 18 + Tailwind CSS + Lucide Icons  │
                                  └────────────────────┬────────────────────┘
                                                       │ SSE Stream / REST API
                                                       ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FastAPI Agent Backend                                           │
│                                                                                                   │
│  ┌───────────────────────┐   ┌───────────────────────────┐   ┌─────────────────────────────────┐  │
│  │   Repository Ingestion│──►│ Architecture & Language   │──►│  Deterministic Analysis Engine  │  │
│  │ Local / Git / Samples │   │         Detector          │   │  AST • OWASP • CVE Dependency   │  │
│  └───────────────────────┘   └───────────────────────────┘   └────────────────┬────────────────┘  │
│                                                                               │                   │
│                                      ┌────────────────────────────────────────┘                   │
│                                      ▼                                                            │
│     ┌───────────────────────────────────────────────────────────────────────────────────────┐     │
│     │                           Deterministic Scanner Disciplines                           │     │
│     │  • Security Engine: SQLi, Command Injection, XSS, Secrets, Crypto, Deserialization    │     │
│     │  • Slop Detector: Tautological comments, AI conversation markers, duplicate imports   │     │
│     │  • Coding Gaps: Swallowed exceptions (`pass`), empty catch blocks, unauthenticated API│     │
│     │  • Loose Ends: Prioritized TODOs/FIXMEs, unimplemented stubs, leftover debuggers      │     │
│     │  • Dependency Scanner: PyPI, npm, Go, Maven manifests matched against CVE database    │     │
│     └───────────────────────────────────────┬───────────────────────────────────────────────┘     │
│                                             ▼                                                     │
│     ┌───────────────────────────────────────────────────────────────────────────────────────┐     │
│     │                               AI Reasoning & Verification                             │     │
│     │  • Context validation & false-positive elimination                                    │     │
│     │  • Security Score computation (0-100) & Letter Grade (A+ to F)                        │     │
│     │  • Automated unified diff patch synthesis                                             │     │
│     │  • Engine Support: Built-in Heuristic, Google Gemini 2.5, OpenAI GPT-4o, Ollama       │     │
│     └───────────────────────────────────────┬───────────────────────────────────────────────┘     │
│                                             ▼                                                     │
│  ┌────────────────────────┐   ┌───────────────────────────┐   ┌────────────────────────────────┐  │
│  │     SQLite Database    │   │  Audit Report Exporter    │   │      Live Patch Engine         │  │
│  │  Scan History & Cache  │   │  HTML • Markdown • JSON   │   │   1-Click Direct File Repair   │  │
│  └────────────────────────┘   └───────────────────────────┘   └────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Benchmark Projects Included

CodeSentinel AI ships with 3 pre-built, realistic multi-stack benchmark projects in `sample_repos/` for instant evaluation:

1. **`vulnerable-python/` (FastAPI + SQLite + PyPI):**
   - Critical SQL injection via string formatting
   - Hardcoded AWS Secret Access Key
   - Swallowed exception with `except Exception: pass`
   - AI conversational prompt artifacts & duplicate module imports
   - Sensitive `/admin/purge` endpoint missing auth guard
   - Unresolved `TODO: Add JWT authentication`
   - Vulnerable `requests==2.25.1` (CVE-2023-32681) and `flask==2.1.0` (CVE-2023-30861)

2. **`vulnerable-node/` (Express + Node.js + npm):**
   - OS command injection via `child_process.exec` in `/api/ping`
   - Reflected Cross-Site Scripting (XSS)
   - Empty catch block `catch (err) {}`
   - Tautological comments & leftover `debugger;`
   - Vulnerable `lodash@4.17.15` (Prototype Pollution CVE-2020-8203) & `express@4.16.0`

3. **`vulnerable-go/` (Go + Gin Framework):**
   - Hardcoded live API secret token
   - SQL injection via `fmt.Sprintf`
   - Discarded error return values with blank identifier `_ = db.Query`
   - Unfinished database stubs & connection pool TODOs
   - Vulnerable `gin-gonic/gin v1.8.0`

---

## ⚡ Quickstart Guide

### 1. Requirements
- Python 3.10+
- Node.js 18+ & npm

### 2. Launch with One Command
```bash
./run.sh
```
This automatically sets up the Python virtual environment, builds the React frontend assets, and launches the unified server at **`http://localhost:8000`**.

### 3. Alternative: Running in Development Mode
If you wish to run backend and frontend with hot-reloading:

**Terminal 1 (FastAPI Backend):**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (React Vite Frontend):**
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 🧪 Automated Test Suite

Run the complete test suite verifying analyzers, scanners, diff generation, report exports, and API endpoints:

```bash
PYTHONPATH=backend backend/venv/bin/pytest backend/tests/ -v
```

Output:
```
backend/tests/test_api.py::test_health_endpoint PASSED
backend/tests/test_api.py::test_samples_endpoint PASSED
backend/tests/test_api.py::test_scan_and_export PASSED
backend/tests/test_pipeline.py::test_end_to_end_python_audit PASSED
backend/tests/test_pipeline.py::test_end_to_end_node_audit PASSED
backend/tests/test_pipeline.py::test_end_to_end_go_audit PASSED
backend/tests/test_scanners.py::test_security_scanner_aws_and_sqli PASSED
backend/tests/test_scanners.py::test_slop_scanner_echo_and_duplicates PASSED
backend/tests/test_scanners.py::test_gaps_scanner_empty_except PASSED
backend/tests/test_scanners.py::test_loose_ends_todo_and_stub PASSED
backend/tests/test_dependency_scanner PASSED

============================== 11 passed in 0.17s ==============================
```

---

## 🔌 REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check endpoint |
| `GET` | `/api/samples` | List pre-packaged benchmark sample repositories |
| `POST` | `/api/scan` | Run synchronous audit scan |
| `POST` | `/api/scan/stream` | Stream audit execution events via Server-Sent Events (SSE) |
| `GET` | `/api/scan/{scan_id}` | Retrieve complete audit report by ID |
| `GET` | `/api/history` | List previous audit runs and security scores |
| `POST` | `/api/patch/apply` | Apply a synthesized diff patch directly to a file |
| `GET` | `/api/export/{scan_id}?format={fmt}` | Export audit as `html`, `markdown`, or `json` |

### Example Scan via cURL:
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"source_type": "sample", "target": "vulnerable-python"}'
```

---

## 🛠️ Security Scoring Methodology

The Security Score ranges from **0 to 100** with calibrated letter grades:
- **Critical Severity:** -25 points (Exposed credentials, SQL injection, RCE)
- **High Severity:** -12 points (XSS, swallowed exceptions, unauthenticated admin routes)
- **Medium Severity:** -5 points (Weak crypto, unhandled promises, medium debt)
- **Low Severity:** -2 points (Echo comments, duplicate imports, minor TODOs)

| Score Range | Grade | Risk Level |
|---|---|---|
| 95 - 100 | **A+** | Exemplary hygiene, no actionable vulnerabilities |
| 85 - 94 | **A** | Strong security posture, minor hygiene items |
| 75 - 84 | **B** | Moderate security, attention recommended |
| 65 - 74 | **C** | Elevated risk, multiple coding gaps |
| 50 - 64 | **D** | High risk, severe vulnerabilities present |
| 0 - 49 | **F** | Critical security compromise, immediate patch required |

---

## 📄 License
MIT License. Built for the AI Agent Hackathon.
