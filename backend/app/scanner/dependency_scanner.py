import re
import uuid
from typing import List, Dict, Any, Optional
from ..ingestion.dependency_parser import Dependency
from ..models.schemas import Finding, FindingCategory, Severity

KNOWN_VULNERABILITIES = [
    # Python (PyPI)
    {
        "name": "requests",
        "ecosystem": "PyPI",
        "vulnerable_below": "2.31.0",
        "fixed_version": "2.31.0",
        "cve_id": "CVE-2023-32681",
        "severity": Severity.MEDIUM,
        "title": "Vulnerable Dependency: requests (Header Leak)",
        "explanation": "requests before 2.31.0 unintentionally sends Proxy-Authorization headers to destination servers when following HTTPS redirects.",
        "remediation": "Upgrade `requests` to version 2.31.0 or newer."
    },
    {
        "name": "urllib3",
        "ecosystem": "PyPI",
        "vulnerable_below": "2.0.7",
        "fixed_version": "2.0.7",
        "cve_id": "CVE-2023-45803",
        "severity": Severity.HIGH,
        "title": "Vulnerable Dependency: urllib3 (Request Body Leak)",
        "explanation": "urllib3 before 2.0.7 does not strip request bodies on 303 See Other redirects, potentially exposing sensitive POST payloads.",
        "remediation": "Upgrade `urllib3` to version 2.0.7 or newer."
    },
    {
        "name": "flask",
        "ecosystem": "PyPI",
        "vulnerable_below": "2.2.5",
        "fixed_version": "2.2.5",
        "cve_id": "CVE-2023-30861",
        "severity": Severity.HIGH,
        "title": "Vulnerable Dependency: Flask (Session Cookie Leak)",
        "explanation": "Flask before 2.2.5 does not properly set the Vary: Cookie header on cached responses, risking session cookie exposure.",
        "remediation": "Upgrade `Flask` to version 2.2.5 or >= 3.0.0."
    },
    {
        "name": "django",
        "ecosystem": "PyPI",
        "vulnerable_below": "4.2.11",
        "fixed_version": "4.2.11",
        "cve_id": "CVE-2024-27351",
        "severity": Severity.HIGH,
        "title": "Vulnerable Dependency: Django (ReDoS in Email Validator)",
        "explanation": "Django before 4.2.11 contains a Regular Expression Denial of Service vulnerability in email validation routines.",
        "remediation": "Upgrade `django` to >= 4.2.11 or >= 5.0.3."
    },
    # JavaScript (npm)
    {
        "name": "lodash",
        "ecosystem": "npm",
        "vulnerable_below": "4.17.21",
        "fixed_version": "4.17.21",
        "cve_id": "CVE-2020-8203",
        "severity": Severity.CRITICAL,
        "title": "Vulnerable Dependency: lodash (Prototype Pollution)",
        "explanation": "lodash versions prior to 4.17.21 are vulnerable to Prototype Pollution via `zipObjectDeep`, leading to property injection or RCE.",
        "remediation": "Upgrade `lodash` to version 4.17.21 or newer."
    },
    {
        "name": "express",
        "ecosystem": "npm",
        "vulnerable_below": "4.19.2",
        "fixed_version": "4.19.2",
        "cve_id": "CVE-2024-29041",
        "severity": Severity.MEDIUM,
        "title": "Vulnerable Dependency: Express.js (Open Redirect)",
        "explanation": "Express versions prior to 4.19.2 contain an open redirect vulnerability in `res.location()` handling.",
        "remediation": "Upgrade `express` to version 4.19.2 or newer."
    },
    {
        "name": "jsonwebtoken",
        "ecosystem": "npm",
        "vulnerable_below": "9.0.0",
        "fixed_version": "9.0.0",
        "cve_id": "CVE-2022-23529",
        "severity": Severity.CRITICAL,
        "title": "Vulnerable Dependency: jsonwebtoken (Remote Code Execution)",
        "explanation": "jsonwebtoken prior to 9.0.0 is vulnerable to arbitrary code execution if an untrusted `secretOrPublicKey` parameter is passed.",
        "remediation": "Upgrade `jsonwebtoken` to version 9.0.0 or newer."
    },
    {
        "name": "axios",
        "ecosystem": "npm",
        "vulnerable_below": "1.6.0",
        "fixed_version": "1.6.0",
        "cve_id": "CVE-2023-45857",
        "severity": Severity.MEDIUM,
        "title": "Vulnerable Dependency: Axios (CSRF Data Leak)",
        "explanation": "Axios versions prior to 1.6.0 leak confidential auth tokens during cross-site redirects.",
        "remediation": "Upgrade `axios` to version 1.6.0 or newer."
    },
    # Java (Maven)
    {
        "name": "log4j-core",
        "ecosystem": "Maven",
        "vulnerable_below": "2.17.1",
        "fixed_version": "2.17.1",
        "cve_id": "CVE-2021-44228",
        "severity": Severity.CRITICAL,
        "title": "Vulnerable Dependency: Log4j (Log4Shell RCE)",
        "explanation": "Log4j JNDI lookup vulnerability allows unauthenticated remote code execution via log message strings.",
        "remediation": "Upgrade `log4j-core` immediately to 2.17.1 or higher."
    },
    # Go
    {
        "name": "github.com/gin-gonic/gin",
        "ecosystem": "Go",
        "vulnerable_below": "1.9.1",
        "fixed_version": "1.9.1",
        "cve_id": "CVE-2023-29401",
        "severity": Severity.HIGH,
        "title": "Vulnerable Dependency: Gin Web Framework (Bypass)",
        "explanation": "Gin web framework versions prior to 1.9.1 mishandle route wildcard matching, enabling path traversal or auth bypass.",
        "remediation": "Upgrade `gin-gonic/gin` to v1.9.1 or newer in `go.mod`."
    }
]

def parse_semver(v: str):
    nums = re.findall(r"\d+", v)
    if not nums:
        return (0, 0, 0)
    parts = [int(n) for n in nums[:3]]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)

def is_version_lower(current_ver: str, threshold_ver: str) -> bool:
    cur = parse_semver(current_ver)
    thresh = parse_semver(threshold_ver)
    return cur < thresh

def scan_dependencies(dependencies: List[Dependency]) -> List[Finding]:
    findings = []
    for dep in dependencies:
        dep_name_clean = dep.name.lower()
        for vuln in KNOWN_VULNERABILITIES:
            if vuln["ecosystem"] == dep.ecosystem and (vuln["name"].lower() == dep_name_clean or dep_name_clean.endswith(vuln["name"].lower())):
                if dep.version != "latest" and is_version_lower(dep.version, vuln["vulnerable_below"]):
                    snippet = f"{dep.manifest_path}:{dep.line_number}: {dep.name}=={dep.version}"
                    findings.append(Finding(
                        id=f"dep-{uuid.uuid4().hex[:8]}",
                        title=vuln["title"],
                        category=FindingCategory.DEPENDENCIES,
                        severity=vuln["severity"],
                        file_path=dep.manifest_path,
                        line_number=dep.line_number,
                        snippet=snippet,
                        explanation=vuln["explanation"],
                        evidence=f"Declared version `{dep.version}` is less than fixed safe threshold `{vuln['fixed_version']}` ({vuln['cve_id']}).",
                        remediation=vuln["remediation"],
                        cwe_id="CWE-1395",
                        rule_id=vuln["cve_id"],
                        confidence=1.0,
                        verified=True
                    ))
    return findings
