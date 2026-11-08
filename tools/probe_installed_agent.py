"""Probe the installed wheel's machine interface without importing source-tree code."""
from __future__ import annotations

import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys

from cmba_agent.protocol import dispatch, manifest, request_schema
from cmba_core import canonical, decode


def _capabilities(result: object, interface: str) -> tuple[list[dict], str, list[str]]:
    if isinstance(result, list):
        capabilities = result
        shape = "list"
    elif isinstance(result, dict) and isinstance(result.get("capabilities"), list):
        capabilities = result["capabilities"]
        shape = "object.capabilities"
    else:
        raise RuntimeError("unsupported capabilities response shape")
    if not capabilities or not all(isinstance(item, dict) for item in capabilities):
        raise RuntimeError("capabilities response must contain capability objects")
    for item in capabilities:
        if item.get("authority_effect") != "NONE":
            raise RuntimeError("installed capability exceeds no-authority boundary")
        if item.get("network") is not False:
            raise RuntimeError("installed capability unexpectedly permits network access")
    effectful = sorted(
        item["capability_id"] for item in capabilities if item.get("effect_class") != "PURE_READ"
    )
    expected_effectful = ["cmba.workbench.export"] if interface == "workbench" else []
    if effectful != expected_effectful:
        raise RuntimeError("installed capabilities have an unexpected effect boundary")
    return capabilities, shape, effectful


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("--out must not exist")

    found = manifest()
    operations = {}
    schema_hashes = {}
    requests = {
        "core": {"schema": "cmba.request.v0.1-i1", "operation": "capabilities", "arguments": {}},
        "app": {"schema": "cmba.request.j1", "operation": "capabilities", "arguments": {}},
        "workbench": {"schema": "cmba.workbench-request.k1", "operation": "capabilities", "arguments": {}},
    }
    for interface, request in requests.items():
        result = dispatch(interface, request)
        capabilities, shape, excluded_effectful = _capabilities(result, interface)
        operations[interface] = {
            "status": "PASS",
            "authority_effect": "NONE",
            "capability_count": len(capabilities),
            "effectful_capabilities_not_agent_callable": excluded_effectful,
            "result_shape": shape,
            "result_sha256": hashlib.sha256(canonical(result)).hexdigest(),
        }
        schema_hashes[interface] = hashlib.sha256(canonical(request_schema(interface))).hexdigest()

    completed = subprocess.run(
        [sys.executable, "-m", "cmba_agent.cli", "request", "core", "-"],
        input=canonical(requests["core"]),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0 or completed.stderr or not completed.stdout.endswith(b"\n"):
        raise RuntimeError("installed agent CLI request failed")
    cli_response = decode(completed.stdout[:-1])
    if (
        cli_response.get("schema") != "cmba.agent-response.v1"
        or cli_response.get("status") != "OK"
        or cli_response.get("interface") != "core"
        or cli_response.get("authority_effect") != "NONE"
    ):
        raise RuntimeError("installed agent CLI returned an unexpected envelope")

    receipt = {
        "schema": "cmba.installed-agent-probe.r001",
        "status": "PASS",
        "distribution": "cmba-core",
        "distribution_version": version("cmba-core"),
        "agent_protocol": found["agent_protocol"],
        "interfaces": sorted(found["interfaces"]),
        "operations": operations,
        "cli_request": {
            "status": "PASS",
            "response_sha256": hashlib.sha256(canonical(cli_response)).hexdigest(),
        },
        "request_schema_sha256": schema_hashes,
        "network": found["network"],
        "effect_interfaces_excluded": found["effect_interfaces_excluded"],
        "authority_effect": "NONE",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
