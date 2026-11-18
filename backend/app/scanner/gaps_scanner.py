import re
import uuid
from pathlib import Path
from typing import List
from ..models.schemas import Finding, FindingCategory, Severity

EMPTY_CATCH_JS = re.compile(r"""catch\s*\([^)]*\)\s*\{\s*(?://[^\n]*\n\s*|/\*[\s\S]*?\*/\s*)*\}""")
UNHANDLED_FETCH = re.compile(r"""\bfetch\([^)]+\)\.then\([^)]+\)(?!\.catch)""")

def scan_file_gaps(file_path: Path, rel_path: str, content: str) -> List[Finding]:
    findings = []
    lines = content.splitlines()

    # 1. Swallowed Exception in Python: except ... : pass (even with comments)
    if file_path.suffix == ".py":
        for idx in range(len(lines)):
            line = lines[idx]
            clean = line.strip()
            if clean.startswith("except") and clean.endswith(":"):
                # Inspect following non-empty lines in same indentation block
                except_indent = len(line) - len(line.lstrip())
                for j in range(idx + 1, min(len(lines), idx + 10)):
                    sub_line = lines[j]
                    sub_clean = sub_line.strip()
                    if not sub_clean or sub_clean.startswith("#"):
                        continue
                    sub_indent = len(sub_line) - len(sub_line.lstrip())
                    if sub_indent <= except_indent:
                        # Exited block without statements
                        break
                    if sub_clean in ("pass", "..."):
                        snippet = f"{idx+1}: {line}\n{j+1}: {sub_line}"
                        findings.append(Finding(
                            id=f"gap-{uuid.uuid4().hex[:8]}",
                            title="Swallowed Exception / Silent Failure (Coding Gap)",
                            category=FindingCategory.GAPS,
                            severity=Severity.HIGH,
                            file_path=rel_path,
                            line_number=idx + 1,
                            snippet=snippet,
                            explanation="The exception block suppresses errors using `pass` without logging or recovery. Silent failures obscure critical operational errors and data corruption.",
                            evidence=f"Silent error suppression at line {idx+1}: `{clean}` -> `{sub_clean}`",
                            remediation="Log the error using a structured logger (e.g., `logger.exception()`) and return an appropriate error response or fallback.",
                            cwe_id="CWE-390",
                            confidence=0.98,
                            verified=True
                        ))
                    break

    # 2. Empty Catch in JS/TS
    for match in EMPTY_CATCH_JS.finditer(content):
        start_pos = match.start()
        line_no = content[:start_pos].count("\n") + 1
        snippet = match.group(0)
        findings.append(Finding(
            id=f"gap-{uuid.uuid4().hex[:8]}",
            title="Empty Catch Block / Swallowed Error",
            category=FindingCategory.GAPS,
            severity=Severity.HIGH,
            file_path=rel_path,
            line_number=line_no,
            snippet=snippet,
            explanation="Empty `catch {}` block completely ignores caught exceptions, making runtime debugging impossible and masking failures.",
            evidence=f"Empty error catch at line {line_no}",
            remediation="Log the error with `console.error(err)` or propagate to a global error handler middleware.",
            cwe_id="CWE-390",
            confidence=0.98,
            verified=True
        ))

    # 3. Discarded Go Errors
    if file_path.suffix == ".go":
        for idx, line in enumerate(lines, 1):
            if "_ = " in line and ("Error" in line or "Close" in line or "Query" in line or "Exec" in line):
                snippet = f"{idx}: {line.strip()}"
                findings.append(Finding(
                    id=f"gap-{uuid.uuid4().hex[:8]}",
                    title="Ignored Error Return Value in Go",
                    category=FindingCategory.GAPS,
                    severity=Severity.MEDIUM,
                    file_path=rel_path,
                    line_number=idx,
                    snippet=snippet,
                    explanation="In Go, discarding error returns with the blank identifier `_` ignores critical I/O or database failures.",
                    evidence=f"Discarded error at line {idx}: `{line.strip()}`",
                    remediation="Handle the returned error explicitly: `if err != nil { return err }`.",
                    cwe_id="CWE-391",
                    confidence=0.95,
                    verified=True
                ))

    # 4. Sensitive Admin / Mutation Routes Missing Authentication Guards
    route_pat = re.compile(r"""(?i)@(app|router)\.(?:post|put|delete|patch)\(['"]/(?:admin|delete|users|settings|roles)""")
    for idx, line in enumerate(lines, 1):
        if route_pat.search(line):
            # Check function definition signature line
            fn_sig = ""
            for j in range(idx, min(len(lines), idx + 5)):
                if lines[j].strip().startswith("def "):
                    fn_sig = lines[j].strip()
                    break
            if fn_sig and not any(kw in fn_sig for kw in ["Depends", "Security", "auth", "current_user", "verify"]):
                snippet = f"{idx}: {line.strip()}\n{fn_sig}"
                findings.append(Finding(
                    id=f"gap-{uuid.uuid4().hex[:8]}",
                    title="Sensitive Route Handler Missing Auth Guard",
                    category=FindingCategory.GAPS,
                    severity=Severity.HIGH,
                    file_path=rel_path,
                    line_number=idx,
                    snippet=snippet,
                    explanation="Administrative or state-modifying route endpoint declared without an explicit authentication/authorization dependency guard in signature.",
                    evidence=f"Endpoint `{line.strip()}` lacks auth dependency in signature `{fn_sig}`",
                    remediation="Add security middleware or dependency: e.g. `dependencies=[Depends(get_current_admin)]`.",
                    cwe_id="CWE-306",
                    confidence=0.90,
                    verified=True
                ))

    # 5. Unhandled Promise in JavaScript
    for idx, line in enumerate(lines, 1):
        if UNHANDLED_FETCH.search(line):
            snippet = f"{idx}: {line.strip()}"
            findings.append(Finding(
                id=f"gap-{uuid.uuid4().hex[:8]}",
                title="Unhandled Promise Chain Missing .catch()",
                category=FindingCategory.GAPS,
                severity=Severity.MEDIUM,
                file_path=rel_path,
                line_number=idx,
                snippet=snippet,
                explanation="Promise chain executes asynchronous requests without a terminating `.catch()` error handler, causing unhandled promise rejections.",
                evidence=f"Uncaught promise chain at line {idx}: `{line.strip()}`",
                remediation="Append a `.catch(err => { ... })` handler or refactor using `async/await` with `try/catch`.",
                cwe_id="CWE-754",
                confidence=0.92,
                verified=True
            ))

    return findings
