import pytest
from pathlib import Path
from app.scanner.security_scanner import scan_file_security
from app.scanner.slop_scanner import scan_file_slop
from app.scanner.gaps_scanner import scan_file_gaps
from app.scanner.loose_ends_scanner import scan_file_loose_ends
from app.scanner.dependency_scanner import scan_dependencies
from app.ingestion.dependency_parser import Dependency
from app.models.schemas import FindingCategory, Severity

def test_security_scanner_aws_and_sqli():
    code = """
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
"""
    findings = scan_file_security(Path("test.py"), "test.py", code)
    titles = [f.title for f in findings]
    assert any("AWS Access Key" in t for t in titles)
    assert any("SQL Injection" in t for t in titles)

def test_slop_scanner_echo_and_duplicates():
    code = """
import os
import os
# increment count
count += 1
# As an AI, here is the helper
"""
    findings = scan_file_slop(Path("test.py"), "test.py", code)
    assert any("Echo Comment" in f.title for f in findings)
    assert any("Duplicate Module Import" in f.title for f in findings)
    assert any("AI Prompt" in f.title for f in findings)

def test_gaps_scanner_empty_except():
    code = """
try:
    do_something()
except Exception:
    pass
"""
    findings = scan_file_gaps(Path("test.py"), "test.py", code)
    assert any("Swallowed Exception" in f.title for f in findings)

def test_loose_ends_todo_and_stub():
    code = """
# TODO: fix auth vulnerability before deployment
def calculate_metrics():
    pass
"""
    findings = scan_file_loose_ends(Path("test.py"), "test.py", code)
    assert any("TODO" in f.title for f in findings)
    assert any("Stub Method" in f.title for f in findings)

def test_dependency_scanner():
    deps = [
        Dependency(name="requests", version="2.25.1", ecosystem="PyPI", manifest_path="requirements.txt", line_number=1),
        Dependency(name="lodash", version="4.17.15", ecosystem="npm", manifest_path="package.json", line_number=2),
    ]
    findings = scan_dependencies(deps)
    assert len(findings) == 2
    assert findings[0].category == FindingCategory.DEPENDENCIES
    assert findings[0].severity == Severity.MEDIUM
    assert findings[1].severity == Severity.CRITICAL
