"""Public temporary fixtures; no production keys, network, deployment or permissions."""
from cmba_core import canonical
from cmba_core.j1.demo import joint_workflow
r=joint_workflow()
assert set(r['initial_statuses'])=={'MATCH_FOR_SUPPLIED_EVIDENCE'}
assert r['later_status']=='INSUFFICIENT' and r['same_assessment_object']
assert r['wrong_output_status']=='CONTRADICTED' and not r['private_content_in_public_view']
print(canonical(r).decode())
