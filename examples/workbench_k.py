"""Explicit local workflow in a temporary operator-owned directory; not publication."""
import tempfile
from pathlib import Path
from cmba_core import canonical,decode
from cmba_workbench.k1.authoring import example
from cmba_workbench.k1.session import Workspace
from cmba_workbench.k1.effects import LocalEffects
from cmba_workbench.k1.views import handoff

w=Workspace();w.load(example('cmba.chc.graph'),name='Public example')
w.use_demo_context();receipt=w.evaluate();w.replay_history(0)
packet=handoff('courthouse',w.selected(),receipt_packet=w.receipt_packet())
with tempfile.TemporaryDirectory() as directory:
    with LocalEffects(directory,current_state=w.state_binding) as host:
        plan=host.prepare('workspace',w.snapshot(),name='workspace.json')
        assert not list(Path(directory).iterdir())
        # DEMONSTRATION HOST DECISION. A real host must separately ask its operator.
        effect=host.commit(host.approve(plan['plan_hash']))
        restored=Workspace();restored.restore(decode((Path(directory)/'workspace.json').read_bytes()))
        assert restored._context is None and restored.history()[0]['verification']=='IMPORTED_NOT_REPLAYED'
        restored.replay_history(0)
print(canonical({'status':'PASS','assessment':receipt['body']['result']['status'],
 'local_effect':effect['status'],'restored_history_replayed':True,'external_submission':'NONE',
 'handoff_hash':packet['handoff_hash'],'authority_effect':'NONE'}).decode())
