"""PUBLIC TEST FIXTURES ONLY. Deterministic keys are public examples, NEVER production identities.

Importing this module has no effects. Explicit fixture calls create temporary in-memory
keys and signed examples. No signing private key is serialized into any output.
"""
import hashlib
from ..codec import canonical,clone
from ..bindings import reference,dimension,bind,profile_reference
from ..registry import contract as i_contract
from ..profiles.dkn import bind_archive
from .common import hash_value
from .evaluation import bind_application,context_for,evaluate,replay
from .endorsements import seal,public_key,endorse,policy as endorsement_policy
from .transforms import toolchain,transform
from .governance import consent_context
from .disclosure import make,select

NOW=100


def fixture_key(number=1):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    return Ed25519PrivateKey.from_private_bytes(bytes([number])*32)


def ref(label):
    return reference('example.fixture',hashlib.sha256(label.encode()).hexdigest())


def authority(entries):
    return {'members':[{'public_key':public_key(key),'roles':roles,'jurisdictions':jurisdictions}
                       for key,roles,jurisdictions in entries],'revoked_keys':[]}


def bundle(profile,record, *, parameters=None, authorities=None, evidence=None):
    b=bind_application(profile,record)
    b['context']=context_for(b['binding'],now=NOW,parameters=parameters,authority=authorities,evidence=evidence)
    return b


def assess(b):return evaluate(b['binding'],b['values'],b['context'])


def graph():
    raw=' { "b": 2, "a": 1 } '; out=transform({'id':'canonical-json','version':1},[raw])
    node=lambda name,value:{'id':name,'text':value,'sha256':hashlib.sha256(value.encode()).hexdigest()}
    record={'nodes':[node('input',raw),node('output',out)],
            'steps':[{'id':'canonicalize','inputs':['input'],'output':'output','rule':{'id':'canonical-json','version':1},'toolchain':toolchain()}],
            'outputs':['output']}
    return bundle('cmba.chc.graph',record)


def session():
    source='Choose canonical JSON; reconsider when the supported grammar changes.'
    events=[]
    for ident,kind,start,end in [('decision','decision',0,21),('trigger','trigger',23,len(source))]:
        events.append({'id':ident,'type':kind,'attributed_to':'example.author','start_byte':start,'end_byte':end,
           'quote':source.encode()[start:end].decode(),'interpretation':source[start:end],
           'references':[] if ident=='decision' else ['decision']})
    return bundle('cmba.gendev.rich-session', {'source':{'text':source,'sha256':hashlib.sha256(source.encode()).hexdigest(),
                   'coverage':'SUPPLIED_RECORD_ONLY'},'events':events})


def approval(record,requirement,key, *, decision='approve',not_before=0,not_after=200):
    r=next(r for r in record['requirements'] if r['id']==requirement)
    return seal('approval',{'subject':record['subject'],'action':record['action'],
         'terms_hash':hash_value('jurisdiction-terms',record),'requirement_id':r['id'],
         'role':r['role'],'jurisdiction':r['jurisdiction'],'decision':decision,
         'not_before':not_before,'not_after':not_after},key)


def kasd(subject=None):
    a=fixture_key(1);s=fixture_key(2)
    record={'subject':subject or ref('artifact'),'action':'publish','facts':{'encoding':'utf8','public':True},
      'requirements':[{'id':'architecture','role':'architect','jurisdiction':'org.arch','threshold':1,'constraints':{'encoding':'utf8'}},
                      {'id':'security','role':'reviewer','jurisdiction':'org.sec','threshold':1,'constraints':{'public':True,'encoding':'utf8'}}]}
    roster=authority([(a,['architect'],['org.arch']),(s,['reviewer'],['org.sec'])])
    evidence=[approval(record,'architecture',a),approval(record,'security',s)]
    return bundle('cmba.kasd',record,authorities=roster,evidence=evidence)


def grant(record,key=None, *, until=200,not_before=0,grant_id='example.grant',supersedes=None):
    key=key or fixture_key(3)
    return seal('consent-grant',{'grant_id':grant_id,'subject':record['subject'],'actor':record['actor'],
        'action':record['action'],'jurisdiction':record['jurisdiction'],'conditions':{'public':True},
        'context_hash':consent_context(record),'not_before':not_before,'not_after':until,
        'delegation_depth':0,'supersedes':[] if supersedes is None else supersedes},key)


def consent(subject=None):
    record={'subject':subject or ref('artifact'),'actor':'example.agent','action':'publish','jurisdiction':'owner',
            'facts':{'public':True},'renewal_context':{'purpose':'release-v1'}}
    k=fixture_key(3)
    return bundle('cmba.consent',record,authorities=authority([(k,['consent-issuer'],['owner'])]),evidence=[grant(record,k)])


def disclosure(subject=None):
    entries=[{'label':'artifact','schema_id':'cmba.reference','value':subject or ref('artifact')},
             {'label':'private-notes','schema_id':'example.note','value':'PRIVATE-FIXTURE-NOT-TO-DISCLOSE'}]
    private=make(entries,salts=['11'*32,'22'*32]);view=select(private,['artifact'])
    return bundle('cmba.disclosure',view,parameters={'expected_disclosure_root':private['header']['disclosure_root'],'required_labels':['artifact']})


def observation():
    from .provenance import measure_bytes
    k=fixture_key(4);inst=ref('instrument');method=ref('sha256-method');cal=ref('calibration')
    r=measure_bytes(b'local supplied bytes',instrument=inst,method=method,calibration=cal,jurisdiction='lab')
    evidence=[seal('observation',{'record_hash':hash_value('observation',r),'decision':'confirm','not_before':0,'not_after':200},k)]
    return bundle('cmba.observation',r,parameters={'expected_instrument':inst,'expected_method':method,
       'expected_calibration':cal,'require_observer':True},authorities=authority([(k,['observer'],['lab'])]),evidence=evidence)


def execution():
    k=fixture_key(5);request={'artifact':ref('artifact'),'configuration':{'mode':'read'},'target':'example.host','operation':'inspect'}
    result=b'ok';r={'request':request,'observed':clone(request),'result_hex':result.hex(),
       'result':reference('sha256.bytes',hashlib.sha256(result).hexdigest()),'jurisdiction':'operations'}
    ev=seal('execution-observation',{'record_hash':hash_value('execution-record',r),'observed_at':90,'decision':'confirm','not_before':0,'not_after':200},k)
    return bundle('cmba.execution-record',r,parameters={'max_age':20},authorities=authority([(k,['execution-observer'],['operations'])]),evidence=[ev])


def coordination():
    from .coordination import terms_hash
    keys=[fixture_key(6),fixture_key(7)]
    r={'subject':ref('artifact'),'terms':{'operation':'review','cost':0},'participants':[public_key(k) for k in keys],
       'jurisdiction':'review','rounds':[]}
    th=terms_hash(r);previous=None
    for phase in (0,1):
        statements=[seal('coordination',{'terms_hash':th,'phase':phase,'previous_round_hash':previous,
           'decision':'agree','not_before':0,'not_after':200},k) for k in keys]
        round_={'phase':phase,'previous_round_hash':previous,'statements':statements};r['rounds'].append(round_)
        previous=hash_value('coordination-round',round_)
    return bundle('cmba.coordination',r,parameters={'required_phase':1},authorities=authority([(k,['participant'],['review']) for k in keys]))


def reconciliation():
    from .reconciliation import reconcile
    snapshots=[{'id':'a','values':{'stable':1,'conflict':'a','gone':None}}, {'id':'b','values':{'stable':1,'conflict':'b'}}]
    r={'snapshots':snapshots,'rule':{'id':'equal-or-conflict','version':1},'proposed':reconcile(snapshots)}
    return bundle('cmba.reconciliation',r)


def trace():
    s=session()['values']['record']
    return bundle('cmba.claim-trace',{'session':s,'claims':[{'id':'claim','text':'Claim interpretation not proved here','event_refs':['decision']}]})


def endorsement():
    k=fixture_key(8)
    p={'schema':'cmba.endorsement-policy.j1','requirements':[{'id':'release','role':'publisher','jurisdiction':'project','action':'publish','threshold':1}]}
    values={'object':{'label':'demo'},'endorsement-policy':p}
    b=bind(profile_reference(i_contract('cmba.generic')),[dimension('object','metadata','example.object',values['object'],critical=False),
       dimension('endorsement-policy','endorsement-requirements','cmba.endorsement-policy.j1',p,critical=False)])
    sig=endorse(b,values,k,requirement_id='release',not_before=0,not_after=200)
    return bundle('cmba.endorsements',{'binding':b,'values':values},parameters={'expected_subject_root':b['binding_root'],
         'expected_endorsement_policy_hash':hash_value('endorsement-policy',p)},authorities=authority([(k,['publisher'],['project'])]),evidence=[sig])


def admissibility(subject=None):
    subject=subject or ref('artifact');children={'approval':kasd(subject),'consent':consent(subject)}
    record={'subject':subject,'assessments':[{'id':k,'binding':v['binding'],'values':v['values']} for k,v in children.items()]}
    return bundle('cmba.admissibility',record,parameters={'child_contexts':{k:v['context'] for k,v in children.items()}})


def native():
    from ..profiles.dkn import load_native
    n=load_native();raw,m=n.pack({'sample.txt':b'example'},[])
    return bundle('cmba.native-dkn',{'operation':'archive','arguments':{'archive_hex':raw.hex(),'expected_root':m['logical_root'],'certificate':None}})


def all_bundles(include_native=True):
    funcs=[graph,session,kasd,consent,disclosure,observation,coordination,reconciliation,execution,trace,endorsement,admissibility]
    if include_native:funcs.append(native)
    return {f()['binding']['body']['profile']['profile_id']:f() for f in funcs}


def joint_workflow():
    """Session → real transform → actual DKN bytes → approvals/consent → selective proof → assessment."""
    from ..profiles.dkn import load_native
    session_b=session();graph_b=graph();g=graph_b['values']['record'];output=g['nodes'][1]['text'].encode()
    n=load_native();archive,manifest=n.pack({'compiled.json':output,'session.txt':session_b['values']['record']['source']['text'].encode()},[])
    cert=n.certify(manifest,fixture_key(9))
    native_b=bind_archive(archive,expected_logical_root=manifest['logical_root'],certificate=cert)
    subject=reference('dkn.logical.v0.2-candidate',manifest['logical_root'])
    a=admissibility(subject);d=disclosure(subject)
    bundles=[session_b,graph_b,a,d]
    receipts=[assess(b) for b in bundles]
    for b,r in zip(bundles,receipts):replay(r,b['binding'],b['values'],b['context'])
    later=clone(a['context']);later['time']['epoch']=250
    for child in later['policy']['parameters']['child_contexts'].values():child['time']['epoch']=250
    expired=evaluate(a['binding'],a['values'],later)
    # A signed-but-wrong transformation is still a consistent binding; actual predicate detects it.
    wrong=clone(graph_b['values']['record']);wrong['nodes'][1]['text']='wrong';wrong['nodes'][1]['sha256']=hashlib.sha256(b'wrong').hexdigest()
    bad=bundle('cmba.chc.graph',wrong);bad_result=assess(bad)
    return {'schema':'cmba.joint-demo.j1','fixture':'PUBLIC_TEST_KEYS_NOT_PRODUCTION',
       'session_root':session_b['binding']['binding_root'],'transformation_root':graph_b['binding']['binding_root'],
       'native_dkn_root':manifest['logical_root'],'cmba_dkn_wrapper_root':native_b['binding']['binding_root'],
       'disclosed_subject':d['values']['record']['openings'][0]['leaf']['value'],
       'initial_statuses':[r['body']['result']['status'] for r in receipts],
       'later_status':expired['body']['result']['status'],'same_assessment_object':a['binding']['binding_root']==expired['body']['binding_root'],
       'wrong_output_status':bad_result['body']['result']['status'],'receipts':[r['receipt_hash'] for r in receipts],
       'private_content_in_public_view':'PRIVATE-FIXTURE' in canonical(d).decode(),
       'authority_effect':'NONE'}
