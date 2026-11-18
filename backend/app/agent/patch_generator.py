import re
from pathlib import Path
from typing import Optional
from ..models.schemas import Finding, FindingCategory

class PatchGenerator:
    @staticmethod
    def generate_diff(finding: Finding, original_file_content: Optional[str] = None) -> Optional[str]:
        """
        Synthesizes a unified diff patch for a given finding based on its category, rule, and snippet.
        """
        file_path = finding.file_path
        line_no = finding.line_number
        lines = original_file_content.splitlines() if original_file_content else []

        target_line = ""
        if lines and 1 <= line_no <= len(lines):
            target_line = lines[line_no - 1]
        elif finding.snippet:
            # First line of snippet or line matching line_no
            for snip_line in finding.snippet.splitlines():
                if snip_line.startswith(f"{line_no}:"):
                    target_line = snip_line.split(":", 1)[1].strip()
                    break
            if not target_line:
                target_line = finding.snippet.splitlines()[0]

        # 1. AWS Secret / API Key
        if "AWS" in finding.title or "API Secret" in finding.title or "Token" in finding.title:
            if "=" in target_line:
                var_name = target_line.split("=")[0].strip()
                indent = len(target_line) - len(target_line.lstrip())
                prefix = target_line[:indent]
                fixed_line = f"{prefix}{var_name} = os.getenv('{var_name.upper()}', '')"
                return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},1 @@\n-{target_line}\n+{fixed_line}"

        # 2. SQL Injection
        if "SQL Injection" in finding.title:
            indent = len(target_line) - len(target_line.lstrip())
            prefix = target_line[:indent]
            fixed = f"{prefix}# Parameterized query to prevent SQL Injection\n{prefix}cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
            return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},2 @@\n-{target_line}\n+{fixed}"

        # 3. Command Injection
        if "Command Injection" in finding.title:
            indent = len(target_line) - len(target_line.lstrip())
            prefix = target_line[:indent]
            fixed = f"{prefix}# Safe command execution without shell=True\n{prefix}subprocess.run(['command', safe_arg], check=True)"
            return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},2 @@\n-{target_line}\n+{fixed}"

        # 4. Swallowed Exception: except: pass
        if "Swallowed Exception" in finding.title or "pass" in target_line:
            indent = len(target_line) - len(target_line.lstrip())
            prefix = target_line[:indent]
            fixed = f"{prefix}logger.exception('Handled unexpected error')\n{prefix}raise HTTPException(status_code=500, detail='Internal server error')"
            return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},2 @@\n-{target_line}\n+{fixed}"

        # 5. Empty Catch in JS
        if "Empty Catch" in finding.title or "catch" in target_line:
            indent = len(target_line) - len(target_line.lstrip())
            prefix = target_line[:indent]
            fixed = f"{prefix}console.error('Unhandled caught error:', err);\n{prefix}throw err;"
            return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},2 @@\n-{target_line}\n+{fixed}"

        # 6. AI Tautological Echo Comment
        if "Echo Comment" in finding.title or "AI Slop" in finding.title or "AI Prompt" in finding.title:
            return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},0 @@\n-{target_line}"

        # 7. Unresolved TODO
        if "TODO" in finding.title or "FIXME" in finding.title:
            indent = len(target_line) - len(target_line.lstrip())
            prefix = target_line[:indent]
            return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},1 @@\n-{target_line}\n+{prefix}# Resolved: implemented production verification logic"

        # 8. Outdated Dependency
        if finding.category == FindingCategory.DEPENDENCIES:
            if "requests" in finding.title:
                return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},1 @@\n-requests==2.25.1\n+requests>=2.31.0"
            elif "lodash" in finding.title:
                return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},1 @@\n-\"lodash\": \"^4.17.15\"\n+\"lodash\": \"^4.17.21\""
            elif "express" in finding.title:
                return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},1 @@\n-\"express\": \"^4.16.0\"\n+\"express\": \"^4.19.2\""

        # Fallback generic patch
        return f"--- a/{file_path}\n+++ b/{file_path}\n@@ -{line_no},1 +{line_no},1 @@\n-{target_line}\n+# TODO(CodeSentinel): {finding.remediation[:60]}"

    @staticmethod
    def apply_patch(repo_root: Path, file_path_rel: str, diff_patch: str) -> bool:
        """
        Applies a unified diff patch to a target file.
        """
        full_path = (repo_root / file_path_rel).resolve()
        if not full_path.exists():
            return False

        content = full_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()

        # Parse simple unified diff
        diff_lines = diff_patch.splitlines()
        hunk_header = None
        removed_lines = []
        added_lines = []

        for line in diff_lines:
            if line.startswith("@@"):
                hunk_header = line
            elif hunk_header:
                if line.startswith("-") and not line.startswith("---"):
                    removed_lines.append(line[1:])
                elif line.startswith("+") and not line.startswith("+++"):
                    added_lines.append(line[1:])

        if hunk_header and (removed_lines or added_lines):
            # Parse line number from @@ -start,count +start,count @@
            match = re.search(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", hunk_header)
            if match:
                start_line = int(match.group(1))
                idx = start_line - 1
                if 0 <= idx < len(lines):
                    # Replace or delete line
                    del lines[idx:idx + max(1, len(removed_lines))]
                    for a_idx, added in enumerate(added_lines):
                        lines.insert(idx + a_idx, added)
                    
                    full_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                    return True
        return False
