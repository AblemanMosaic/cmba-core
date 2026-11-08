"""Installed protocol discovery for agents and other machine consumers."""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files
from typing import Any

from cmba_core.codec import clone, decode
from cmba_core.errors import Refusal


INTERFACES = ("core", "app", "workbench")
_SCHEMAS = {
    "core": "request-core.json",
    "app": "request-app.json",
    "workbench": "request-workbench.json",
}


def distribution_version() -> str:
    try:
        return version("cmba-core")
    except PackageNotFoundError:
        return "0.1.0a7+source"


def manifest() -> dict[str, Any]:
    raw = files("cmba_agent").joinpath("data/protocol-manifest.json").read_bytes()
    value = decode(raw, canonical_required=False)
    value["distribution_version"] = distribution_version()
    return clone(value)


def request_schema(interface: str) -> dict[str, Any]:
    if interface not in _SCHEMAS:
        raise Refusal("CMBA_AGENT_INTERFACE_UNSUPPORTED")
    raw = files("cmba_agent").joinpath("data", _SCHEMAS[interface]).read_bytes()
    return decode(raw, canonical_required=False)


def dispatch(interface: str, request: dict[str, Any]) -> Any:
    if interface == "core":
        from cmba_core.abi import dispatch as handler
    elif interface == "app":
        from cmba_core.j1.abi import dispatch as handler
    elif interface == "workbench":
        from cmba_workbench.k1.abi import dispatch as handler
    else:
        raise Refusal("CMBA_AGENT_INTERFACE_UNSUPPORTED")
    return handler(request)
