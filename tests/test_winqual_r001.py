"""Successor preservation and Windows-qualification boundary checks."""
from pathlib import Path
import hashlib,json,tomllib

ROOT=Path(__file__).resolve().parents[1]


def test_distribution_and_release_boundary_are_a7_publication_successor():
    project=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))
    boundary=json.loads((ROOT/'RELEASE-BOUNDARY.json').read_text(encoding='utf-8'))
    assert project['project']['version']==boundary['version']=='0.1.0a7'
    assert boundary['engineering_review']=='PUBLICATION-CLOSURE-r001'
    assert boundary['public_release_gate']=='CLEARED_FOR_LABELED_RESEARCH_PREVIEW'
    assert boundary['independent_review']=='NOT_PERFORMED'


def test_i1_semantics_preserved_and_jk_commitments_deliberately_renewed():
    manifest=json.loads((ROOT/'history/audit-r001-predecessor/FILE-MANIFEST.json').read_text(encoding='utf-8'))
    rows={r['path']:r for r in manifest['files']}
    retained=[p for p in rows if p.startswith('src/cmba_core/') and p!='src/cmba_core/cli.py']
    retained+=['model/CONTRACT.json','model/COMMITMENT.json','interop/core-i1.json']
    assert retained
    for name in retained:
        raw=(ROOT/name).read_bytes()
        assert len(raw)==rows[name]['bytes']
        assert hashlib.sha256(raw).hexdigest()==rows[name]['sha256'],name
    for name in ('src/cmba_core/cli.py','model/j1/CONTRACT.json','model/j1/COMMITMENT.json',
                 'model/k1/CONTRACT.json','model/k1/COMMITMENT.json',
                 'interop/applications-j1.json','interop/workbench-k1.json'):
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=rows[name]['sha256']
    j=json.loads((ROOT/'model/j1/CONTRACT.json').read_text(encoding='utf-8'))
    k=json.loads((ROOT/'model/k1/CONTRACT.json').read_text(encoding='utf-8'))
    assert [o['id'] for o in j['obligations']]==[f'J-{n:02d}' for n in range(1,29)]
    assert [o['id'] for o in k['obligations']]==[f'K-{n:02d}' for n in range(1,27)]


def test_successor_review_records_commitment_transition_and_open_review_gate():
    ledger=json.loads((ROOT/'PROGRAM-LEDGER.json').read_text(encoding='utf-8'))
    assert ledger['successor_review']['runtime_change']=='EVIDENCE_WITNESS_AND_TERMINAL_CLOSURE_NO_RUNTIME_FEATURES'
    assert ledger['successor_review']['semantic_transition']=='I1_J1_EXACT_K1_COMMITMENT_RENEWED_FOR_PLATFORM_AMENDMENT'
    assert ledger['successor_review']['independent_review']=='NOT_PERFORMED'
    assert ledger['publication_successor']['distribution_version']=='0.1.0a7'
    assert ledger['publication_successor']['predecessor_source_sha256']=='1eff3fd4038fdd0955d30d0bb36079e01d9579393339ff23be2b8f43296e451f'
    assert ledger['public_release_gate']=='CLEARED_FOR_LABELED_RESEARCH_PREVIEW'
