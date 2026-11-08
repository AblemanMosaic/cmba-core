"""Finite, data-only workbench views; no interpretation of file-supplied code."""
from importlib.resources import files
from cmba_core import canonical,decode,inspect
from cmba_core.codec import clone
from cmba_core.bindings import exact,hex_digest,reference,profile_reference
from cmba_core.errors import require
from cmba_core.j1 import registry,disclosure
from .common import hash_value,integer,no_effect

DESIGN_FIELDS={
 'topology':['object','acyclic-graph','cyclic-consensus'],
 'granularity':['object','bounded-records','unbounded-stream'],
 'disclosure':['full','salted-inclusion','encrypted-private'],
 'anchor':['reader-pin','recognized-endorsements','popularity'],
 'time':['supplied-snapshot','finite-validity','globally-current'],
 'amendment':['new-root','lifecycle-f1','silent-rewrite']}

def design(configuration):
    exact(configuration,set(DESIGN_FIELDS))
    for k,choices in DESIGN_FIELDS.items():require(configuration[k] in choices,'CMBA_K_DESIGN_VALUE')
    unsupported=[];mechanisms=['CMBA I1 typed binding'];obligations=['Independent acquisition of intended root','Check application predicates, not only commitments']
    for k,bad in [('topology','cyclic-consensus'),('granularity','unbounded-stream'),('disclosure','encrypted-private'),
                  ('anchor','popularity'),('time','globally-current'),('amendment','silent-rewrite')]:
        if configuration[k]==bad:unsupported.append(k+':'+bad)
    if configuration['topology']=='acyclic-graph':mechanisms.append('AP-J1 finite transformation graph')
    if configuration['disclosure']=='salted-inclusion':
        mechanisms.append('SD-J1 selected openings');obligations.append('Protect undisclosed values and salts separately; no encryption/unlinkability claim')
    if configuration['anchor']=='recognized-endorsements':
        mechanisms.append('SE-J1 detached statements');obligations.append('Recognize issuer roles independently; provision real keys')
    if configuration['time']=='finite-validity':obligations.append('Provide accepted clock and sufficiently current evidence')
    if configuration['amendment']=='lifecycle-f1':
        mechanisms.append('Optional pinned native DKN LC-F1');obligations.append('Precommit recovery policy and respect the finite journal bound')
    body={'schema':'cmba.design-blueprint.k1','selection':clone(configuration),
      'status':'UNSUPPORTED_COMBINATION' if unsupported else 'SUPPORTED_COMPONENTS_NOT_DEPLOYMENT_QUALIFIED',
      'unsupported':unsupported,'mechanisms':mechanisms,'evidence_obligations':obligations,
      'registration':'NOT_REGISTERED','security_score':'NOT_COMPUTED','authority_effect':'NONE'}
    return {'body':body,'blueprint_hash':hash_value('design',body)}

def capabilities():
    from cmba_core.registry import capability_descriptors
    return capability_descriptors()+registry.capabilities()+[
      {'capability_id':'cmba.workbench.export','effect_class':'EXPLICIT_HOST_LOCAL_WRITE',
       'input':'displayed plan + host-only approval object','network':False,'subprocess':False,
       'authority_effect':'NONE','boundary':'NOT_CALLABLE_FROM_JSON_ABI'}]

def catalogue():return decode(files('cmba_core').joinpath('data/j1-catalogue.json').read_bytes())

def matrix(receipt):
    exact(receipt,{'schema','body','receipt_hash'});result=receipt['body']['result']
    require(type(result) is dict and type(result.get('checks')) is dict,'CMBA_K_RECEIPT_BODY')
    rows=[{'predicate':k,'outcome':v} for k,v in sorted(result['checks'].items())]
    return no_effect({'status':result['status'],'rows':rows,'details':clone(result.get('details',{})),
      'interpretation':'DISPLAY_OF_RECEIPT_REPLAY_REQUIRED_FOR_IMPORTED_DATA','authorization':result.get('authorization','NOT_ESTABLISHED')})

def preview_disclosure(private,labels, *, expected_root):
    # Verify ALL openings before selecting; unrelated broken material is not hidden.
    disclosure.verify(private,expected_root=expected_root)
    view=disclosure.select(private,labels);report=disclosure.verify(view,expected_root=expected_root)
    return no_effect({'schema':'cmba.disclosure-preview.k1','view':view,'report':report,
        'export_contains_only_selected_openings':True,'private_source_included':False})

def handoff(target,bundle, *, receipt_packet=None):
    require(target in ('dkn','ccp','ucm','pippi','courthouse'),'CMBA_K_HANDOFF_TARGET')
    from .session import admit_bundle,engine,Workspace
    admit_bundle(bundle)
    if receipt_packet is not None:
        exact(receipt_packet, {'schema','document_id','bundle','context','context_source','receipt'})
        require(receipt_packet['schema']=='cmba.receipt-packet.k1','CMBA_K_RECEIPT_PACKET')
        row={k:v for k,v in receipt_packet.items() if k!='schema'};Workspace._validate_history(row)
        require(canonical(receipt_packet['bundle'])==canonical(bundle),'CMBA_K_HANDOFF_SUBJECT')
        b=receipt_packet['bundle'];engine(b).replay(receipt_packet['receipt'],b['binding'],b['values'],receipt_packet['context'])
    body={'schema':'cmba.integration-handoff-body.k1','target':target,
       'binding':reference('cmba.binding',bundle['binding']['binding_root']),
       'document_hash':hash_value('document',bundle),'profile':clone(bundle['binding']['body']['profile']),
       'receipt_hash':None if receipt_packet is None else receipt_packet['receipt']['receipt_hash'],
       'included_material':'REFERENCES_ONLY','operational_integration':'NOT_ESTABLISHED','decision':'EXTERNAL_DECISION_REQUIRED',
       'authority_effect':'NONE','network_effect':'NONE'}
    return {'schema':'cmba.integration-handoff.k1','body':body,'handoff_hash':hash_value('handoff',body)}

def qualification(left,right):
    fields={'semantic_commitment','realization_sha256','corpus_sha256','claimed_results'}
    for v in (left,right):
        exact(v,fields)
        for k in ('semantic_commitment','realization_sha256','corpus_sha256'):hex_digest(v[k])
        require(type(v['claimed_results']) is dict,'CMBA_K_QUALIFICATION_DECLARATION')
        canonical(v)
    return no_effect({'schema':'cmba.realization-comparison.k1',
       'same_declared_contract':left['semantic_commitment']==right['semantic_commitment'],
       'same_realization':left['realization_sha256']==right['realization_sha256'],
       'same_corpus':left['corpus_sha256']==right['corpus_sha256'],
       'same_claimed_results':canonical(left['claimed_results'])==canonical(right['claimed_results']),
       'verification':'DECLARATION_COMPARISON_ONLY','conformance':'NOT_EXECUTED','replacement_approval':'EXTERNAL_DECISION_REQUIRED',
       'equivalence':'NOT_ESTABLISHED'})


def compare_receipts(left,right):
    """Recompute both supplied receipts, then expose input/result differences, not causality."""
    from .session import Workspace,engine
    for p in (left,right):
        exact(p,{'schema','document_id','bundle','context','context_source','receipt'})
        require(p['schema']=='cmba.receipt-packet.k1','CMBA_K_RECEIPT_PACKET')
        Workspace._validate_history({k:v for k,v in p.items() if k!='schema'})
        b=p['bundle'];engine(b).replay(p['receipt'],b['binding'],b['values'],p['context'])
    a=left['receipt']['body'];b=right['receipt']['body']
    fields=['binding_root','profile','supplied_values_hash','policy_hash','authority_snapshot_hash',
            'evidence_snapshot_hash','time_hash','evaluator']
    return no_effect({'schema':'cmba.receipt-comparison.k1',
        'changed_inputs':[k for k in fields if canonical(a.get(k))!=canonical(b.get(k))],
        'same_binding':a['binding_root']==b['binding_root'],
        'left_result':clone(a['result']),'right_result':clone(b['result']),
        'verification':'BOTH_REPLAYED_CURRENT_RUNTIME','causal_explanation':'NOT_INFERRED_FROM_HASH_DIFFERENCES'})


def installed_qualification():
    import hashlib
    from cmba_core.evaluation import realization_identity
    material=decode(files('cmba_workbench.k1').joinpath('data/qualification.json').read_bytes())
    material['installed_core_realization_sha256']=realization_identity()
    material['authentication']='NOT_ESTABLISHED_BY_SELF_HASH'
    material['qualification']='CONFORMANCE_REQUIRES_EXPLICIT_REPLAY_NOT_THIS_VIEW'
    return material
