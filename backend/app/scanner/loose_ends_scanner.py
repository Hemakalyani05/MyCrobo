import re
import uuid
from pathlib import Path
from typing import List
from ..models.schemas import Finding, FindingCategory, Severity

TODO_PATTERN = re.compile(r"""(?i)(?:#|//|/\*)\s*(TODO|FIXME|HACK|XXX|BUG|TEMP)\s*[:\-]?\s*(.+)""")
DEBUG_STATEMENT_PATTERNS = [
    (r"\b(?:breakpoint\(\)|import\s+pdb|pdb\.set_trace\(\))\b", "Python Debugger / Breakpoint Left in Code", Severity.HIGH),
    (r"\bdebugger;\b", "JavaScript Debugger Statement Left in Code", Severity.HIGH),
    (r"""\bconsole\.(?:log|debug)\s*\([^)]*(?:debug|test|fixme|dummy|here)[^)]*\)""", "Verbose Debug Logging in Production Code", Severity.LOW),
    (r"""\bprint\s*\([^)]*(?:debug|test|temporary|fixme)[^)]*\)""", "Debug Print Statement in Production Code", Severity.LOW),
]

STUB_PATTERN_PY = re.compile(r"""def\s+(\w+)\([^)]*\)(?:\s*->\s*[^:]+)?:\s*\n\s*(?:pass|raise\s+NotImplementedError(?:\([^)]*\))?|\.\.\.)\s*$""", re.MULTILINE)
STUB_PATTERN_JS = re.compile(r"""(?:function\s+(\w+)|(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)\s*\{\s*(?://[^\n]*\n\s*)?(?:return\s+null;|throw\s+new\s+Error\(['"]Not implemented['"]\);)?\s*\}""")

def scan_file_loose_ends(file_path: Path, rel_path: str, content: str) -> List[Finding]:
    findings = []
    lines = content.splitlines()

    # 1. Scrutinize TODO / FIXME / HACK
    for idx, line in enumerate(lines, 1):
        match = TODO_PATTERN.search(line)
        if match:
            tag = match.group(1).upper()
            detail = match.group(2).strip().rstrip("*/")
            
            # Elevate severity if it touches security, auth, or validation
            is_critical = any(kw in detail.lower() for kw in ["security", "auth", "token", "password", "sanitize", "leak", "vulnerab", "cve"])
            severity = Severity.HIGH if is_critical else (Severity.MEDIUM if tag in ["FIXME", "BUG"] else Severity.LOW)

            snippet = f"{idx}: {line.strip()}"
            findings.append(Finding(
                id=f"loose-{uuid.uuid4().hex[:8]}",
                title=f"Unresolved {tag}: {detail[:50]}...",
                category=FindingCategory.LOOSE_ENDS,
                severity=severity,
                file_path=rel_path,
                line_number=idx,
                snippet=snippet,
                explanation=f"Found unfinished technical debt marker `{tag}`: \"{detail}\". Incomplete logic can lead to regressions or exposed security vectors.",
                evidence=f"{tag} item at line {idx}: `{detail}`",
                remediation=f"Complete the remaining implementation or create a tracked issue: {detail}",
                confidence=0.99,
                verified=True
            ))

    # 2. Leftover Debugger statements
    for idx, line in enumerate(lines, 1):
        for pat, title, sev in DEBUG_STATEMENT_PATTERNS:
            if re.search(pat, line):
                snippet = f"{idx}: {line.strip()}"
                findings.append(Finding(
                    id=f"loose-{uuid.uuid4().hex[:8]}",
                    title=title,
                    category=FindingCategory.LOOSE_ENDS,
                    severity=sev,
                    file_path=rel_path,
                    line_number=idx,
                    snippet=snippet,
                    explanation="Development debugging artifact detected. In production, this can halt thread execution or leak sensitive operational runtime states.",
                    evidence=f"Debugging artifact at line {idx}: `{line.strip()}`",
                    remediation="Remove debugger breakpoint and development log calls prior to release.",
                    confidence=0.99,
                    verified=True
                ))

    # 3. Stub implementations in Python
    for match in STUB_PATTERN_PY.finditer(content):
        start_pos = match.start()
        line_no = content[:start_pos].count("\n") + 1
        fn_name = match.group(1)
        snippet = match.group(0)
        findings.append(Finding(
            id=f"loose-{uuid.uuid4().hex[:8]}",
            title=f"Incomplete Stub Method `{fn_name}`",
            category=FindingCategory.LOOSE_ENDS,
            severity=Severity.MEDIUM,
            file_path=rel_path,
            line_number=line_no,
            snippet=snippet,
            explanation=f"The function `{fn_name}` is declared but only contains a placeholder (`pass` or `raise NotImplementedError`). Calling this at runtime will trigger unexpected behavior.",
            evidence=f"Placeholder stub at line {line_no}",
            remediation=f"Implement the concrete logic for `{fn_name}` or mark the enclosing class as an abstract interface.",
            confidence=0.95,
            verified=True
        ))

    return findings
