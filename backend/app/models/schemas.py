from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class FindingCategory(str, Enum):
    SECURITY = "security"
    SLOP = "slop"
    GAPS = "gaps"
    LOOSE_ENDS = "loose_ends"
    DEPENDENCIES = "dependencies"

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class Finding(BaseModel):
    id: str
    title: str
    category: FindingCategory
    severity: Severity
    file_path: str
    line_number: int
    end_line_number: Optional[int] = None
    snippet: str
    explanation: str
    evidence: str
    remediation: str
    diff_patch: Optional[str] = None
    confidence: float = 1.0
    verified: bool = True
    rule_id: Optional[str] = None
    cwe_id: Optional[str] = None

class LanguageBreakdown(BaseModel):
    language: str
    files_count: int
    lines_count: int
    percentage: float

class RepoMetadata(BaseModel):
    repo_name: str
    repo_path: str
    total_files: int
    total_lines: int
    languages: List[LanguageBreakdown] = []
    frameworks: List[str] = []
    manifests: List[str] = []

class ScanSummary(BaseModel):
    total_findings: int
    security_score: int
    grade: str
    by_severity: Dict[str, int]
    by_category: Dict[str, int]
    false_positives_filtered: int = 0

class AuditReport(BaseModel):
    scan_id: str
    created_at: str
    source_type: str
    target: str
    metadata: RepoMetadata
    summary: ScanSummary
    findings: List[Finding]
    agent_analysis: str
    duration_seconds: float

class ScanRequest(BaseModel):
    source_type: str = "sample"  # "sample", "local", "github", "snippet"
    target: str
    language: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ollama_url: Optional[str] = "http://localhost:11434"
    ai_model: Optional[str] = "heuristic"  # "heuristic", "gemini", "openai", "ollama"
    verify_with_ai: bool = True

class ApplyPatchRequest(BaseModel):
    file_path: str
    diff_patch: str
    scan_id: Optional[str] = None

class AgentEvent(BaseModel):
    type: str  # log, progress, finding, summary, complete, error
    stage: str
    progress_percent: int
    message: str
    data: Optional[Dict[str, Any]] = None
