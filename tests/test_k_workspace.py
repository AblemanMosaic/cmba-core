from copy import deepcopy as cp
import json,hashlib,os,sys,subprocess
from pathlib import Path
import pytest
from cmba_core import canonical,decode,Refusal,bind,relation,reference
from cmba_core.j1.registry import contracts
from cmba_workbench.k1.session import Workspace,execute_task,execute_verified_task,BUNDLE_J
from cmba_workbench.k1.authoring import example,author
from cmba_workbench.k1 import views

PROFILES=[c['profile_id'] for c in contracts()]

@pytest.mark.parametrize('profile',PROFILES)
def test_all_application_profiles_through_workbench(profile):
    w=Workspace();b=example(profile);w.load(b)
    assert w.inspection()['status']=='BINDING_STRUCTURE_VALID'
    with pytest.raises(Refusal,match='READER_CONTEXT_REQUIRED'):w.evaluate()
    w.use_demo_context();r=w.evaluate()
    assert r['body']['result']['status'] in ('MATCH_FOR_SUPPLIED_EVIDENCE','NATIVE_REPORT_COMPUTED')
    assert r['body']['result']['authority_effect']=='NONE'
    assert w.replay_history(0)['status']=='MATCH_EXACT_EVALUATION_REPLAY'
    assert views.matrix(r)['authorization']=='EXTERNAL_DECISION_REQUIRED'


def test_explicit_context_ownership_and_no_adoption():
    w=Workspace();b=example('cmba.consent');w.load(b)
    bad=cp(b['context']);bad['expected_binding_root']='0'*64
    with pytest.raises(Refusal,match='ROOT_MISMATCH'):w.set_reader_context(bad)
    with pytest.raises(Refusal):w.context()
    w.set_reader_context(b['context']);assert w._context_source=='READER_SELECTED'
    assert w.evaluate()['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
    bad['handler']='os.system'
    with pytest.raises(Refusal):w.set_reader_context(bad)
    with pytest.raises(Refusal):w.evaluate()
    assert w.history()[0]['status']=='MATCH_FOR_SUPPLIED_EVIDENCE' # historical only
    assert w._last is None


def test_same_binding_different_time_separate_receipts():
    w=Workspace();b=example('cmba.consent');w.load(b);w.use_demo_context();a=w.evaluate()
    c=cp(b['context']);c['time']['epoch']=201;w.set_reader_context(c);z=w.evaluate()
    assert a['body']['binding_root']==z['body']['binding_root']
    assert a['receipt_hash']!=z['receipt_hash'] and z['body']['result']['status']!='MATCH_FOR_SUPPLIED_EVIDENCE'
    assert len(w.history())==2

@pytest.mark.parametrize('replacement',[b'null',b'{}',b'{"schema":1,"schema":2}',b' { }',b'{"x":1.0}'])
def test_failed_import_clears_active_context(replacement):
    w=Workspace();w.load(example('cmba.chc.graph'));w.use_demo_context();w.evaluate()
    with pytest.raises(Refusal):w.load_raw(replacement)
    assert len(w.history())==1 and w._selected is None
    with pytest.raises(Refusal):w.selected()


def test_task_source_change_cancellation_and_rehashed_forgery():
    w=Workspace();w.load(example('cmba.chc.graph'));w.use_demo_context();t=w.prepare_evaluation()
    result=execute_task(t);w.cancel()
    with pytest.raises(Refusal,match='STALE_RESULT'):w.accept_result(result)
    w.use_demo_context();t=w.prepare_evaluation();r=execute_task(t)
    r['receipt']['body']['result']['status']='EXECUTE_ALLOWED'
    from cmba_core.j1.common import hash_value
    r['receipt']['receipt_hash']=hash_value('receipt',r['receipt']['body'])
    with pytest.raises(Refusal,match='REPLAY_MISMATCH'):w.accept_result(r)
    assert not w.history()
    w.use_demo_context();t=w.prepare_evaluation();verified=execute_verified_task(t)
    assert w.accept_verified(verified)['body']['result']['status']=='MATCH_FOR_SUPPLIED_EVIDENCE'
    with pytest.raises(Refusal,match='HOST_RESULT_REQUIRED'):w.accept_verified({'raw':canonical(r).hex()})


def test_workspace_roundtrip_does_not_restore_trust():
    w=Workspace();w.load(example('cmba.chc.graph'));w.use_demo_context();w.evaluate();snap=w.snapshot()
    restored=Workspace();restored.restore(decode(canonical(snap)))
    assert restored._selected is None and restored._context is None
    assert restored.history()[0]['verification']=='IMPORTED_NOT_REPLAYED'
    restored.replay_history(0)
    assert restored.history()[0]['verification']=='REPLAYED_CURRENT_RUNTIME'
    did=restored.documents()[0]['document_id'];restored.select(did)
    with pytest.raises(Refusal):restored.evaluate()
    assert canonical(restored.snapshot())==canonical(snap)


def test_imported_claimed_receipt_needs_replay():
    w=Workspace();w.load(example('cmba.chc.graph'));w.use_demo_context();w.evaluate();p=w.receipt_packet()
    p['receipt']['body']['result']['status']='MATCH_FOR_SUPPLIED_EVIDENCE'
    p['receipt']['body']['result']['details']['invented']=True
    receiver=Workspace();receiver.import_receipt(p)
    assert receiver.history()[0]['verification']=='IMPORTED_NOT_REPLAYED'
    with pytest.raises(Refusal):receiver.replay_history(0)
    assert receiver.history()[0]['verification']=='IMPORTED_NOT_REPLAYED'

@pytest.mark.parametrize('mutation',['trust','extra','duplicate','wrong-id','bad-body','source'])
def test_workspace_malformed_refused(mutation):
    w=Workspace();w.load(example('cmba.chc.graph'));w.use_demo_context();w.evaluate();s=w.snapshot()
    if mutation=='trust':s['trust_state']='ADOPT_PINS'
    if mutation=='extra':s['execute']='payload'
    if mutation=='duplicate':s['documents'].append(cp(s['documents'][0]))
    if mutation=='wrong-id':s['documents'][0]['document_id']='0'*64
    if mutation=='bad-body':s['history'][0]['receipt']['body']={}
    if mutation=='source':s['history'][0]['context_source']='TRUSTED'
    with pytest.raises(Refusal):Workspace().restore(s)


def test_snapshot_detaches_caller_values_and_freezes_limits():
    b=example('cmba.chc.graph');w=Workspace();w.load(b);b['values']['record']['outputs']=[]
    assert w.selected()['values']['record']['outputs']
    for i in range(63):w.load(author('cmba.generic',{'n':i}),name=str(i))
    with pytest.raises(Refusal,match='DOCUMENT_LIMIT'):w.load(author('cmba.generic',{'n':1000}))
    assert len(w.documents())==64


def test_history_budget_refuses_without_silent_eviction(monkeypatch):
    import cmba_workbench.k1.session as module
    monkeypatch.setattr(module,'MAX_HISTORY',2)
    w=Workspace();w.load(example('cmba.chc.graph'));w.use_demo_context();w.evaluate();w.evaluate()
    with pytest.raises(Refusal,match='HISTORY_LIMIT'):w.evaluate()
    assert len(w.history())==2


def test_navigation_resolution_scope_and_truncation():
    w=Workspace();a=author('cmba.generic',{'a':1});aid=w.load(a)['document_id']
    rels=[relation('depends','depends_on',reference('cmba.binding',a['binding']['binding_root'])),
          relation('lookalike','mentions',reference('different.scheme',a['binding']['binding_root']))]
    b=author('cmba.generic',{'b':1},relations=rels);bid=w.load(b)['document_id']
    graph=w.navigate();assert graph['scope']=='ADMITTED_LOCAL_COLLECTION_ONLY'
    assert [x['target_status'] for x in graph['edges']]==['PRESENT_LOCALLY','NOT_RESOLVED']
    limited=w.navigate(max_nodes=1,max_edges=1)
    assert limited['node_limited'] and limited['edge_limited'] and limited['truncated']
    assert w.compare_documents(aid,bid)['semantic_equivalence']=='NOT_ESTABLISHED'
    assert w.navigate(max_edges=2)['completeness']=='NOT_GLOBAL'


def test_authoring_preserves_no_stale_approvals():
    b=example('cmba.kasd');r=cp(b['values']['record']);r['facts']['public']=False
    created=author('cmba.kasd',r)
    assert created['binding']['binding_root']!=b['binding']['binding_root']
    assert created['context']['authority_snapshot']['members']==[] and created['context']['evidence_snapshot']==[]
    w=Workspace();w.load(created);w.use_demo_context();assert w.evaluate()['body']['result']['status']!='MATCH_FOR_SUPPLIED_EVIDENCE'

@pytest.mark.parametrize('profile',['os.system','__import__','http://evil','cmba.vote','cmba.weapons'])
def test_author_never_imports_handlers(profile):
    with pytest.raises(Refusal):author(profile,{'handler':'os.system'})


def test_core_evaluator_identity_is_unchanged_from_frozen_j():
    from cmba_core.evaluation import realization_identity
    root=Path(__file__).resolve().parents[1]
    m=json.loads((root/'history/j1/FILE-MANIFEST.json').read_text(encoding='utf-8'))
    changed=[]
    for row in m['files']:
        if row['path'].startswith('src/'):
            actual=hashlib.sha256((root/row['path']).read_bytes()).hexdigest()
            if actual!=row['sha256']:changed.append(row['path'])
    assert changed==['src/cmba_core/cli.py']
    assert len(realization_identity())==64


def test_k_library_no_tk_crypto_or_native_import_by_default():
    root=Path(__file__).resolve().parents[1];env=os.environ.copy();env['PYTHONPATH']=str(root/'src')
    code="import sys;from cmba_workbench.k1.session import Workspace;from cmba_workbench.k1.authoring import example;w=Workspace();w.load(example('cmba.chc.graph'));w.use_demo_context();w.evaluate();assert not any(k.startswith(('tkinter','cryptography','dkn_v02')) for k in sys.modules)"
    p=subprocess.run([sys.executable,'-S','-c',code],env=env,capture_output=True);assert p.returncode==0,p.stderr
