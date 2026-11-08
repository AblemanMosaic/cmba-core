"""Optional frozen-library integration; no publication, keys or namespace migration."""
import json
from cmba_core.profiles.dkn import load_native,bind_archive
from cmba_core.evaluation import context_for,evaluate

def main():
    n=load_native();raw,m=n.pack({'readme.txt':b'An unchanged DKN artifact, referenced through CMBA.\n'})
    result=bind_archive(raw,expected_logical_root=m['logical_root'])
    receipt=evaluate(result['binding'],result['values'],context_for(result['binding'],epoch=100))
    assert result['native_report']['status']=='PASS'
    print(json.dumps({'status':'PASS','native_root':m['logical_root'],'binding_root':result['binding']['binding_root'],
                      'evaluation':receipt['body']['result']['status'],'authority_effect':'NONE'},sort_keys=True))
if __name__=='__main__':main()
