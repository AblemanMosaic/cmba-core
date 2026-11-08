"""A false transform can have a valid binding; only actual checking rejects its claim."""
from cmba_core.demo import chc,session
from cmba_core import inspect
from cmba_core.evaluation import evaluate,replay
import json

def main():
    results=[]
    for label,b in [('correct-transform',chc()),('incorrect-transform',chc(wrong_output=True)),('session',session())]:
        inspect(b['binding'],b['values'])
        r=evaluate(b['binding'],b['values'],b['context'])
        replay(r,b['binding'],b['values'],b['context'])
        results.append({'case':label,'status':r['body']['result']['status'],'root':b['binding']['binding_root']})
    assert [r['status'] for r in results]==['MATCH_FOR_SUPPLIED_EVIDENCE','CONTRADICTED','MATCH_FOR_SUPPLIED_EVIDENCE']
    print(json.dumps({'status':'PASS','cases':results,'authority_effect':'NONE'},sort_keys=True))
if __name__=='__main__':main()
