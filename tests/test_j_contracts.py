from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,sys
import pytest,jsonschema
from cmba_core import canonical,decode,Refusal
from cmba_core.j1 import demo
from cmba_core.j1.registry import contracts
from cmba_core.j1.evaluation import evaluate
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import export_j_schemas

MAP={'cmba.chc.graph':'record-graph','cmba.gendev.rich-session':'record-session','cmba.kasd':'record-kasd',
 'cmba.consent':'record-consent','cmba.admissibility':'record-admissibility','cmba.disclosure':'record-disclosure',
 'cmba.observation':'record-observation','cmba.coordination':'record-coordination','cmba.reconciliation':'record-reconciliation',
 'cmba.execution-record':'record-execution','cmba.claim-trace':'record-trace','cmba.endorsements':'record-endorsements','cmba.native-dkn':'record-native'}

@pytest.mark.parametrize('name',list(MAP))
def test_exported_application_schemas(name):
    schemas=export_j_schemas.build();b=demo.all_bundles()[name]
    jsonschema.Draft202012Validator(schemas[MAP[name]]).validate(b['values']['record'])
    jsonschema.Draft202012Validator(schemas['context']).validate(b['context'])
    jsonschema.Draft202012Validator(schemas['bundle']).validate({'schema':'cmba.workbench-bundle.j1',**b})
    jsonschema.Draft202012Validator(schemas['receipt']).validate(demo.assess(b))
    record=cp(b['values']['record']);record['unrecognized-extra-field']=True
    with pytest.raises(jsonschema.ValidationError):jsonschema.Draft202012Validator(schemas[MAP[name]]).validate(record)

def test_exported_schemas_exact_regeneration():
    schemas=export_j_schemas.build();assert len(schemas)==24
    for name,schema in schemas.items():
        assert canonical(schema)==canonical(json.loads((ROOT/'schemas/j1'/f'{name}.schema.json').read_text(encoding='utf-8')))
        jsonschema.Draft202012Validator.check_schema(schema)
    assert canonical(schemas)==(ROOT/'src/cmba_core/data/j1-schemas.json').read_bytes()

def test_schema_pass_not_cryptographic_pass():
    b=demo.kasd();r=demo.assess(b);r['body']['result']['status']='NO_MATCH'
    jsonschema.Draft202012Validator(export_j_schemas.build()['receipt']).validate(r)
    from cmba_core.j1.evaluation import replay
    with pytest.raises(Refusal):replay(r,b['binding'],b['values'],b['context'])

def test_frozen_i1_and_native_files_preserved():
    m=json.loads((ROOT/'history/i1/FILE-MANIFEST.json').read_text(encoding='utf-8'))
    retained=[r for r in m['files'] if r['path'].startswith('src/') or r['path'] in (
      'model/CONTRACT.json','model/COMMITMENT.json','interop/core-i1.json') or r['path'].startswith('baseline/dkn/')]
    assert retained
    for r in retained:
        actual=hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()
        if r['path']=='src/cmba_core/cli.py':assert actual!=r['sha256']
        else:assert actual==r['sha256'],r['path']

def test_key_admission_copy_exact():
    import os
    original=Path(os.environ['DKN_TEST_ROOT'])/'src/dkn_v02/key_validation.py'
    assert original.read_bytes()==(ROOT/'src/cmba_core/j1/_key_admission.py').read_bytes()

def test_catalogue_preserves_sources_and_does_not_invent_domain_engines():
    old=json.loads((ROOT/'catalogue/APPLICATIONS.json').read_text(encoding='utf-8'))
    new=decode((ROOT/'catalogue/APPLICATIONS-J1.json').read_bytes())
    assert len(new['entries'])==71 and len(new['domain_templates'])==52
    assert canonical(new)==(ROOT/'src/cmba_core/data/j1-catalogue.json').read_bytes()
    by_id={e['catalogue_id']:e for e in old['entries']}
    for row in new['entries']:assert row['source_record_preserved']==by_id[row['catalogue_id']]
    for template in new['domain_templates']:
        assert template['validation']=='NOT_IMPLEMENTED_DOMAIN_ENGINE' and template['operational_control'] is False
        if template['label'] in ('CMBA-Military','CMBA-Weapons','CMBA-Nuclear'):assert not template['capability_mappings']
    vote=next(e for e in new['entries'] if e['catalogue_id']=='family.vote')
    assert vote['implementation']=='RESEARCH_REFERENCE_ONLY' and vote['callable'] is False

@pytest.mark.parametrize('field', ['evidence_snapshot','authority_snapshot'])
def test_context_budgets(field):
    b=demo.kasd()
    if field=='evidence_snapshot':b['context'][field]=b['context'][field][:1]*65
    else:b['context'][field]['members']=b['context'][field]['members'][:1]*65
    with pytest.raises(Refusal,match='SEQUENCE_LIMIT'):demo.assess(b)

def test_disclosure_budget_and_no_single_empty_allproof():
    from cmba_core.j1.disclosure import make
    with pytest.raises(Refusal):make([])
    with pytest.raises(Refusal):make([{'label':str(i),'schema_id':'x','value':i} for i in range(65)])

def test_boolean_vs_integer_exact_oracle():
    from run_conformance import compare_output
    with pytest.raises(Refusal,match='CONFORMANCE_MISMATCH'):compare_output(b'{"x":1}',{'x':True})
    with pytest.raises(Refusal,match='CONFORMANCE_MISMATCH'):compare_output(b'null',{'status':'RESULT'})

def test_j_model_traceability():
    import check_j_model
    assert check_j_model.check()['obligations']>=20

@pytest.mark.parametrize('case', json.loads((ROOT/'interop/applications-j1.json').read_text(encoding='utf-8'))['cases'], ids=lambda c:c['id'])
def test_frozen_j_conformance(case):
    from reference_j_conformance import dispatch
    assert canonical(dispatch(case['request']))==canonical(case['expected'])

@pytest.mark.parametrize('xml',[
 '<testsuites><testsuite tests="0"/></testsuites>',
 '<testsuites><testsuite tests="2"><testcase classname="x" name="y"/></testsuite></testsuites>',
 '<testsuites><testsuite tests="1"><testcase classname="x" name="y"><skipped/></testcase></testsuite></testsuites>',
 '<testsuites><testsuite tests="2"><testcase classname="x" name="y"/><testcase classname="x" name="y"/></testsuite></testsuites>',
 '<testsuites><testsuite tests="1" errors="1"><testcase classname="x" name="y"/></testsuite></testsuites>'
])
def test_release_runner_refuses_incomplete_test_evidence(tmp_path,xml):
    import verify_j
    path=tmp_path/'tests.xml';path.write_text(xml)
    with pytest.raises(ValueError):verify_j.test_summary(path)
