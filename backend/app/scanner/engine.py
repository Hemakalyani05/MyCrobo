import os
from pathlib import Path
from typing import List, Callable, Optional, Dict, Any
from ..models.schemas import Finding, RepoMetadata
from ..ingestion.language_detector import IGNORE_DIRS, EXTENSION_MAP
from ..ingestion.dependency_parser import extract_all_dependencies
from .security_scanner import scan_file_security
from .slop_scanner import scan_file_slop
from .gaps_scanner import scan_file_gaps
from .loose_ends_scanner import scan_file_loose_ends
from .dependency_scanner import scan_dependencies

MAX_FILE_SIZE_BYTES = 1024 * 1024  # 1MB limit for static scan

class ScanEngine:
    def __init__(self, repo_path: str, metadata: RepoMetadata):
        self.repo_path = Path(repo_path)
        self.metadata = metadata

    def run(self, progress_callback: Optional[Callable[[str, int, str], None]] = None) -> List[Finding]:
        all_findings: List[Finding] = []

        # 1. Dependency Analysis
        if progress_callback:
            progress_callback("Analyzing Dependencies & Manifests", 15, "Parsing package manifests for known CVEs...")
        
        deps = extract_all_dependencies(str(self.repo_path), self.metadata.manifests)
        dep_findings = scan_dependencies(deps)
        all_findings.extend(dep_findings)

        # 2. Collect audit-eligible source files
        source_files = []
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
            for file in files:
                if file.startswith(".") and file not in {".env", ".env.local"}:
                    continue
                file_p = Path(root) / file
                ext = file_p.suffix.lower()
                if ext in EXTENSION_MAP or file in {".env", "Dockerfile"}:
                    source_files.append(file_p)

        total_files = len(source_files)
        if total_files == 0:
            if progress_callback:
                progress_callback("Scan Complete", 100, "No audit-eligible source files found.")
            return all_findings

        # 3. Scan Files
        for index, file_p in enumerate(source_files):
            pct = 20 + int((index / total_files) * 55)
            rel_p = str(file_p.relative_to(self.repo_path))
            
            if progress_callback and (index % max(1, total_files // 10) == 0 or index == total_files - 1):
                progress_callback("Scanning Source Files", pct, f"Inspecting AST and patterns: {rel_p}")

            try:
                if file_p.stat().st_size > MAX_FILE_SIZE_BYTES:
                    continue
                content = file_p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # Run Security Rules
            sec_finds = scan_file_security(file_p, rel_p, content)
            all_findings.extend(sec_finds)

            # Run Slop Detection
            slop_finds = scan_file_slop(file_p, rel_p, content)
            all_findings.extend(slop_finds)

            # Run Coding Gaps
            gaps_finds = scan_file_gaps(file_p, rel_p, content)
            all_findings.extend(gaps_finds)

            # Run Loose Ends
            loose_finds = scan_file_loose_ends(file_p, rel_p, content)
            all_findings.extend(loose_finds)

        if progress_callback:
            progress_callback("Deterministic Analysis Complete", 75, f"Identified {len(all_findings)} initial findings.")

        return all_findings
