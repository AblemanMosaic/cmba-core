from copy import deepcopy as cp
from pathlib import Path
import sys,subprocess,os,threading,time,hashlib
import pytest
from cmba_core import canonical,decode,Refusal
from cmba_core.j1 import disclosure
from cmba_workbench.k1 import views
from cmba_workbench.k1.authoring import example,author
from cmba_workbench.k1.session import Workspace
from cmba_workbench.k1.abi import dispatch
from cmba_workbench.k1.effects import LocalEffects
from cmba_workbench.k1.jobs import Jobs


def req(op,**args):return {'schema':'cmba.workbench-request.k1','operation':op,'arguments':args}

def test_disclosure_export_contains_only_selected_openings(tmp_path):
    private=disclosure.make([{'label':'public','schema_id':'example.text','value':'hello'},
     {'label':'secret','schema_id':'example.text','value':'NEVER_EXPORT_THIS_PRIVATE_VALUE'}],salts=['11'*32,'22'*32])
    preview=views.preview_disclosure(private,['public'],expected_root=private['header']['disclosure_root'])
    assert 'NEVER_EXPORT' not in canonical(preview).decode()
    assert '22'*32 not in canonical(preview).decode()
    assert preview['report']['details']['confidentiality']=='NOT_ESTABLISHED'
    with LocalEffects(tmp_path,current_state=lambda:'a'*64) as h:
        p=h.prepare('disclosure',preview['view'],name='public.json');h.commit(h.approve(p['plan_hash']))
    assert 'NEVER_EXPORT' not in (tmp_path/'public.json').read_text(encoding='utf-8')
    assert decode((tmp_path/'public.json').read_bytes())==preview['view']


def test_disclosure_cannot_hide_invalid_unselected_opening():
    private=disclosure.make([{'label':'public','schema_id':'x','value':1},{'label':'secret','schema_id':'x','value':2}])
    private['openings'][1]['leaf']['value']=99
    with pytest.raises(Refusal):views.preview_disclosure(private,['public'],expected_root=private['header']['disclosure_root'])

@pytest.mark.parametrize('field',list(views.DESIGN_FIELDS))
def test_explorer_explicit_unsupported_combinations(field):
    config={k:v[0] for k,v in views.DESIGN_FIELDS.items()}
    assert views.design(config)['body']['status']=='SUPPORTED_COMPONENTS_NOT_DEPLOYMENT_QUALIFIED'
    config[field]=views.DESIGN_FIELDS[field][-1]
    result=views.design(config)
    assert result['body']['status']=='UNSUPPORTED_COMBINATION' and result['body']['registration']=='NOT_REGISTERED'
    assert result['body']['security_score']=='NOT_COMPUTED'


def test_qualification_never_promotes_declarations():
    a={'semantic_commitment':'0'*64,'realization_sha256':'1'*64,'corpus_sha256':'2'*64,'claimed_results':{'pass':True}}
    b={**a,'realization_sha256':'3'*64,'claimed_results':{'pass':1}}
    r=views.qualification(a,b)
    assert r['same_declared_contract'] and not r['same_realization'] and not r['same_claimed_results']
    assert r['conformance']=='NOT_EXECUTED' and r['replacement_approval']=='EXTERNAL_DECISION_REQUIRED'

@pytest.mark.parametrize('target',['dkn','ccp','ucm','pippi','courthouse'])
def test_handoff_references_only_no_submission(target):
    b=example('cmba.chc.graph');w=Workspace();w.load(b);w.use_demo_context();w.evaluate()
    h=views.handoff(target,b,receipt_packet=w.receipt_packet())
    assert h['body']['receipt_hash']==w.receipt_packet()['receipt']['receipt_hash']
    assert h['body']['network_effect']=='NONE' and h['body']['operational_integration']=='NOT_ESTABLISHED'
    assert 'values' not in h['body'] and 'evidence_snapshot' not in h['body']
    bad=w.receipt_packet();bad['receipt']['body']['result']['status']='EXECUTE'
    with pytest.raises(Refusal):views.handoff(target,b,receipt_packet=bad)


def test_handoff_cannot_attach_another_objects_receipt():
    w=Workspace();w.load(example('cmba.chc.graph'));w.use_demo_context();w.evaluate()
    with pytest.raises(Refusal,match='HANDOFF_SUBJECT'):views.handoff('ucm',example('cmba.gendev.rich-session'),receipt_packet=w.receipt_packet())

@pytest.mark.parametrize('op',['write','approve','commit','sign','exec','execute','install','fetch','publish','trust-update',
                               'open-path','read-vault','load-plugin','delete','replace','shell','__import__'])
def test_k_json_interface_cannot_request_effects(op):
    with pytest.raises(Refusal,match='OPERATION_UNSUPPORTED'):dispatch(req(op))


def test_closed_interface_and_cli_parity():
    b=example('cmba.chc.graph');r=req('evaluate',bundle=b,reader_context=b['context']);expected=dispatch(r)
    p=subprocess.run([sys.executable,'-m','cmba_workbench.k1.cli','-'],input=canonical(r),capture_output=True)
    assert p.returncode==0 and p.stdout==canonical(expected)+b'\n'
    r['arguments']['reader_context']['handler']='some_code'
    with pytest.raises(Refusal):dispatch(r)
    for raw in (b'null',b'{} ',b'{"x":1,"x":2}'):
        p=subprocess.run([sys.executable,'-m','cmba_workbench.k1.cli','-'],input=raw,capture_output=True)
        assert p.returncode==2 and decode(p.stdout[:-1])['status']=='REFUSED'


def test_all_readonly_operations_real_calls():
    b=example('cmba.chc.graph');w=Workspace();w.load(b);w.use_demo_context();w.evaluate()
    assert dispatch(req('inspect',bundle=b))['status']=='BINDING_STRUCTURE_VALID'
    assert dispatch(req('replay',packet=w.receipt_packet()))['status']=='MATCH_EXACT_EVALUATION_REPLAY'
    assert dispatch(req('compare',left=b,right=b))['same_binding']
    assert dispatch(req('navigate',workspace=w.snapshot(),max_nodes=4,max_edges=4))['total_local_documents']==1
    assert len(dispatch(req('catalogue'))['entries'])==71
    assert len(dispatch(req('capabilities'))['capabilities'])>=17
    assert dispatch(req('author',profile_id='cmba.generic',record={'n':1},now=0,parameters={},relations=[]))['schema'].startswith('cmba.workbench-bundle')


def test_interactive_export_refuses_non_operator_input(tmp_path):
    from cmba_workbench.k1.cli import export_main
    f=tmp_path/'source.json';f.write_bytes(canonical(author('cmba.generic',{'x':1})))
    code='from cmba_workbench.k1.cli import export_main;raise SystemExit(export_main())'
    p=subprocess.run([sys.executable,'-c',code,str(f),'--workspace',str(tmp_path),'--name','out.json','--kind','bundle'],input=b'yes\n',capture_output=True)
    assert p.returncode==2 and b'TTY_REQUIRED' in p.stdout and not (tmp_path/'out.json').exists()


def wait_result(job):
    until=time.monotonic()+4
    while time.monotonic()<until:
        r=job.poll()
        if r and not job.busy:return r
        time.sleep(.005)
    raise AssertionError('worker did not finish')


def test_jobs_cancel_discard_and_refuse_concurrent_workers():
    ready=threading.Event();release=threading.Event();job=Jobs()
    def work():ready.set();release.wait(3);return {'result':True}
    job.start(work);assert ready.wait(2)
    with pytest.raises(Refusal,match='JOB_BUSY'):job.start(lambda:None)
    job.cancel();early=job.poll();assert early['worker']=='STILL_RUNNING_RESULT_WILL_BE_DISCARDED'
    assert job.busy;release.set();r=wait_result(job)
    assert r['status']=='CANCELLED' and 'value' not in r
    job.start(lambda:7);assert wait_result(job)['value']==7


def test_jobs_timeout_is_discard_not_a_claim_of_termination():
    now=[0];release=threading.Event();job=Jobs(clock=lambda:now[0])
    job.start(lambda:release.wait(3),seconds=1);now[0]=2
    assert job.poll()['status']=='TIMED_OUT' and job.busy
    release.set();assert wait_result(job)['worker']=='FINISHED_RESULT_DISCARDED'


def test_job_errors_are_typed_without_leaking_exception_payload():
    job=Jobs()
    def fail():raise RuntimeError('SECRET_PATH_VALUE')
    job.start(fail);r=wait_result(job)
    assert r=={'status':'REFUSED','code':'CMBA_K_INTERNAL_ERROR','exception_type':'RuntimeError'}


def test_optional_installed_capability_not_permission():
    cap=next(x for x in views.capabilities() if x['capability_id']=='cmba.workbench.export')
    assert cap['effect_class']=='EXPLICIT_HOST_LOCAL_WRITE'
    assert cap['boundary']=='NOT_CALLABLE_FROM_JSON_ABI' and cap['authority_effect']=='NONE'


def test_receipt_comparison_replays_then_exposes_changed_context():
    w=Workspace();bundle=example('cmba.consent');w.load(bundle);w.use_demo_context();w.evaluate();a=w.receipt_packet()
    context=cp(bundle['context']);context['time']['epoch']=201;w.set_reader_context(context);w.evaluate();b=w.receipt_packet()
    result=views.compare_receipts(a,b)
    assert result['same_binding'] and result['changed_inputs']==['time_hash']
    assert result['left_result']['status']!=result['right_result']['status']
    b['receipt']['body']['result']['status']='APPROVED'
    with pytest.raises(Refusal):views.compare_receipts(a,b)


def test_installed_qualification_is_not_self_authentication():
    r=views.installed_qualification()
    assert r['authentication']=='NOT_ESTABLISHED_BY_SELF_HASH'
    assert len(r['accepted_baselines'])==2 and len(r['installed_core_realization_sha256'])==64
    assert r['independent_review']=='NOT_PERFORMED'
