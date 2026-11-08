"""Unified, canonical JSON command line for machine consumers."""
from __future__ import annotations

import argparse
import sys

from cmba_core.cli import read_local
from cmba_core.codec import MAX_BYTES, canonical, decode
from cmba_core.errors import Refusal, require

from .protocol import INTERFACES, dispatch, distribution_version, manifest, request_schema


def _write(value: object) -> None:
    sys.stdout.buffer.write(canonical(value) + b"\n")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmba-agent",
        description="CMBA machine protocol discovery and read-only dispatch",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version", help="emit installed distribution and agent protocol versions")
    sub.add_parser("manifest", help="emit the machine-readable interface manifest")
    schema = sub.add_parser("schema", help="emit one bundled request schema")
    schema.add_argument("interface", choices=INTERFACES)
    request = sub.add_parser("request", help="dispatch one exact canonical JSON request")
    request.add_argument("interface", choices=INTERFACES)
    request.add_argument("input", help="canonical JSON file, or - for stdin")
    return parser


def _response(interface: str, result: object) -> dict:
    return {
        "schema": "cmba.agent-response.v1",
        "status": "OK",
        "interface": interface,
        "result": result,
        "authority_effect": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "version":
            result = {
                "schema": "cmba.agent-version.v1",
                "status": "OK",
                "distribution": "cmba-core",
                "distribution_version": distribution_version(),
                "agent_protocol": "v1",
                "authority_effect": "NONE",
            }
        elif args.command == "manifest":
            result = manifest()
        elif args.command == "schema":
            result = {
                "schema": "cmba.agent-schema-response.v1",
                "status": "OK",
                "interface": args.interface,
                "request_schema": request_schema(args.interface),
                "authority_effect": "NONE",
            }
        else:
            raw = sys.stdin.buffer.read(MAX_BYTES + 1) if args.input == "-" else read_local(args.input)
            require(len(raw) <= MAX_BYTES, "CMBA_BYTE_LIMIT")
            result = _response(args.interface, dispatch(args.interface, decode(raw)))
        _write(result)
        return 0
    except Refusal as exc:
        _write({
            "schema": "cmba.agent-response.v1",
            "status": "REFUSED",
            "error": {"code": exc.code},
            "authority_effect": "NONE",
        })
        return 2
    except OSError:
        _write({
            "schema": "cmba.agent-response.v1",
            "status": "REFUSED",
            "error": {"code": "CMBA_AGENT_IO_ERROR"},
            "authority_effect": "NONE",
        })
        return 2
    except Exception:
        _write({
            "schema": "cmba.agent-response.v1",
            "status": "ERROR",
            "error": {"code": "CMBA_AGENT_INTERNAL_ERROR"},
            "authority_effect": "NONE",
        })
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
