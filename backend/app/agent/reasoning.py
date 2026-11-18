from pathlib import Path
from typing import List, Dict, Any, Tuple
from ..models.schemas import Finding, FindingCategory, Severity, ScanSummary, RepoMetadata
from .patch_generator import PatchGenerator
from .llm_client import LLMClient

class ReasoningAgent:
    def __init__(self, repo_path: str, metadata: RepoMetadata, llm_client: LLMClient):
        self.repo_path = Path(repo_path)
        self.metadata = metadata
        self.llm = llm_client

    async def verify_and_enrich(self, raw_findings: List[Finding]) -> Tuple[List[Finding], ScanSummary, str]:
        verified_findings: List[Finding] = []
        filtered_count = 0

        # Cache file contents to speed up diff synthesis
        file_cache: Dict[str, str] = {}

        for finding in raw_findings:
            # 1. False Positive Checks
            if self._is_false_positive(finding):
                filtered_count += 1
                continue

            # Read file content for diff generation
            rel_p = finding.file_path
            if rel_p not in file_cache:
                full_p = self.repo_path / rel_p
                if full_p.is_file():
                    try:
                        file_cache[rel_p] = full_p.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        file_cache[rel_p] = ""
                else:
                    file_cache[rel_p] = ""

            # 2. Attach Unified Diff Patch
            patch = PatchGenerator.generate_diff(finding, file_cache.get(rel_p))
            finding.diff_patch = patch
            finding.verified = True

            verified_findings.append(finding)

        # 3. Calculate Security Score & Grade
        summary = self._calculate_summary(verified_findings, filtered_count)

        # 4. Generate AI Agent Executive Analysis
        executive_summary = await self._generate_executive_analysis(verified_findings, summary)

        return verified_findings, summary, executive_summary

    def _is_false_positive(self, finding: Finding) -> bool:
        lower_path = finding.file_path.lower()

        # Suppress test files from triggering critical auth or secret alarms if they're standard mock files
        if "test" in lower_path or "mock" in lower_path or "fixture" in lower_path:
            if "dummy" in finding.snippet.lower() or "mock" in finding.snippet.lower():
                return True

        # SQL injection false positives (no format specifier or concatenation actually present)
        if "SQL Injection" in finding.title:
            if "SELECT " in finding.snippet and not any(ch in finding.snippet for ch in ["%", "+", "f\"", "f'", "$", "{"]):
                return True

        return False

    def _calculate_summary(self, findings: List[Finding], false_positives_filtered: int) -> ScanSummary:
        by_sev = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        by_cat = {
            FindingCategory.SECURITY.value: 0,
            FindingCategory.SLOP.value: 0,
            FindingCategory.GAPS.value: 0,
            FindingCategory.LOOSE_ENDS.value: 0,
            FindingCategory.DEPENDENCIES.value: 0,
        }

        score = 100
        for f in findings:
            sev_str = f.severity.value
            by_sev[sev_str] = by_sev.get(sev_str, 0) + 1
            by_cat[f.category.value] = by_cat.get(f.category.value, 0) + 1

            # Score deduction
            if f.severity == Severity.CRITICAL:
                score -= 25
            elif f.severity == Severity.HIGH:
                score -= 12
            elif f.severity == Severity.MEDIUM:
                score -= 5
            elif f.severity == Severity.LOW:
                score -= 2

        score = max(0, min(100, score))

        if score >= 95:
            grade = "A+"
        elif score >= 85:
            grade = "A"
        elif score >= 75:
            grade = "B"
        elif score >= 65:
            grade = "C"
        elif score >= 50:
            grade = "D"
        else:
            grade = "F"

        return ScanSummary(
            total_findings=len(findings),
            security_score=score,
            grade=grade,
            by_severity=by_sev,
            by_category=by_cat,
            false_positives_filtered=false_positives_filtered
        )

    async def _generate_executive_analysis(self, findings: List[Finding], summary: ScanSummary) -> str:
        prompt = (
            f"Repository: {self.metadata.repo_name}\n"
            f"Languages: {', '.join(l.language for l in self.metadata.languages)}\n"
            f"Total Files: {self.metadata.total_files}, Lines of Code: {self.metadata.total_lines}\n"
            f"Security Score: {summary.security_score}/100 (Grade: {summary.grade})\n"
            f"Findings: Critical={summary.by_severity['critical']}, High={summary.by_severity['high']}, "
            f"Medium={summary.by_severity['medium']}, Low={summary.by_severity['low']}\n"
            f"Top Issues: {[f.title for f in findings[:5]]}\n\n"
            "Provide a concise executive security and code quality review summarizing core risks, architecture debt, and immediate remediation steps."
        )

        sys_prompt = "You are CodeSentinel AI, an elite cybersecurity and software architecture auditing agent."
        return await self.llm.generate_reasoning(sys_prompt, prompt)
