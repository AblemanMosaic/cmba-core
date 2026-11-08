"""Bounded in-memory workbench. Reading never adopts a document's recognition policy.

Evaluation tasks use immutable snapshots. Imported history is unverified until replay.
File operations live in effects.py, not here or in application evaluators.
"""
from __future__ import annotations
from dataclasses import dataclass
from cmba_core import canonical, decode, inspect, compare
from cmba_core.codec import clone
from cmba_core.bindings import exact, hex_digest, validate_reference
from cmba_core.errors import require, Refusal
from cmba_core import evaluation as i_eval
from cmba_core.j1 import evaluation as j_eval
from cmba_core.j1.registry import contracts, resolve
from cmba_core.registry import resolve_profile
from .common import *

BUNDLE_I='cmba.workbench-bundle.v0.1-i1'
BUNDLE_J='cmba.workbench-bundle.j1'


def admit_bundle(bundle):
    canonical(bundle); exact(bundle, {'schema','binding','values','context'})
    require(bundle['schema'] in (BUNDLE_I,BUNDLE_J), 'CMBA_K_BUNDLE_SCHEMA')
    # Unknown profiles may be inspected; their evaluator is never inferred or imported.
    result=inspect(bundle['binding'],bundle['values'])
    require(type(bundle['context']) is dict,'CMBA_K_DOCUMENT_CONTEXT')
    return result


def engine(bundle):
    return j_eval if bundle['schema']==BUNDLE_J else i_eval


def validate_reader(bundle,context):
    canonical(context)
    if bundle['schema']==BUNDLE_J:
        j_eval.validate_context(context, resolve(bundle['binding']['body']['profile']))
    else:
        i_eval._context(context,resolve_profile(bundle['binding']['body']['profile']))
    require(context['expected_binding_root']==bundle['binding']['binding_root'],'CMBA_EXPECTED_ROOT_MISMATCH')


def execute_task(task):
    """Pure computation; safe to run off the Tk thread. No host file operations."""
    exact(task, {'schema','task_hash','body'})
    require(task['schema']=='cmba.workbench-task.k1','CMBA_K_TASK_SCHEMA')
    require(hash_value('task',task['body'])==task['task_hash'],'CMBA_K_TASK_HASH')
    body=task['body'];exact(body, {'generation','document_id','bundle','reader_context','context_source'})
    admit_bundle(body['bundle']);validate_reader(body['bundle'],body['reader_context'])
    b=body['bundle'];receipt=engine(b).evaluate(b['binding'],b['values'],body['reader_context'])
    return {'task_hash':task['task_hash'],'receipt':receipt}


@dataclass(frozen=True)
class _VerifiedEvaluation:
    """Host-only result of computation and replay; never deserialized from input."""
    raw: bytes


def execute_verified_task(task):
    result=execute_task(task);b=task['body']['bundle']
    engine(b).replay(result['receipt'],b['binding'],b['values'],task['body']['reader_context'])
    return _VerifiedEvaluation(canonical(result))


class Workspace:
    """Single-controller bounded RAM state; snapshots are data, never trust stores."""
    def __init__(self):
        self._documents={};self._history=[];self._selected=None;self._context=None
        self._context_source='NOT_SELECTED';self._generation=0;self._pending=None;self._last=None
        self._replayed=set()

    def _clear(self):
        self._generation+=1;self._selected=None;self._context=None
        self._context_source='NOT_SELECTED';self._pending=None;self._last=None

    def _changed(self):
        self._generation+=1;self._pending=None;self._last=None

    def load(self,bundle, *, name='Imported binding'):
        self._clear()
        label(name);admit_bundle(bundle)
        did=hash_value('document',bundle)
        require(did in self._documents or len(self._documents)<MAX_DOCUMENTS,'CMBA_K_DOCUMENT_LIMIT')
        row={'document_id':did,'label':name,'bundle':clone(bundle)}
        proposed=dict(self._documents);proposed[did]=row
        # Bound total persisted state BEFORE committing it to live state.
        canonical({'documents':list(proposed.values()),'history':self._history})
        self._documents=proposed;self._selected=did
        return {'document_id':did,'inspection':self.inspection(),'context':'NOT_SELECTED','authority_effect':'NONE'}

    def load_raw(self,raw, *, name='Imported binding'):
        self._clear()
        return self.load(decode(raw),name=name)

    def select(self,did):
        self._clear();hex_digest(did)
        require(did in self._documents,'CMBA_K_DOCUMENT_MISSING')
        self._selected=did
        return self.inspection()

    def selected(self):
        require(self._selected in self._documents,'CMBA_NO_SELECTION')
        return clone(self._documents[self._selected]['bundle'])

    def documents(self):
        return [{'document_id':d,'label':r['label'],'root':r['bundle']['binding']['binding_root'],
                 'profile':r['bundle']['binding']['body']['profile']} for d,r in self._documents.items()]

    def inspection(self):
        b=self.selected();return inspect(b['binding'],b['values'])

    def set_reader_context(self,context, *, source='READER_SELECTED'):
        self._context=None;self._context_source='NOT_SELECTED';self._changed()
        require(source in ('READER_SELECTED','DOCUMENT_DEMO_UNTRUSTED'),'CMBA_K_CONTEXT_SOURCE')
        validate_reader(self.selected(),context)
        self._context=clone(context);self._context_source=source
        return {'status':'CONTEXT_SELECTED_NOT_AUTHENTICATED','source':source,'authority_effect':'NONE'}

    def use_demo_context(self):
        return self.set_reader_context(self.selected()['context'],source='DOCUMENT_DEMO_UNTRUSTED')

    def context(self):
        require(self._context is not None,'CMBA_READER_CONTEXT_REQUIRED')
        return clone(self._context)

    def state_binding(self):
        return hash_value('workspace',{'generation':self._generation,'selected':self._selected,
          'context':self._context,'source':self._context_source,
          'documents':sorted(self._documents),'history':[x['receipt']['receipt_hash'] for x in self._history]})

    def prepare_evaluation(self):
        self._last=None;self._pending=None
        require(self._context is not None,'CMBA_READER_CONTEXT_REQUIRED')
        body={'generation':self._generation,'document_id':self._selected,'bundle':self.selected(),
              'reader_context':self.context(),'context_source':self._context_source}
        task={'schema':'cmba.workbench-task.k1','body':body,'task_hash':hash_value('task',body)}
        self._pending=clone(task);return clone(task)

    def accept_result(self,result):
        return self._accept(result,verified=False)

    def accept_verified(self,host_result):
        require(type(host_result) is _VerifiedEvaluation,'CMBA_K_HOST_RESULT_REQUIRED')
        return self._accept(decode(host_result.raw),verified=True)

    def _accept(self,result, *, verified):
        exact(result, {'task_hash','receipt'})
        require(self._pending is not None and self._pending['task_hash']==result['task_hash'], 'CMBA_K_STALE_RESULT')
        task=self._pending;self._pending=None;body=task['body']
        require(self._generation==body['generation'] and self._selected==body['document_id'],'CMBA_K_STALE_RESULT')
        # A received result is a claim, not a trust anchor. Replay even the host task's result.
        b=body['bundle']
        if not verified:engine(b).replay(result['receipt'],b['binding'],b['values'],body['reader_context'])
        require(len(self._history)<MAX_HISTORY,'CMBA_K_HISTORY_LIMIT')
        row={'document_id':body['document_id'],'bundle':b,'context':body['reader_context'],
             'context_source':body['context_source'],'receipt':clone(result['receipt'])}
        canonical({'documents':list(self._documents.values()),'history':self._history+[row]})
        self._history.append(row);self._last=len(self._history)-1;self._replayed.add(self._last)
        # invalidate any prepared local effect after an assessment changes displayed state
        self._generation+=1
        return clone(result['receipt'])

    def evaluate(self):
        return self.accept_result(execute_task(self.prepare_evaluation()))

    def cancel(self):
        self._pending=None;self._last=None;self._generation+=1

    def history(self):
        return [{'index':i,'binding_root':r['receipt']['body']['binding_root'],
          'receipt_hash':r['receipt']['receipt_hash'],'status':r['receipt']['body']['result']['status'],
          'assessment_time':r['context']['time'],'context_source':r['context_source'],
          'verification':'REPLAYED_CURRENT_RUNTIME' if i in self._replayed else 'IMPORTED_NOT_REPLAYED'}
          for i,r in enumerate(self._history)]

    def receipt_packet(self,index=None):
        index=self._last if index is None else index
        require(type(index) is int and 0<=index<len(self._history),'CMBA_NO_RECEIPT')
        return {'schema':'cmba.receipt-packet.k1',**clone(self._history[index])}

    def replay_history(self,index):
        p=self.receipt_packet(index);b=p['bundle']
        report=engine(b).replay(p['receipt'],b['binding'],b['values'],p['context'])
        self._replayed.add(index);return report

    def import_receipt(self,packet):
        exact(packet, {'schema','document_id','bundle','context','context_source','receipt'})
        require(packet['schema']=='cmba.receipt-packet.k1','CMBA_K_RECEIPT_PACKET')
        row={k:v for k,v in packet.items() if k!='schema'}
        self._validate_history(row)
        require(len(self._history)<MAX_HISTORY,'CMBA_K_HISTORY_LIMIT')
        canonical({'documents':list(self._documents.values()),'history':self._history+[row]})
        self._history.append(clone(row));self._changed()
        return {'status':'IMPORTED_NOT_REPLAYED','index':len(self._history)-1,'authority_effect':'NONE'}

    @staticmethod
    def _validate_history(r):
        exact(r, {'document_id','bundle','context','context_source','receipt'})
        admit_bundle(r['bundle']);require(r['document_id']==hash_value('document',r['bundle']),'CMBA_K_DOCUMENT_ID')
        require(r['context_source'] in ('READER_SELECTED','DOCUMENT_DEMO_UNTRUSTED'),'CMBA_K_CONTEXT_SOURCE')
        validate_reader(r['bundle'],r['context']);exact(r['receipt'], {'schema','body','receipt_hash'})
        body=r['receipt']['body'];require(type(body) is dict and type(body.get('result')) is dict,'CMBA_K_RECEIPT_BODY')
        require(type(body['result'].get('status')) is str,'CMBA_K_RECEIPT_BODY')
        require(body.get('binding_root')==r['bundle']['binding']['binding_root'],'CMBA_K_RECEIPT_SUBJECT')
        hex_digest(r['receipt']['receipt_hash'])
        # It is deliberately still unverified: only replay can establish the claimed result.

    def snapshot(self):
        result={'schema':'cmba.workspace.k1','documents':clone(list(self._documents.values())),
          'history':clone(self._history),'trust_state':'NOT_SERIALIZED','authority_effect':'NONE'}
        canonical(result);return result

    def restore(self,value):
        self._clear()
        canonical(value);exact(value, {'schema','documents','history','trust_state','authority_effect'})
        require(value['schema']=='cmba.workspace.k1' and value['trust_state']=='NOT_SERIALIZED'
                and value['authority_effect']=='NONE','CMBA_K_WORKSPACE_SCHEMA')
        require(type(value['documents']) is list and len(value['documents'])<=MAX_DOCUMENTS,'CMBA_K_DOCUMENT_LIMIT')
        require(type(value['history']) is list and len(value['history'])<=MAX_HISTORY,'CMBA_K_HISTORY_LIMIT')
        docs={}
        for row in value['documents']:
            exact(row, {'document_id','label','bundle'});label(row['label']);admit_bundle(row['bundle'])
            did=hash_value('document',row['bundle']);require(did==row['document_id'] and did not in docs,'CMBA_K_DOCUMENT_ID')
            docs[did]=clone(row)
        for row in value['history']:self._validate_history(row)
        self._documents=docs;self._history=clone(value['history']);self._replayed=set()
        return {'status':'WORKSPACE_RESTORED_WITHOUT_TRUST','documents':len(docs),'history':len(self._history),'authority_effect':'NONE'}

    def compare_documents(self,left,right):
        require(left in self._documents and right in self._documents,'CMBA_K_DOCUMENT_MISSING')
        a=self._documents[left]['bundle'];b=self._documents[right]['bundle']
        result=compare(a['binding'],b['binding'])
        result['same_document_context']=canonical(a['context'])==canonical(b['context'])
        result['same_supplied_values']=canonical(a['values'])==canonical(b['values'])
        return result

    def navigate(self, *, max_nodes=32,max_edges=128):
        integer(max_nodes,1,MAX_DOCUMENTS);integer(max_edges,1,MAX_EDGES)
        # Finite complete scan of the admitted local collection. All nodes are re-inspected.
        rows=list(self._documents.items());nodes=[];edges=[];unresolved=[];edge_count=0
        roots={r['bundle']['binding']['binding_root'] for _,r in rows}
        for did,row in rows:
            b=row['bundle'];admit_bundle(b)
            if len(nodes)<max_nodes:nodes.append({'document_id':did,'root':b['binding']['binding_root'],'label':row['label']})
            for rel in b['binding']['body']['relations']:
                edge_count+=1
                if len(edges)>=max_edges:continue
                t=rel['target'];local=t['scheme']=='cmba.binding' and t['algorithm']=='SHA-256' and t['digest_hex'] in roots
                edge={'source':b['binding']['binding_root'],'relation':clone(rel),'target_status':'PRESENT_LOCALLY' if local else 'NOT_RESOLVED',
                      'truth':'NOT_ESTABLISHED','target_validation':'LOCAL_COMMITMENT_ONLY' if local else 'NOT_CHECKED'}
                edges.append(edge)
                if not local:unresolved.append(clone(t))
        visible={n['root'] for n in nodes}
        for e in edges:e['target_visible']=e['relation']['target']['digest_hex'] in visible and e['target_status']=='PRESENT_LOCALLY'
        out={'schema':'cmba.local-graph.k1','nodes':nodes,'edges':edges,'unresolved':unresolved,
          'total_local_documents':len(rows),'total_declared_edges':edge_count,
          'node_limited':len(rows)>max_nodes,'edge_limited':edge_count>max_edges,
          'truncated':len(rows)>max_nodes or edge_count>max_edges,'scope':'ADMITTED_LOCAL_COLLECTION_ONLY',
          'completeness':'NOT_GLOBAL','authority_effect':'NONE'}
        canonical(out);return out
