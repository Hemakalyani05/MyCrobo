import pytest
from app.models.schemas import ScanRequest
from app.agent.orchestrator import AuditOrchestrator
from app.agent.reporter import Reporter
from app.agent.patch_generator import PatchGenerator
from pathlib import Path

@pytest.mark.asyncio
async def test_end_to_end_python_audit():
    req = ScanRequest(source_type="sample", target="vulnerable-python")
    orchestrator = AuditOrchestrator(req)
    report = await orchestrator.execute_scan()

    assert report.metadata.repo_name == "vulnerable-python"
    assert report.summary.total_findings > 5
    # Since it contains critical SQL injection and AWS key, score should be low
    assert report.summary.security_score < 70
    assert report.summary.grade in ["D", "F"]

    # Verify findings categories
    cats = [f.category.value for f in report.findings]
    assert "security" in cats
    assert "slop" in cats
    assert "gaps" in cats
    assert "loose_ends" in cats
    assert "dependencies" in cats

    # Verify diff patches are attached
    patches = [f.diff_patch for f in report.findings if f.diff_patch]
    assert len(patches) > 0

    # Verify reports generation
    md = Reporter.to_markdown(report)
    assert "CodeSentinel AI Audit Report" in md
    assert "Executive AI Assessment" in md

    html = Reporter.to_html(report)
    assert "CodeSentinel AI Audit" in html

@pytest.mark.asyncio
async def test_end_to_end_node_audit():
    req = ScanRequest(source_type="sample", target="vulnerable-node")
    orchestrator = AuditOrchestrator(req)
    report = await orchestrator.execute_scan()

    assert report.metadata.repo_name == "vulnerable-node"
    assert report.summary.total_findings >= 3
    # Look for command injection or XSS
    titles = [f.title for f in report.findings]
    assert any("Command Injection" in t or "XSS" in t for t in titles)

@pytest.mark.asyncio
async def test_end_to_end_go_audit():
    req = ScanRequest(source_type="sample", target="vulnerable-go")
    orchestrator = AuditOrchestrator(req)
    report = await orchestrator.execute_scan()

    assert report.metadata.repo_name == "vulnerable-go"
    assert report.summary.total_findings >= 3
