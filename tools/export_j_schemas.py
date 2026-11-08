"""AUTHORING ONLY J1 shape schemas. Hashes, signatures and predicate conclusions need runtime checks."""
from pathlib import Path
from copy import deepcopy
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
from cmba_core import canonical
from export_schemas import obj,const,ref,arr,ID,HEX,S,B,D as I
N={'type':'integer','minimum':0,'maximum':2**63-1};JSON={};MAP={'type':'object'}
D={k:deepcopy(I[k]) for k in ('profile-reference','reference','dimension','relation','binding-body','binding')}
D['statement-body']=obj({'schema':const('cmba.statement-body.j1'),'kind':{'enum':['endorsement','approval','consent-grant','consent-withdrawal','coordination','observation','execution-observation']},
  'payload':MAP,'algorithm':const('Ed25519'),'public_key':HEX})
D['signed-statement']=obj({'schema':const('cmba.signed-statement.j1'),'body':ref('statement-body'),
  'signature_hex':{'type':'string','pattern':'^[0-9a-f]{128}$'},'record_hash':HEX})
D['authority']=obj({'members':arr(obj({'public_key':HEX,'roles':arr(ID,64),'jurisdictions':arr(ID,64)}),64),'revoked_keys':arr(HEX,64)})
D['context']=obj({'schema':const('cmba.evaluation-context.j1'),'expected_binding_root':HEX,
  'policy':obj({'profile':ref('profile-reference'),'required_checks':arr(ID,64),'parameters':MAP}),
  'authority_snapshot':ref('authority'),'evidence_snapshot':arr(ref('signed-statement'),64),
  'time':obj({'epoch':N,'clock_source':ID})})
D['result']=obj({'schema':const('cmba.application-result.j1'),
 'status':{'enum':['MATCH_FOR_SUPPLIED_EVIDENCE','CONTRADICTED','UNSUPPORTED','INSUFFICIENT','NO_MATCH','NATIVE_REPORT_COMPUTED']},
 'checks':{'type':'object','minProperties':1,'additionalProperties':{'enum':['MATCH','CONTRADICTED','UNSUPPORTED','INSUFFICIENT','NO_MATCH','NATIVE_REPORT_COMPUTED']}},
 'details':MAP,'claim_ceiling':S,'authority_effect':const('NONE'),'authorization':const('EXTERNAL_DECISION_REQUIRED'),
 'freshness':const('SUPPLIED_VIEW_ONLY'),'semantic_truth':const('NOT_ESTABLISHED'),'uninterpreted_dimensions':arr(ID,64)},
 required=['schema','status','checks','details','claim_ceiling','authority_effect','authorization','freshness','semantic_truth'])
D['receipt-body']=obj({'schema':const('cmba.application-receipt-body.j1'),'binding_root':HEX,'profile':ref('profile-reference'),
 'supplied_values_hash':HEX,'context_hash':HEX,'policy_hash':HEX,'authority_snapshot_hash':HEX,'evidence_snapshot_hash':HEX,
 'time_hash':HEX,'evaluator':obj({'id':const('cmba.applications.j1'),'realization_sha256':HEX}),
 'result':ref('result'),'signature':const('NOT_SIGNED')})
D['receipt']=obj({'schema':const('cmba.application-receipt.j1'),'body':ref('receipt-body'),'receipt_hash':HEX})
D['bundle']=obj({'schema':const('cmba.workbench-bundle.j1'),'binding':ref('binding'),'values':MAP,'context':ref('context')})
D['endorsement-policy']=obj({'schema':const('cmba.endorsement-policy.j1'),'requirements':arr(obj({
 'id':ID,'role':ID,'jurisdiction':ID,'action':ID,'threshold':{'type':'integer','minimum':1,'maximum':64}}),16,1)})
D['endorsed-envelope']=obj({'schema':const('cmba.endorsed-envelope.j1'),'body':obj({'schema':const('cmba.endorsed-envelope-body.j1'),
 'binding':ref('binding'),'values':MAP,'endorsements':arr(ref('signed-statement'),64)}),'envelope_hash':HEX})
D['disclosure-header']=obj({'schema':const('cmba.disclosure-header.j1'),'leaf_count':{'type':'integer','minimum':1,'maximum':64},
 'merkle_root':HEX,'disclosure_root':HEX})
D['disclosure-leaf']=obj({'schema':const('cmba.disclosure-leaf.j1'),'index':{'type':'integer','minimum':0,'maximum':63},
 'label':ID,'schema_id':ID,'value':JSON,'salt_hex':HEX})
D['disclosure-opening']=obj({'leaf':ref('disclosure-leaf'),'path':arr(obj({'side':{'enum':['left','right']},'hash':HEX}),6)})
D['record-disclosure']=obj({'header':ref('disclosure-header'),'openings':arr(ref('disclosure-opening'),64)})
D['record-graph']=obj({'nodes':arr(obj({'id':ID,'text':S,'sha256':HEX}),64,1),
 'steps':arr(obj({'id':ID,'inputs':arr(ID,16,1),'output':ID,'rule':obj({'id':ID,'version':N}),
 'toolchain':obj({'id':ID,'implementation_sha256':HEX})}),32,1),'outputs':arr(ID,64,1)})
D['session-event']=obj({'id':ID,'type':{'enum':['requirement','decision','alternative','uncertainty','trigger','output','claim']},
 'attributed_to':ID,'start_byte':N,'end_byte':N,'quote':S,'interpretation':S,'references':arr(ID,64)})
D['record-session']=obj({'source':obj({'text':S,'sha256':HEX,'coverage':const('SUPPLIED_RECORD_ONLY')}),
 'events':arr(ref('session-event'),64,1)})
D['record-trace']=obj({'session':ref('record-session'),'claims':arr(obj({'id':ID,'text':S,'event_refs':arr(ID,64,1)}),64,1)})
D['record-kasd']=obj({'subject':ref('reference'),'action':ID,'facts':MAP,
 'requirements':arr(obj({'id':ID,'role':ID,'jurisdiction':ID,'threshold':{'type':'integer','minimum':1,'maximum':64},'constraints':MAP}),16,1)})
D['record-consent']=obj({'subject':ref('reference'),'actor':ID,'action':ID,'jurisdiction':ID,'facts':MAP,'renewal_context':MAP})
D['record-observation']=obj({'subject':ref('reference'),'raw_hex':{'type':'string','pattern':'^(?:[0-9a-f]{2})*$','maxLength':131072},
 'measured_digest':HEX,'measured_size':{'type':'integer','minimum':0,'maximum':65536},
 'instrument':ref('reference'),'method':ref('reference'),'calibration':ref('reference'),'jurisdiction':ID,
 'measurement_type':const('SUPPLIED_BYTES_RECOMPUTED')})
D['record-coordination']=obj({'subject':ref('reference'),'terms':JSON,'participants':arr(HEX,16,1),'jurisdiction':ID,
 'rounds':arr(obj({'phase':{'type':'integer','minimum':0,'maximum':1},'previous_round_hash':{'anyOf':[HEX,{'type':'null'}]},
 'statements':arr(ref('signed-statement'),64)}),2,1)})
D['record-reconciliation']=obj({'snapshots':arr(obj({'id':ID,'values':{'type':'object','maxProperties':64}}),16,1),
 'rule':obj({'id':const('equal-or-conflict'),'version':const(1)}),'proposed':obj({'merged':MAP,'conflicts':MAP})})
D['execution-request']=obj({'artifact':ref('reference'),'configuration':JSON,'target':ID,'operation':ID})
D['record-execution']=obj({'request':ref('execution-request'),'observed':ref('execution-request'),
 'result_hex':{'type':'string','pattern':'^(?:[0-9a-f]{2})*$','maxLength':131072},'result':ref('reference'),'jurisdiction':ID})
D['record-admissibility']=obj({'subject':ref('reference'),'assessments':arr(obj({'id':ID,'binding':ref('binding'),'values':MAP}),8,1)})
D['record-endorsements']=obj({'binding':ref('binding'),'values':MAP})
D['record-native']=obj({'operation':{'enum':['archive','namespace','lineage','lifecycle','assurance','distributed']},'arguments':MAP})
args={'evaluate':obj({'binding':ref('binding'),'values':MAP,'context':ref('context')}),
      'replay':obj({'receipt':ref('receipt'),'binding':ref('binding'),'values':MAP,'context':ref('context')}),
      'profiles':obj({}),'capabilities':obj({}),'verify-statement':obj({'record':ref('signed-statement')}),
      'verify-envelope':obj({'envelope':ref('endorsed-envelope')}),
      'verify-disclosure':obj({'view':ref('record-disclosure'),'expected_root':HEX}),
      'dkn-read':obj({'request':ref('record-native')})}
D['request']=obj({'schema':const('cmba.request.j1'),'operation':{'enum':list(args)},'arguments':MAP})
D['request']['allOf']=[{'if':{'properties':{'operation':const(k)}},'then':{'properties':{'arguments':v}}} for k,v in args.items()]
NAMES=['signed-statement','authority','context','result','receipt','bundle','endorsement-policy','endorsed-envelope',
 'disclosure-header','disclosure-opening','record-disclosure','record-graph','record-session','record-trace','record-kasd',
 'record-consent','record-observation','record-coordination','record-reconciliation','record-execution',
 'record-admissibility','record-endorsements','record-native','request']


def build():
    # Export only transitive definitions used by each schema, avoiding repeated unrelated data.
    def deps(name):
        needed={name};todo=[name]
        def refs(v):
            if type(v) is dict:
                for k,x in v.items():
                    if k=='$ref':yield x.removeprefix('#/$defs/')
                    else:yield from refs(x)
            elif type(v) is list:
                for x in v:yield from refs(x)
        while todo:
            for key in refs(D[todo.pop()]):
                if key not in needed:needed.add(key);todo.append(key)
        return {k:D[k] for k in sorted(needed)}
    return {name:{'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:cmba:j1:'+name,
                  '$ref':'#/$defs/'+name,'$defs':deps(name)} for name in NAMES}

if __name__=='__main__':
    for name,schema in build().items():
        (ROOT/'schemas/j1'/f'{name}.schema.json').write_text(json.dumps(schema,sort_keys=True,indent=2)+'\n')
    (ROOT/'src/cmba_core/data/j1-schemas.json').write_bytes(canonical(build()))
    print('schemas',len(build()))
