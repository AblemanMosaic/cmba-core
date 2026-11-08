from pathlib import Path
import json,sys,hashlib,copy
import pytest,jsonschema
from cmba_core import canonical,decode,Refusal
from cmba_workbench.k1.authoring import example
from cmba_workbench.k1.session import Workspace
from cmba_workbench.k1.effects import LocalEffects
from cmba_workbench.k1 import views
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import export_k_schemas
from reference_k_conformance import dispatch

@pytest.mark.parametrize('case',json.loads((ROOT/'interop/workbench-k1.json').read_text(encoding='utf-8'))['cases'],ids=lambda c:c['id'])
def test_frozen_k_conformance(case):
    assert canonical(dispatch(case['request']))==canonical(case['expected'])

@pytest.mark.parametrize('name',list(export_k_schemas.build()))
def test_k_schema_export_exact_and_valid(name):
    s=export_k_schemas.build()[name];jsonschema.Draft202012Validator.check_schema(s)
    assert canonical(s)==canonical(json.loads((ROOT/'schemas/k1'/(name+'.schema.json')).read_text(encoding='utf-8')))


def test_actual_structures_fit_schema_without_authentication(tmp_path):
    schemas=export_k_schemas.build()
    def check(name,value):jsonschema.Draft202012Validator(schemas[name]).validate(value)
    w=Workspace();b=example('cmba.chc.graph');w.load(b);w.use_demo_context();task=w.prepare_evaluation()
    check('bundle',b);check('task',task);w.evaluate();check('receipt-packet',w.receipt_packet());check('workspace',w.snapshot());check('local-graph',w.navigate())
    check('handoff',views.handoff('courthouse',b))
    with LocalEffects(tmp_path,current_state=w.state_binding) as h:
        p=h.prepare('bundle',b,name='test.json');check('effect-plan',p)
        mutated=copy.deepcopy(p);mutated['plan_hash']='0'*64;check('effect-plan',mutated)
        with pytest.raises(Refusal):h.approve(mutated['plan_hash'])
        p=h.prepare('bundle',b,name='test.json');r=h.commit(h.approve(p['plan_hash']));check('effect-receipt',r)


def test_request_schemas_refuse_effects_and_boolean_limits():
    schema=export_k_schemas.build()['request'];v=jsonschema.Draft202012Validator(schema)
    for op in ('commit','approve','write','execute'):
        with pytest.raises(jsonschema.ValidationError):v.validate({'schema':'cmba.workbench-request.k1','operation':op,'arguments':{}})


def test_k_semantic_traceability():
    import check_k_model
    assert check_k_model.check()['obligations']==26


def test_preserved_i1_model_and_deliberately_renewed_jk_models_and_corpora():
    m=json.loads((ROOT/'history/audit-r001-predecessor/FILE-MANIFEST.json').read_text(encoding='utf-8'))
    paths={'model/CONTRACT.json','model/COMMITMENT.json','interop/core-i1.json'}
    found=[]
    for r in m['files']:
        if r['path'] in paths:
            assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'];found.append(r['path'])
    assert set(found)==paths
    changed=('model/j1/CONTRACT.json','model/j1/COMMITMENT.json','model/k1/CONTRACT.json',
             'model/k1/COMMITMENT.json','interop/applications-j1.json','interop/workbench-k1.json')
    rows={r['path']:r for r in m['files']}
    for name in changed:
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=rows[name]['sha256']
