import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..models.schemas import Finding, FindingCategory, Severity

SECURITY_RULES = [
    # 1. AWS Access Key
    {
        "id": "SEC-001",
        "title": "Hardcoded AWS Access Key ID",
        "category": FindingCategory.SECURITY,
        "severity": Severity.CRITICAL,
        "cwe_id": "CWE-798",
        "pattern": r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
        "explanation": "Hardcoded AWS credentials detected in source code. If committed, an attacker can extract these keys and compromise AWS cloud infrastructure.",
        "remediation": "Revoke the exposed key immediately in AWS IAM, rotate credentials, and load keys from environment variables or IAM roles.",
        "patch_hint": "Replace hardcoded key with os.getenv('AWS_ACCESS_KEY_ID') or environment configuration."
    },
    # 2. Generic API Keys & Tokens
    {
        "id": "SEC-002",
        "title": "Hardcoded API Secret / Private Token",
        "category": FindingCategory.SECURITY,
        "severity": Severity.HIGH,
        "cwe_id": "CWE-798",
        "pattern": r"""(?i)(?:api_key|apikey|secret_key|secret|token|auth_token|client_secret)\s*[:=]\s*["']([A-Za-z0-9_\-\.]{20,})["']""",
        "explanation": "High-entropy API key or secret token discovered in source code. Hardcoded credentials can be leaked via repositories or build artifacts.",
        "remediation": "Store sensitive keys in an encrypted secrets manager or environment variables (`.env`).",
        "patch_hint": "Use os.environ.get('API_SECRET') or process.env.API_SECRET instead of string literals."
    },
    # 3. RSA / SSH Private Key
    {
        "id": "SEC-003",
        "title": "Hardcoded Private Cryptographic Key",
        "category": FindingCategory.SECURITY,
        "severity": Severity.CRITICAL,
        "cwe_id": "CWE-312",
        "pattern": r"-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE\s+KEY-----",
        "explanation": "Plaintext private key discovered in source code. Compromise of this key allows impersonation, decryption of TLS traffic, or unauthorized SSH access.",
        "remediation": "Remove the private key from source control immediately, regenerate the keypair, and mount keys securely via secrets volumes.",
        "patch_hint": "Read key file from secure filesystem path specified in environment variables."
    },
    # 4. SQL Injection via string formatting
    {
        "id": "SEC-004",
        "title": "SQL Injection via String Concatenation or Interpolation",
        "category": FindingCategory.SECURITY,
        "severity": Severity.CRITICAL,
        "cwe_id": "CWE-89",
        "pattern": r"""(?i)(?:execute|query|raw|exec)\s*\(\s*(?:f["'][^"']*(?:SELECT|INSERT|UPDATE|DELETE)[^"']*\{[^}]+\}|["'][^"']*(?:SELECT|INSERT|UPDATE|DELETE)[^"']*["']\s*\+\s*[a-zA-Z0-9_\.]+|fmt\.Sprintf\(["'][^"']*(?:SELECT|INSERT|UPDATE|DELETE)[^"']*%s)""",
        "explanation": "Constructing dynamic SQL queries via string concatenation or interpolation allows attackers to alter query logic, bypass authentication, and exfiltrate database records.",
        "remediation": "Use parameterized queries or ORM query builders (e.g., `execute('SELECT * FROM users WHERE id = %s', (user_id,))`).",
        "patch_hint": "Parameterize the SQL query using bind parameters instead of string formatting."
    },
    # 5. OS Command Injection
    {
        "id": "SEC-005",
        "title": "Potential OS Command Injection",
        "category": FindingCategory.SECURITY,
        "severity": Severity.CRITICAL,
        "cwe_id": "CWE-78",
        "pattern": r"""(?i)(?:subprocess\.(?:Popen|call|run|check_output)\([^)]*shell\s*=\s*True|os\.system\([^)]+\)|child_process\.exec\([^)]+\)|exec\.Command\("sh",\s*"-c")""",
        "explanation": "Invoking shell commands with `shell=True` or `exec` without argument vector sanitization permits arbitrary operating system command execution (RCE).",
        "remediation": "Pass commands as an argument list with `shell=False` or use explicit child_process.execFile with strict whitelist validation.",
        "patch_hint": "Change to subprocess.run(['command', arg1, arg2], check=True) with shell=False."
    },
    # 6. Cross-Site Scripting (DOM/Reflected XSS)
    {
        "id": "SEC-006",
        "title": "Cross-Site Scripting (XSS) via Unsanitized Output",
        "category": FindingCategory.SECURITY,
        "severity": Severity.HIGH,
        "cwe_id": "CWE-79",
        "pattern": r"""(?i)(?:dangerouslySetInnerHTML\s*=\s*\{\s*\{\s*__html\s*:|\.innerHTML\s*=\s*[^;]+|res\.send\([^)]*(?:req\.query|req\.params|req\.body)|document\.write\()""",
        "explanation": "Rendering raw HTML or echoing unsanitized user inputs directly into client documents allows attackers to execute malicious scripts in users' browsers.",
        "remediation": "Sanitize untrusted content using DOMPurify or use standard text binding (`textContent`, React default escaping).",
        "patch_hint": "Sanitize untrusted input using DOMPurify.sanitize() or use text node rendering."
    },
    # 7. Insecure Deserialization
    {
        "id": "SEC-007",
        "title": "Insecure Deserialization",
        "category": FindingCategory.SECURITY,
        "severity": Severity.HIGH,
        "cwe_id": "CWE-502",
        "pattern": r"""(?i)(?:pickle\.loads?\(|yaml\.load\([^,)]+\)|unserialize\()""",
        "explanation": "Deserializing untrusted data with `pickle` or unconstrained `yaml.load` can lead to arbitrary remote code execution during object reconstitution.",
        "remediation": "Use safe serializers like JSON or specify `yaml.safe_load(data)`.",
        "patch_hint": "Replace with json.loads(data) or yaml.safe_load(data)."
    },
    # 8. Weak Hashing Algorithm for Sensitive Data
    {
        "id": "SEC-008",
        "title": "Weak Hashing Algorithm (MD5 / SHA1)",
        "category": FindingCategory.SECURITY,
        "severity": Severity.MEDIUM,
        "cwe_id": "CWE-327",
        "pattern": r"""(?i)(?:hashlib\.md5\(|hashlib\.sha1\(|crypto\.createHash\(["'](?:md5|sha1)["']\))""",
        "explanation": "MD5 and SHA-1 have known collision and preimage vulnerabilities. They are unsafe for passwords, digital signatures, or integrity checks.",
        "remediation": "Use robust cryptographic hashes like SHA-256 for integrity or bcrypt/Argon2id for passwords.",
        "patch_hint": "Switch to hashlib.sha256() or bcrypt.hashpw()."
    },
    # 9. Disabled SSL/TLS Verification
    {
        "id": "SEC-009",
        "title": "Disabled SSL/TLS Certificate Verification",
        "category": FindingCategory.SECURITY,
        "severity": Severity.HIGH,
        "cwe_id": "CWE-295",
        "pattern": r"""(?i)(?:verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['"]?0['"]?|rejectUnauthorized:\s*false)""",
        "explanation": "Disabling TLS certificate verification renders HTTPS connections vulnerable to Man-in-the-Middle (MITM) eavesdropping and tampering.",
        "remediation": "Enable TLS validation by removing `verify=False` and provisioning valid certificates.",
        "patch_hint": "Set verify=True and install the valid CA bundle."
    },
    # 10. Overly Permissive CORS Configuration
    {
        "id": "SEC-010",
        "title": "Overly Permissive CORS Policy with Credentials",
        "category": FindingCategory.SECURITY,
        "severity": Severity.MEDIUM,
        "cwe_id": "CWE-942",
        "pattern": r"""(?i)(?:allow_origins=\["\*"\][\s\S]{0,100}allow_credentials=True|allow_origins\s*=\s*\[\s*["']\*["']\s*\]|Access-Control-Allow-Origin['"]?\s*:\s*['"]\*['"])""",
        "explanation": "Allowing all origins (`*`) with credentials enables any malicious site to perform authenticated cross-origin requests on behalf of victims.",
        "remediation": "Specify explicit trusted domains in `allow_origins` rather than wildcards.",
        "patch_hint": "Replace '*' with explicit trusted origins: allow_origins=['https://app.yourdomain.com']."
    },
    # 11. Hardcoded Weak JWT Secret
    {
        "id": "SEC-011",
        "title": "Hardcoded or Trivial JWT Secret",
        "category": FindingCategory.SECURITY,
        "severity": Severity.HIGH,
        "cwe_id": "CWE-798",
        "pattern": r"""(?i)(?:jwt\.(?:encode|decode|sign|verify)\([^)]*["'](?:secret|test|jwtsecret|123456|password)["'])""",
        "explanation": "Signing JWT tokens with a weak or hardcoded secret allows attackers to forge authorization tokens with arbitrary claims.",
        "remediation": "Use a cryptographically secure random secret loaded from environment variables (e.g. at least 256 bits).",
        "patch_hint": "Load secret from os.environ['JWT_SECRET_KEY']."
    },
    # 12. Path Traversal
    {
        "id": "SEC-012",
        "title": "Unsanitized Path Traversal",
        "category": FindingCategory.SECURITY,
        "severity": Severity.HIGH,
        "cwe_id": "CWE-22",
        "pattern": r"""(?i)(?:open\s*\(\s*f["'][^"']*\{[^}]*(?:file|path|name)[^}]*\}|fs\.readFile(?:Sync)?\s*\([^,)]*(?:req\.query|req\.params))""",
        "explanation": "Concatenating user input into file system operations without path canonicalization allows traversal using `../` to access unauthorized files.",
        "remediation": "Resolve absolute paths and ensure they remain inside an intended safe directory base.",
        "patch_hint": "Validate path using os.path.abspath and check startswith(ALLOWED_BASE_DIR)."
    }
]

def scan_file_security(file_path: Path, rel_path: str, content: str) -> List[Finding]:
    findings = []
    lines = content.splitlines()

    for rule in SECURITY_RULES:
        regex = re.compile(rule["pattern"])
        for idx, line in enumerate(lines, 1):
            if regex.search(line):
                # Avoid flagging test fixtures or comments if obvious
                clean_line = line.strip()
                if clean_line.startswith("//") or clean_line.startswith("#"):
                    # Check if line is just a comment mentioning the keyword
                    if not any(token in clean_line.lower() for token in ["dummy_secret_", "sk_live_", "akia", "-----begin"]):
                        continue

                # Extract context snippet (up to 3 lines)
                start_l = max(0, idx - 2)
                end_l = min(len(lines), idx + 2)
                snippet_lines = [f"{i+1}: {lines[i]}" for i in range(start_l, end_l)]
                snippet = "\n".join(snippet_lines)

                finding_id = f"sec-{uuid.uuid4().hex[:8]}"
                findings.append(Finding(
                    id=finding_id,
                    title=rule["title"],
                    category=rule["category"],
                    severity=rule["severity"],
                    file_path=rel_path,
                    line_number=idx,
                    snippet=snippet,
                    explanation=rule["explanation"],
                    evidence=f"Matched pattern at line {idx}: `{line.strip()}`",
                    remediation=rule["remediation"],
                    rule_id=rule["id"],
                    cwe_id=rule["cwe_id"],
                    confidence=0.95,
                    verified=True
                ))
    return findings
