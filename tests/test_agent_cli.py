from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

from cmba_agent.protocol import dispatch, manifest, request_schema
from cmba_core import canonical, decode


ROOT = Path(__file__).resolve().parents[1]


def test_manifest_is_closed_read_only_discovery():
    value = manifest()
    assert value["schema"] == "cmba.agent-protocol-manifest.v1"
    assert set(value["interfaces"]) == {"core", "app", "workbench"}
    assert all(v["effect_class"] == "PURE_READ" for v in value["interfaces"].values())
    assert value["effect_interfaces_excluded"] == ["cmba-export"]
    assert value["network"] is False
    canonical(value)


def test_bundled_request_schemas_are_exact_source_bytes():
    paths = {
        "core": ROOT / "schemas/request.schema.json",
        "app": ROOT / "schemas/j1/request.schema.json",
        "workbench": ROOT / "schemas/k1/request.schema.json",
    }
    for interface, path in paths.items():
        assert canonical(request_schema(interface)) == canonical(decode(path.read_bytes(), canonical_required=False))


def test_unified_dispatch_preserves_core_result():
    request = {"schema": "cmba.request.v0.1-i1", "operation": "capabilities", "arguments": {}}
    result = dispatch("core", request)
    assert result["authority_effect"] == "NONE"
    assert type(result["capabilities"]) is list


def test_all_discovered_capability_shapes_preserve_read_only_boundary():
    requests = {
        "core": {"schema": "cmba.request.v0.1-i1", "operation": "capabilities", "arguments": {}},
        "app": {"schema": "cmba.request.j1", "operation": "capabilities", "arguments": {}},
        "workbench": {"schema": "cmba.workbench-request.k1", "operation": "capabilities", "arguments": {}},
    }
    for interface, request in requests.items():
        result = dispatch(interface, request)
        capabilities = result if isinstance(result, list) else result["capabilities"]
        assert capabilities
        assert all(item["authority_effect"] == "NONE" for item in capabilities)
        assert all(item["network"] is False for item in capabilities)
        effectful = sorted(
            item["capability_id"] for item in capabilities if item["effect_class"] != "PURE_READ"
        )
        assert effectful == (["cmba.workbench.export"] if interface == "workbench" else [])

    workbench_manifest = manifest()["interfaces"]["workbench"]
    assert "export" not in workbench_manifest["operations"]
    assert manifest()["effect_interfaces_excluded"] == ["cmba-export"]


def run_cli(*args: str, stdin: bytes | None = None):
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(ROOT / "src") + (os.pathsep + existing if existing else "")
    return subprocess.run(
        [sys.executable, "-m", "cmba_agent.cli", *args],
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )


def test_cli_version_and_manifest_are_canonical():
    for command in ("version", "manifest"):
        completed = run_cli(command)
        assert completed.returncode == 0, completed.stderr.decode()
        raw = completed.stdout[:-1]
        assert completed.stdout.endswith(b"\n")
        assert canonical(decode(raw)) == raw


def test_cli_request_envelope_and_typed_refusal():
    request = canonical({"schema": "cmba.request.v0.1-i1", "operation": "capabilities", "arguments": {}})
    completed = run_cli("request", "core", "-", stdin=request)
    assert completed.returncode == 0
    result = decode(completed.stdout[:-1])
    assert result["schema"] == "cmba.agent-response.v1"
    assert result["status"] == "OK"
    assert result["interface"] == "core"

    refused = run_cli("request", "core", "-", stdin=b" {}")
    assert refused.returncode == 2
    failure = decode(refused.stdout[:-1])
    assert failure["status"] == "REFUSED"
    assert failure["error"]["code"] == "CMBA_NOT_CANONICAL"
