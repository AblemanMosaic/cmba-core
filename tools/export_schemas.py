"""Explicit schema authoring; schemas describe shape, not cryptographic correctness."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def obj(props,required=None):
    return {'type':'object','properties':props,'required':list(props) if required is None else required,'additionalProperties':False}
def const(v):return {'const':v}
def ref(k):return {'$ref':'#/$defs/'+k}
def arr(v,max_items=1024,min_items=0):return {'type':'array','items':v,'maxItems':max_items,'minItems':min_items}
ID={'type':'string','pattern':'^[a-z][a-z0-9._:/-]{0,191}$'}
HEX={'type':'string','pattern':'^[0-9a-f]{64}$'}
S={'type':'string'};B={'type':'boolean'}
D={}
D['profile-reference']=obj({'profile_id':ID,'profile_version':ID,'contract_hash':HEX})
D['reference']=obj({'scheme':ID,'algorithm':{'enum':['SHA-256','BLAKE3-256']},'digest_hex':HEX})
D['dimension']=obj({'dimension_id':ID,'role':ID,'schema_id':ID,'codec':const('cmba-cjson-i1'),
                    'algorithm':const('SHA-256'),'critical':B,'value_hash':HEX})
D['relation']=obj({'relation_id':ID,'predicate':ID,'target':ref('reference')})
D['binding-body']=obj({'schema':const('cmba.binding-body.v0.1-i1'),'profile':ref('profile-reference'),
                       'dimensions':arr(ref('dimension'),64,1),'relations':arr(ref('relation'),256)})
D['binding']=obj({'schema':const('cmba.binding.v0.1-i1'),'body':ref('binding-body'),'binding_root':HEX})
D['context']=obj({'schema':const('cmba.evaluation-context.v0.1-i1'),'expected_binding_root':HEX,
  'policy':obj({'profile':ref('profile-reference'),'required_checks':arr(ID,64)}),
  'authority_snapshot':{'type':'object'},'evidence_snapshot':arr({}),
  'time':obj({'epoch':{'type':'integer','minimum':0,'maximum':2**63-1},'clock_source':ID})})
D['result']=obj({'schema':const('cmba.evaluation-result.v0.1-i1'),
 'status':{'enum':['MATCH_FOR_SUPPLIED_EVIDENCE','CONTRADICTED','INSUFFICIENT','UNSUPPORTED']},
 'checks':{'type':'object','additionalProperties':{'enum':['MATCH','CONTRADICTED','UNSUPPORTED','NOT_CHECKED']}},
 'missing_dimensions':arr(ID,64),'missing_values':arr(ID,64),'unsupported_critical_dimensions':arr(ID,64),
 'uninterpreted_dimensions':arr(ID,64),'authority_effect':const('NONE'),
 'authority_interpretation':const('NOT_EVALUATED'),'evidence_interpretation':const('NOT_EVALUATED'),
 'authorization':const('EXTERNAL_DECISION_REQUIRED'),'claim_ceiling':S})
D['receipt-body']=obj({'schema':const('cmba.evaluation-receipt-body.v0.1-i1'),'binding_root':HEX,'profile':ref('profile-reference'),
 'supplied_values_hash':HEX,'policy_hash':HEX,'authority_snapshot_hash':HEX,'evidence_snapshot_hash':HEX,
 'time_hash':HEX,'expected_binding_root':HEX,
 'evaluator':obj({'id':const('cmba.builtin-evaluator.i1'),'realization_sha256':HEX}),
 'result':ref('result'),'signature':const('NOT_SIGNED')})
D['receipt']=obj({'schema':const('cmba.evaluation-receipt.v0.1-i1'),'body':ref('receipt-body'),'receipt_hash':HEX})
D['bundle']=obj({'schema':const('cmba.workbench-bundle.v0.1-i1'),'binding':ref('binding'),'values':{'type':'object'},'context':ref('context')})
D['request']=obj({'schema':const('cmba.request.v0.1-i1'),'operation':{'enum':['inspect','compare','evaluate','replay','catalogue','capabilities']},'arguments':{'type':'object'}})
# Operation-dependent argument closure is enforced below as well as at runtime.
arg={'inspect':obj({'binding':ref('binding'),'values':{'type':'object'},'expected_root':{'anyOf':[HEX,{'type':'null'}]}}),
 'compare':obj({'left':ref('binding'),'right':ref('binding')}),
 'evaluate':obj({'binding':ref('binding'),'values':{'type':'object'},'context':ref('context')}),
 'replay':obj({'receipt':ref('receipt'),'binding':ref('binding'),'values':{'type':'object'},'context':ref('context')}),
 'catalogue':obj({}),'capabilities':obj({})}
D['request']['allOf']=[{'if':{'properties':{'operation':const(k)}},'then':{'properties':{'arguments':v}}} for k,v in arg.items()]
D['profile-contract']=obj({'schema':const('cmba.profile-contract.v0.1-i1'),'profile_id':ID,'profile_version':ID,'title':S,
 'required_dimensions':arr(obj({'dimension_id':ID,'role':ID,'schema_id':ID}),64),'predicates':arr(ID,64,1),
 'unknown_critical':const('UNSUPPORTED'),'unknown_noncritical':const('PRESERVE_WITHOUT_INTERPRETATION'),
 'authority_effect':const('NONE'),'claim_ceiling':S})
D['capability']=obj({'schema':const('cmba.capability.v0.1-i1'),'capability_id':ID,'profile':ref('profile-reference'),
 'inputs':S,'effect_class':const('PURE_READ'),'requires_host_selection':const(True),
 'network':const(False),'subprocess':const(False),'auto_install':const(False),'authority_effect':const('NONE'),'claim_ceiling':S})


def build():
    names=('binding','dimension','reference','profile-contract','context','result','receipt','bundle','request','capability')
    return {name:{'$schema':'https://json-schema.org/draft/2020-12/schema',
                  '$id':'urn:cmba:i1:'+name,'$ref':'#/$defs/'+name,'$defs':D} for name in names}

if __name__=='__main__':
    for name,schema in build().items():
        (ROOT/'schemas'/f'{name}.schema.json').write_text(json.dumps(schema,sort_keys=True,indent=2)+'\n')
    print(len(build()),'schemas exported')
