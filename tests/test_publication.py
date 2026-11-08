from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("verify_publication", ROOT / "tools/verify_publication.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_publication_layer_is_closed_and_claim_bounded():
    result = MODULE.verify(ROOT)
    assert result["status"] == "PASS"
    assert result["public_release_gate"] == "CLEARED_FOR_LABELED_RESEARCH_PREVIEW"
    assert result["independent_review"] == "NOT_PERFORMED"
    assert result["publication"] == "NOT_PERFORMED"
    assert result["authority_effect"] == "NONE"


def test_agent_cli_is_not_an_effect_path():
    source = (ROOT / "src/cmba_agent/cli.py").read_text(encoding="utf-8")
    assert "cmba-export" not in source
    assert "LocalEffects" not in source
    assert "subprocess" not in source
