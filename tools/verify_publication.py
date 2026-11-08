"""Verify the bounded GitHub/research-preview publication layer."""
from __future__ import annotations

import hashlib
import argparse
import json
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/pull_request_template.md",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "NOTICE",
    "README.md",
    "SECURITY.md",
    "docs/ABI.md",
    "docs/AGENT-CLI.md",
    "docs/CONCEPTS.md",
    "docs/CONTRIBUTOR-TESTING.md",
    "docs/PUBLICATION.md",
    "src/cmba_agent/cli.py",
    "src/cmba_agent/data/protocol-manifest.json",
)
SCHEMA_COPIES = {
    "schemas/request.schema.json": "src/cmba_agent/data/request-core.json",
    "schemas/j1/request.schema.json": "src/cmba_agent/data/request-app.json",
    "schemas/k1/request.schema.json": "src/cmba_agent/data/request-workbench.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root: Path = ROOT) -> dict:
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    if missing:
        raise ValueError("PUBLICATION_REQUIRED_FILE:" + ",".join(missing))

    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    boundary = json.loads((root / "RELEASE-BOUNDARY.json").read_text(encoding="utf-8"))
    if project["version"] != "0.1.0a7" or boundary["version"] != project["version"]:
        raise ValueError("PUBLICATION_VERSION")
    if project["scripts"].get("cmba-agent") != "cmba_agent.cli:main":
        raise ValueError("PUBLICATION_AGENT_ENTRYPOINT")
    if boundary["public_release_gate"] != "CLEARED_FOR_LABELED_RESEARCH_PREVIEW":
        raise ValueError("PUBLICATION_GATE")
    if boundary["independent_review"] != "NOT_PERFORMED" or boundary["authority_effect"] != "NONE":
        raise ValueError("PUBLICATION_CLAIM_BOUNDARY")

    for source, installed in SCHEMA_COPIES.items():
        if (root / source).read_bytes() != (root / installed).read_bytes():
            raise ValueError("PUBLICATION_SCHEMA_DRIFT:" + source)

    readme = (root / "README.md").read_text(encoding="utf-8")
    for link in re.findall(r"\[[^]]+\]\(([^)]+)\)", readme):
        if "://" not in link and not link.startswith("#") and not (root / link).exists():
            raise ValueError("PUBLICATION_BROKEN_README_LINK:" + link)
    if "OWNER/" in readme or "github.com/OWNER" in readme:
        raise ValueError("PUBLICATION_PLACEHOLDER")

    manifest = json.loads((root / "src/cmba_agent/data/protocol-manifest.json").read_text(encoding="utf-8"))
    if set(manifest["interfaces"]) != {"core", "app", "workbench"}:
        raise ValueError("PUBLICATION_INTERFACE_SET")
    if any(value["effect_class"] != "PURE_READ" for value in manifest["interfaces"].values()):
        raise ValueError("PUBLICATION_AGENT_EFFECT")
    if manifest["effect_interfaces_excluded"] != ["cmba-export"]:
        raise ValueError("PUBLICATION_EFFECT_EXCLUSION")

    return {
        "schema": "cmba.publication-verification.r001",
        "status": "PASS",
        "version": project["version"],
        "required_files": len(REQUIRED),
        "schema_copies": len(SCHEMA_COPIES),
        "agent_interfaces": sorted(manifest["interfaces"]),
        "readme_sha256": digest(root / "README.md"),
        "public_release_gate": boundary["public_release_gate"],
        "independent_review": boundary["independent_review"],
        "publication": boundary["publication"],
        "authority_effect": "NONE",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        result = verify()
        if args.out:
            if args.out.exists():
                raise ValueError("PUBLICATION_OUTPUT_EXISTS")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True))
    except (OSError, ValueError, KeyError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(json.dumps({
            "schema": "cmba.publication-verification.r001",
            "status": "REFUSED",
            "reason": str(exc),
            "authority_effect": "NONE",
        }, sort_keys=True))
        raise SystemExit(2)
