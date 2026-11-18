import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any

class Dependency:
    def __init__(self, name: str, version: str, ecosystem: str, manifest_path: str, line_number: int = 1):
        self.name = name
        self.version = version
        self.ecosystem = ecosystem
        self.manifest_path = manifest_path
        self.line_number = line_number

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "ecosystem": self.ecosystem,
            "manifest_path": self.manifest_path,
            "line_number": self.line_number
        }

def parse_requirements_txt(content: str, manifest_path: str) -> List[Dependency]:
    deps = []
    lines = content.splitlines()
    for idx, line in enumerate(lines, 1):
        clean = line.strip()
        if not clean or clean.startswith("#") or clean.startswith("-"):
            continue
        # Match name and version specifiers: requests==2.25.1 or flask>=2.0.0
        match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*([=><~^!]+)\s*([a-zA-Z0-9_\-\.]+)", clean)
        if match:
            deps.append(Dependency(
                name=match.group(1).lower(),
                version=match.group(3),
                ecosystem="PyPI",
                manifest_path=manifest_path,
                line_number=idx
            ))
        else:
            # Name only
            name_match = re.match(r"^([a-zA-Z0-9_\-\.]+)", clean)
            if name_match:
                deps.append(Dependency(
                    name=name_match.group(1).lower(),
                    version="latest",
                    ecosystem="PyPI",
                    manifest_path=manifest_path,
                    line_number=idx
                ))
    return deps

def parse_package_json(content: str, manifest_path: str) -> List[Dependency]:
    deps = []
    try:
        data = json.loads(content)
        lines = content.splitlines()
        
        all_deps = {}
        if "dependencies" in data and isinstance(data["dependencies"], dict):
            all_deps.update(data["dependencies"])
        if "devDependencies" in data and isinstance(data["devDependencies"], dict):
            all_deps.update(data["devDependencies"])

        for pkg, ver in all_deps.items():
            clean_ver = re.sub(r"[^0-9\.]", "", str(ver))
            # Find line number roughly
            line_no = 1
            pkg_pattern = f'"{pkg}"'
            for idx, line in enumerate(lines, 1):
                if pkg_pattern in line:
                    line_no = idx
                    break
            deps.append(Dependency(
                name=pkg,
                version=clean_ver or str(ver),
                ecosystem="npm",
                manifest_path=manifest_path,
                line_number=line_no
            ))
    except Exception:
        pass
    return deps

def parse_go_mod(content: str, manifest_path: str) -> List[Dependency]:
    deps = []
    lines = content.splitlines()
    in_require_block = False

    for idx, line in enumerate(lines, 1):
        clean = line.strip()
        if clean.startswith("require ("):
            in_require_block = True
            continue
        elif in_require_block and clean == ")":
            in_require_block = False
            continue

        if in_require_block:
            parts = clean.split()
            if len(parts) >= 2 and not clean.startswith("//"):
                deps.append(Dependency(
                    name=parts[0],
                    version=parts[1].lstrip("v"),
                    ecosystem="Go",
                    manifest_path=manifest_path,
                    line_number=idx
                ))
        elif clean.startswith("require "):
            parts = clean.replace("require ", "").split()
            if len(parts) >= 2:
                deps.append(Dependency(
                    name=parts[0],
                    version=parts[1].lstrip("v"),
                    ecosystem="Go",
                    manifest_path=manifest_path,
                    line_number=idx
                ))
    return deps

def parse_pom_xml(content: str, manifest_path: str) -> List[Dependency]:
    deps = []
    try:
        # Strip namespaces for simpler parsing
        xml_clean = re.sub(r'xmlns(:\w+)?="[^"]+"', '', content)
        root = ET.fromstring(xml_clean)
        for dep in root.findall(".//dependency"):
            group = dep.find("groupId")
            art = dep.find("artifactId")
            ver = dep.find("version")
            if art is not None:
                art_name = art.text.strip() if art.text else ""
                group_name = group.text.strip() if group is not None and group.text else ""
                full_name = f"{group_name}:{art_name}" if group_name else art_name
                version_str = ver.text.strip() if ver is not None and ver.text else "unknown"
                deps.append(Dependency(
                    name=full_name,
                    version=version_str,
                    ecosystem="Maven",
                    manifest_path=manifest_path,
                    line_number=1
                ))
    except Exception:
        pass
    return deps

def parse_cargo_toml(content: str, manifest_path: str) -> List[Dependency]:
    deps = []
    lines = content.splitlines()
    in_deps = False
    for idx, line in enumerate(lines, 1):
        clean = line.strip()
        if clean.startswith("[dependencies]") or clean.startswith("[dev-dependencies]"):
            in_deps = True
            continue
        elif clean.startswith("[") and in_deps:
            in_deps = False
            continue

        if in_deps and "=" in clean and not clean.startswith("#"):
            parts = clean.split("=", 1)
            pkg = parts[0].strip()
            ver_raw = parts[1].strip().strip('"').strip("'")
            ver_clean = re.sub(r"[^0-9\.]", "", ver_raw)
            deps.append(Dependency(
                name=pkg,
                version=ver_clean or ver_raw,
                ecosystem="Cargo",
                manifest_path=manifest_path,
                line_number=idx
            ))
    return deps

def extract_all_dependencies(repo_path: str, manifests: List[str]) -> List[Dependency]:
    base = Path(repo_path)
    all_deps = []

    for rel_path in manifests:
        p = base / rel_path
        if not p.is_file():
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            filename = p.name.lower()
            if filename == "requirements.txt" or filename.endswith(".txt"):
                all_deps.extend(parse_requirements_txt(content, rel_path))
            elif filename == "package.json":
                all_deps.extend(parse_package_json(content, rel_path))
            elif filename == "go.mod":
                all_deps.extend(parse_go_mod(content, rel_path))
            elif filename == "pom.xml":
                all_deps.extend(parse_pom_xml(content, rel_path))
            elif filename == "cargo.toml":
                all_deps.extend(parse_cargo_toml(content, rel_path))
        except Exception:
            continue

    return all_deps
