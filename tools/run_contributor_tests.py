"""Portable contributor test lanes; release qualification remains separate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
LANES = {
    "agent": ["tests/test_agent_cli.py"],
    "core": [
        "tests/test_bindings.py",
        "tests/test_codec.py",
        "tests/test_contracts.py",
        "tests/test_evaluation.py",
        "tests/test_interfaces.py",
        "tests/test_agent_cli.py",
        "tests/test_publication.py",
    ],
    # The optional lane intentionally excludes the assertion that DKN is absent;
    # that negative dependency case is exercised by the core-only lane.
    "optional": ["tests", "-k", "not test_dkn_missing_dependency_is_typed"],
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=sorted(LANES), default="core")
    parser.add_argument("--basetemp", type=Path)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)

    if args.basetemp is None:
        # Use a sibling of the checkout. Some managed Windows environments expose
        # a nominal system temp directory that subprocesses cannot mutate.
        custody = Path(tempfile.mkdtemp(prefix=f"cmba-{args.lane}-", dir=ROOT.parent))
        base = custody / "pytest"
    else:
        base = args.basetemp.resolve()
        if base.exists():
            parser.error("--basetemp must name a nonexistent path")
        base.parent.mkdir(parents=True, exist_ok=True)

    evidence = args.evidence_dir.resolve() if args.evidence_dir else None
    if evidence is not None:
        if evidence.exists():
            parser.error("--evidence-dir must name a nonexistent path")
        evidence.mkdir(parents=True)

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        f"--basetemp={base}",
        *([f"--junitxml={evidence / 'tests.xml'}"] if evidence else []),
        *LANES[args.lane],
    ]
    print(f"CMBA contributor lane: {args.lane}", flush=True)
    print(f"Temporary custody: {base}", flush=True)
    completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=evidence is not None)
    if evidence is None:
        return completed.returncode

    assert completed.stdout is not None and completed.stderr is not None
    sys.stdout.buffer.write(completed.stdout)
    sys.stderr.buffer.write(completed.stderr)
    stdout_path = evidence / "stdout.txt"
    stderr_path = evidence / "stderr.txt"
    stdout_path.write_bytes(completed.stdout)
    stderr_path.write_bytes(completed.stderr)
    xml_path = evidence / "tests.xml"
    suite = ET.parse(xml_path).getroot()
    counts = {name: sum(int(item.get(name, "0")) for item in suite.iter("testsuite"))
              for name in ("tests", "failures", "errors", "skipped")}
    receipt = {
        "schema": "cmba.contributor-test-receipt.r001",
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "lane": args.lane,
        "python": platform.python_version(),
        "platform": platform.system(),
        "command": command,
        "exit_code": completed.returncode,
        "counts": counts,
        "stdout_sha256": hashlib.sha256(completed.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr).hexdigest(),
        "junit_sha256": hashlib.sha256(xml_path.read_bytes()).hexdigest(),
        "authority_effect": "NONE",
    }
    (evidence / "receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
