import os
import shutil
import subprocess
import hashlib
from pathlib import Path
from typing import Tuple, Optional
from ..core.config import DATA_DIR, SAMPLE_REPOS_DIR

REPOS_CACHE_DIR = DATA_DIR / "cloned_repos"
SNIPPETS_CACHE_DIR = DATA_DIR / "snippets"

REPOS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
SNIPPETS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

class RepoLoader:
    @staticmethod
    def load(source_type: str, target: str, language: Optional[str] = None) -> Tuple[str, str]:
        """
        Loads the repository based on source_type.
        Returns: (repo_name, resolved_path)
        """
        if source_type == "sample":
            target_clean = target.strip("/\\")
            sample_path = SAMPLE_REPOS_DIR / target_clean
            if not sample_path.exists():
                # Try finding in sample_repos directory
                found = list(SAMPLE_REPOS_DIR.glob(f"*{target_clean}*"))
                if found:
                    sample_path = found[0]
                else:
                    raise ValueError(f"Sample repository '{target}' not found in {SAMPLE_REPOS_DIR}")
            return sample_path.name, str(sample_path.resolve())

        elif source_type == "local":
            local_path = Path(target).resolve()
            if not local_path.exists() or not local_path.is_dir():
                raise ValueError(f"Local directory '{target}' does not exist or is not a directory")
            return local_path.name, str(local_path)

        elif source_type == "github":
            url = target.strip()
            if not (url.startswith("http://") or url.startswith("https://") or url.startswith("git@")):
                raise ValueError(f"Invalid Git URL: '{target}'")
            
            repo_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
            clone_dest = REPOS_CACHE_DIR / f"{repo_name}_{repo_hash}"

            if not clone_dest.exists():
                cmd = ["git", "clone", "--depth", "1", url, str(clone_dest)]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if result.returncode != 0:
                    raise RuntimeError(f"Git clone failed: {result.stderr.strip()}")
            return repo_name, str(clone_dest.resolve())

        elif source_type == "snippet":
            # Direct code snippet passed in target
            ext_map = {
                "python": "snippet.py",
                "javascript": "snippet.js",
                "typescript": "snippet.ts",
                "go": "snippet.go",
                "java": "Snippet.java",
                "c": "snippet.c",
                "cpp": "snippet.cpp",
                "rust": "snippet.rs",
                "php": "snippet.php",
                "ruby": "snippet.rb",
                "sql": "snippet.sql",
                "shell": "snippet.sh",
            }
            lang_key = (language or "python").lower()
            filename = ext_map.get(lang_key, "snippet.txt")

            snip_hash = hashlib.md5(target.encode()).hexdigest()[:10]
            snippet_dir = SNIPPETS_CACHE_DIR / f"snippet_{snip_hash}"
            snippet_dir.mkdir(parents=True, exist_ok=True)
            snippet_file = snippet_dir / filename
            snippet_file.write_text(target, encoding="utf-8")

            return f"Snippet ({filename})", str(snippet_dir.resolve())

        else:
            raise ValueError(f"Unknown source_type '{source_type}'")
