"""One unchanged object, different supplied evidence times, explicit selective view."""
from copy import deepcopy
from cmba_core import canonical
from cmba_core.j1.disclosure import make
from cmba_workbench.k1.authoring import example
from cmba_workbench.k1.session import Workspace
from cmba_workbench.k1.views import compare_receipts,preview_disclosure
w=Workspace();bundle=example('cmba.consent');w.load(bundle);w.use_demo_context();w.evaluate();first=w.receipt_packet()
context=deepcopy(bundle['context']);context['time']['epoch']=201;w.set_reader_context(context);w.evaluate()
comparison=compare_receipts(first,w.receipt_packet())
assert comparison['same_binding'] and comparison['changed_inputs']==['time_hash']
private=make([{'label':'artifact','schema_id':'example.binding-root','value':bundle['binding']['binding_root']},
              {'label':'note','schema_id':'example.note','value':'PRIVATE EXAMPLE'}])
view=preview_disclosure(private,['artifact'],expected_root=private['header']['disclosure_root'])
assert b'PRIVATE EXAMPLE' not in canonical(view)
print(canonical({'status':'PASS','same_binding':comparison['same_binding'],'changed_inputs':comparison['changed_inputs'],
 'early':comparison['left_result']['status'],'later':comparison['right_result']['status'],
 'private_value_exported':False,'authority_effect':'NONE'}).decode())
