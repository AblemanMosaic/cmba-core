"""Build or verify an unsigned, claim-bounded publication release envelope."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = b"CMBA:PUBLICATION:r001:release-envelope\0"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def build(paths: list[Path]) -> dict:
    boundary_path = ROOT / "RELEASE-BOUNDARY.json"
    boundary = json.loads(boundary_path.read_text(encoding="utf-8"))
    rows = []
    seen = set()
    for path in paths:
        resolved = path.resolve()
        if not resolved.is_file() or resolved.name in seen:
            raise ValueError("PUBLICATION_ARTIFACT_REFUSED")
        seen.add(resolved.name)
        rows.append({"name": resolved.name, "bytes": resolved.stat().st_size, "sha256": digest(resolved)})
    rows.sort(key=lambda row: row["name"])
    body = {
        "schema": "cmba.publication-release-body.r001",
        "distribution": "cmba-core",
        "version": boundary["version"],
        "artifacts": rows,
        "predecessor_source_sha256": boundary["predecessor_source_sha256"],
        "release_boundary_sha256": digest(boundary_path),
        "public_release_gate": boundary["public_release_gate"],
        "public_release_scope": boundary["public_release_scope"],
        "independent_review": boundary["independent_review"],
        "publication": "NOT_PERFORMED",
        "standing": "RESEARCH_PREVIEW_CANDIDATE",
        "signature": "NOT_SIGNED",
        "authority_effect": "NONE",
    }
    return {
        "schema": "cmba.publication-release-envelope.r001",
        "body": body,
        "binding_root": hashlib.sha256(DOMAIN + canonical(body)).hexdigest(),
    }


def verify(envelope: dict, root: Path) -> dict:
    if set(envelope) != {"schema", "body", "binding_root"}:
        raise ValueError("PUBLICATION_ENVELOPE_FIELDS")
    if envelope["schema"] != "cmba.publication-release-envelope.r001":
        raise ValueError("PUBLICATION_ENVELOPE_SCHEMA")
    body = envelope["body"]
    if hashlib.sha256(DOMAIN + canonical(body)).hexdigest() != envelope["binding_root"]:
        raise ValueError("PUBLICATION_ENVELOPE_ROOT")
    if not HEX64.fullmatch(envelope["binding_root"]):
        raise ValueError("PUBLICATION_ENVELOPE_DIGEST")
    if (body["public_release_gate"] != "CLEARED_FOR_LABELED_RESEARCH_PREVIEW"
            or body["independent_review"] != "NOT_PERFORMED"
            or body["publication"] != "NOT_PERFORMED"
            or body["signature"] != "NOT_SIGNED"
            or body["authority_effect"] != "NONE"):
        raise ValueError("PUBLICATION_ENVELOPE_CLAIM")
    for row in body["artifacts"]:
        path = root / row["name"]
        if not path.is_file() or path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
            raise ValueError("PUBLICATION_ARTIFACT_MISMATCH:" + row["name"])
    return {
        "schema": "cmba.publication-release-verification.r001",
        "status": "PASS",
        "binding_root": envelope["binding_root"],
        "artifact_count": len(body["artifacts"]),
        "authority_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", nargs="+", type=Path)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    if args.build:
        if args.out is None or args.out.exists():
            parser.error("--build requires a nonexistent --out")
        envelope = build(args.build)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(envelope, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(verify(envelope, args.out.parent), sort_keys=True))
    else:
        envelope = json.loads(args.verify.read_text(encoding="utf-8"))
        print(json.dumps(verify(envelope, (args.root or args.verify.parent).resolve()), sort_keys=True))


if __name__ == "__main__":
    main()
