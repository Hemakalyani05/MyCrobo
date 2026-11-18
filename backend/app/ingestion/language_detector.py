import os
from pathlib import Path
from typing import Dict, List, Tuple
from ..models.schemas import RepoMetadata, LanguageBreakdown

IGNORE_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "venv", ".venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", "dist", "build",
    ".next", ".nuxt", "coverage", ".idea", ".vscode", "vendor",
    "target", "bin", "obj"
}

EXTENSION_MAP = {
    ".py": "Python",
    ".pyw": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".go": "Go",
    ".java": "Java",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++ Header",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".cs": "C#",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "SASS",
    ".sql": "SQL",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
    ".md": "Markdown",
}

MANIFEST_FILES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "requirements.txt", "Pipfile", "Pipfile.lock", "pyproject.toml", "setup.py",
    "go.mod", "go.sum",
    "pom.xml", "build.gradle", "build.gradle.kts",
    "Cargo.toml", "Cargo.lock",
    "Gemfile", "Gemfile.lock",
    "composer.json", "composer.lock",
    "Dockerfile", "docker-compose.yml"
}

FRAMEWORK_SIGNATURES = {
    "FastAPI": [("fastapi", ["requirements.txt", "pyproject.toml", "Pipfile"]), ("from fastapi import", [".py"])],
    "Flask": [("flask", ["requirements.txt", "pyproject.toml", "Pipfile"]), ("from flask import", [".py"])],
    "Django": [("django", ["requirements.txt", "pyproject.toml", "Pipfile"]), ("DJANGO_SETTINGS_MODULE", [".py", "manage.py"])],
    "React": [('"react":', ["package.json"]), ("from 'react'", [".js", ".jsx", ".ts", ".tsx"])],
    "Next.js": [('"next":', ["package.json"]), ("next/router", [".js", ".jsx", ".ts", ".tsx"])],
    "Express": [('"express":', ["package.json"]), ("require('express')", [".js", ".ts"])],
    "NestJS": [('"@nestjs/core"', ["package.json"])],
    "Tailwind CSS": [('"tailwindcss":', ["package.json"]), ("tailwind.config.js", ["package.json"])],
    "Gin (Go)": [("github.com/gin-gonic/gin", ["go.mod", ".go"])],
    "Spring Boot": [("spring-boot", ["pom.xml", "build.gradle"])],
    "Actix Web (Rust)": [("actix-web", ["Cargo.toml"])],
    "Docker": [("FROM ", ["Dockerfile"])],
}

def analyze_repository(repo_path: str) -> RepoMetadata:
    path = Path(repo_path).resolve()
    repo_name = path.name

    lang_stats: Dict[str, Dict[str, int]] = {}
    found_manifests: List[str] = []
    total_files = 0
    total_lines = 0

    if not path.exists():
        return RepoMetadata(
            repo_name=repo_name,
            repo_path=str(path),
            total_files=0,
            total_lines=0,
            languages=[],
            frameworks=[],
            manifests=[]
        )

    # Walk directory
    for root, dirs, files in os.walk(path):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

        for file in files:
            if file.startswith(".") and file not in {".env.example"}:
                continue
            
            file_path = Path(root) / file
            rel_path = file_path.relative_to(path)

            if file in MANIFEST_FILES or file.startswith("Dockerfile"):
                found_manifests.append(str(rel_path))

            ext = file_path.suffix.lower()
            if ext in EXTENSION_MAP:
                lang = EXTENSION_MAP[ext]
                line_count = 0
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        line_count = sum(1 for _ in f)
                except Exception:
                    line_count = 0

                if lang not in lang_stats:
                    lang_stats[lang] = {"files": 0, "lines": 0}
                lang_stats[lang]["files"] += 1
                lang_stats[lang]["lines"] += line_count

                total_files += 1
                total_lines += line_count

    # Calculate percentages
    breakdown: List[LanguageBreakdown] = []
    if total_lines > 0:
        for lang, stats in sorted(lang_stats.items(), key=lambda x: x[1]["lines"], reverse=True):
            pct = round((stats["lines"] / total_lines) * 100, 1)
            breakdown.append(LanguageBreakdown(
                language=lang,
                files_count=stats["files"],
                lines_count=stats["lines"],
                percentage=pct
            ))

    # Detect Frameworks
    detected_frameworks = set()
    manifest_contents: Dict[str, str] = {}
    for m in found_manifests:
        m_path = path / m
        if m_path.is_file():
            try:
                manifest_contents[m] = m_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass

    for fw, signatures in FRAMEWORK_SIGNATURES.items():
        matched = False
        for token, target_files in signatures:
            for tf in target_files:
                for m_name, m_text in manifest_contents.items():
                    if m_name.endswith(tf) and token in m_text:
                        detected_frameworks.add(fw)
                        matched = True
                        break
                if matched:
                    break
            if matched:
                break

    return RepoMetadata(
        repo_name=repo_name,
        repo_path=str(path),
        total_files=total_files,
        total_lines=total_lines,
        languages=breakdown,
        frameworks=sorted(list(detected_frameworks)),
        manifests=sorted(list(set(found_manifests)))
    )
