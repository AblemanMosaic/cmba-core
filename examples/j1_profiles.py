"""Execute the bounded family catalogue using public fixture identities only."""
from cmba_core import canonical
from cmba_core.j1.demo import all_bundles,assess
r={name:assess(b)['body']['result']['status'] for name,b in all_bundles().items()}
assert r.pop('cmba.native-dkn')=='NATIVE_REPORT_COMPUTED'
assert set(r.values())=={'MATCH_FOR_SUPPLIED_EVIDENCE'}
r['cmba.native-dkn']='NATIVE_REPORT_COMPUTED'
print(canonical({'profiles':r,'authority_effect':'NONE'}).decode())
