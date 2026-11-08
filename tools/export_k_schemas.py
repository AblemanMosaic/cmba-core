"""Author K1 structural schemas. Runtime cryptographic/policy checks remain necessary."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cmba_core import canonical


def obj(properties):return {'type':'object','required':list(properties),'properties':properties,'additionalProperties':False}
def const(v):return {'const':v}
D={'type':'string','pattern':'^[0-9a-f]{64}$'};S={'type':'string'};O={'type':'object'};N={'type':'integer','minimum':0};B={'type':'boolean'}
def arr(items,limit=128):return {'type':'array','items':items,'maxItems':limit}


def build():
    bundle=obj({'schema':{'enum':['cmba.workbench-bundle.v0.1-i1','cmba.workbench-bundle.j1']},'binding':O,'values':O,'context':O})
    history=obj({'document_id':D,'bundle':bundle,'context':O,'context_source':{'enum':['READER_SELECTED','DOCUMENT_DEMO_UNTRUSTED']},'receipt':O})
    packet=obj({'schema':const('cmba.receipt-packet.k1'),**history['properties']})
    workspace=obj({'schema':const('cmba.workspace.k1'),'documents':arr(obj({'document_id':D,'label':{'type':'string','minLength':1,'maxLength':128},'bundle':bundle}),64),
       'history':arr(history),'trust_state':const('NOT_SERIALIZED'),'authority_effect':const('NONE')})
    from cmba_workbench.k1.views import DESIGN_FIELDS
    design=obj({k:{'enum':v} for k,v in DESIGN_FIELDS.items()})
    q=obj({'semantic_commitment':D,'realization_sha256':D,'corpus_sha256':D,'claimed_results':O})
    operations={
      'inspect':{'bundle':bundle},'author':{'profile_id':S,'record':O,'now':N,'parameters':O,'relations':arr(O,256)},
      'evaluate':{'bundle':bundle,'reader_context':O},'replay':{'packet':packet},'compare':{'left':bundle,'right':bundle},
      'compare-receipts':{'left':packet,'right':packet},'navigate':{'workspace':workspace,'max_nodes':{'type':'integer','minimum':1,'maximum':64},'max_edges':{'type':'integer','minimum':1,'maximum':256}},
      'disclosure-preview':{'private':O,'labels':arr(S,64),'expected_root':D},'design':{'configuration':design},
      'qualification':{'left':q,'right':q},'handoff':{'target':{'enum':['dkn','ccp','ucm','pippi','courthouse']},'bundle':bundle,'receipt_packet':{'anyOf':[packet,{'type':'null'}]}},
      'capabilities':{},'catalogue':{},'installed-qualification':{}}
    request={'oneOf':[obj({'schema':const('cmba.workbench-request.k1'),'operation':const(op),'arguments':obj(args)}) for op,args in operations.items()]}
    planbody=obj({'schema':const('cmba.local-effect-plan-body.k1'),'kind':{'enum':['bundle','receipt','workspace','disclosure','handoff','design']},
      'operation':const('CREATE_ONLY_JSON'),'workspace':S,'target_name':S,'workspace_identity':{'type':'array','items':S,'minItems':2,'maxItems':2},
      'input_state':D,'output_sha256':D,'output_bytes':{'type':'integer','minimum':1,'maximum':1048576},
      'ttl_seconds':{'type':'integer','minimum':1,'maximum':300},'nonce':{'type':'string','pattern':'^[0-9a-f]{32}$'},
      'overwrite':const(False),'authority_effect':const('NONE'),'host_effect':const('CREATE_LOCAL_FILE'),'approval':const('HOST_CONFIRMATION_REQUIRED')})
    plan=obj({'schema':const('cmba.local-effect-plan.k1'),'body':planbody,'plan_hash':D})
    effect=obj({'schema':const('cmba.local-effect-receipt.k1'),'status':{'enum':['LOCAL_FILE_CREATED_AND_READ_BACK','LOCAL_FILE_CREATED_READBACK_INDETERMINATE']},
      'plan':plan,'output_sha256':D,'durability':S,'warnings':arr(S),'host_effect':const('CREATE_LOCAL_FILE'),
      'authority_effect':const('NONE'),'signature':const('NOT_SIGNED'),'claim_ceiling':S})
    result={'bundle':bundle,'workspace':workspace,'receipt-packet':packet,'request':request,'effect-plan':plan,'effect-receipt':effect,
      'task':obj({'schema':const('cmba.workbench-task.k1'),'task_hash':D,'body':obj({'generation':N,'document_id':D,'bundle':bundle,
           'reader_context':O,'context_source':{'enum':['READER_SELECTED','DOCUMENT_DEMO_UNTRUSTED']}})}),
      'design-selection':design,'qualification-declaration':q,
      'disclosure-preview':obj({'schema':const('cmba.disclosure-preview.k1'),'view':O,'report':O,
        'export_contains_only_selected_openings':const(True),'private_source_included':const(False),'authority_effect':const('NONE')}),
      'handoff':obj({'schema':const('cmba.integration-handoff.k1'),'body':O,'handoff_hash':D}),
      'local-graph':obj({'schema':const('cmba.local-graph.k1'),'nodes':arr(O,64),'edges':arr(O,256),'unresolved':arr(O,256),
        'total_local_documents':N,'total_declared_edges':N,'node_limited':B,'edge_limited':B,'truncated':B,
        'scope':const('ADMITTED_LOCAL_COLLECTION_ONLY'),'completeness':const('NOT_GLOBAL'),'authority_effect':const('NONE')})}
    return {name:{'$schema':'https://json-schema.org/draft/2020-12/schema',**schema} for name,schema in result.items()}

if __name__=='__main__':
    out=ROOT/'schemas/k1';out.mkdir(parents=True,exist_ok=True)
    for name,schema in build().items():(out/(name+'.schema.json')).write_text(json.dumps(schema,sort_keys=True,indent=2)+'\n')
    print('exported',len(build()),'K1 structural schemas; host approvals have NO data schema')
