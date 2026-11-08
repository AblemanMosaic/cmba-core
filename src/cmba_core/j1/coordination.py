"""Finite two-round public agreement records. No distributed consensus protocol."""
from ..bindings import exact, validate_reference, identifier, hex_digest
from ..errors import require
from .common import sequence, integer, equal, hash_value, recognized, valid_time, interval, outcome
from .endorsements import verified_records


def terms_hash(record):
    return hash_value('coordination-terms',{k:record[k] for k in ('subject','terms','participants','jurisdiction')})


def assess(record, context):
    exact(record, {'subject','terms','participants','jurisdiction','rounds'})
    validate_reference(record['subject']);identifier(record['jurisdiction'])
    sequence(record['participants'],minimum=1,limit=16)
    for key in record['participants']:hex_digest(key)
    require(len(set(record['participants']))==len(record['participants']),'CMBA_J_DUPLICATE_PARTICIPANT')
    sequence(record['rounds'],minimum=1,limit=2)
    p=context['policy']['parameters'];exact(p, {'required_phase'});integer(p['required_phase'],0,1)
    # Evidence is carried in signed round envelopes, not accepted external PASS records.
    require(not context['evidence_snapshot'],'CMBA_J_UNCONSUMED_EVIDENCE')
    th=terms_hash(record);previous=None;rows=[];overall='MATCH'
    for index,round_ in enumerate(record['rounds']):
        exact(round_, {'phase','previous_round_hash','statements'})
        integer(round_['phase'],0,1);require(round_['phase']==index and round_['previous_round_hash']==previous,'CMBA_J_ROUND_ORDER')
        signed=set();denied=set();ignored=[]
        for rec,b in verified_records(round_['statements']):
            require(b['kind']=='coordination','CMBA_J_STATEMENT_KIND');v=b['payload']
            exact(v, {'terms_hash','phase','previous_round_hash','decision','not_before','not_after'})
            hex_digest(v['terms_hash']);integer(v['phase'],0,1);interval(v)
            require(v['decision'] in ('agree','withdraw'),'CMBA_J_DECISION')
            if v['previous_round_hash'] is not None:hex_digest(v['previous_round_hash'])
            if (v['terms_hash']==th and v['phase']==index and v['previous_round_hash']==previous and
                valid_time(v,context['time']['epoch']) and b['public_key'] in record['participants'] and
                recognized(context['authority_snapshot'],b['public_key'],'participant',record['jurisdiction'])):
                (signed if v['decision']=='agree' else denied).add(b['public_key'])
            else:ignored.append(rec['record_hash'])
        state='CONTRADICTED' if denied else 'MATCH' if signed==set(record['participants']) else 'INSUFFICIENT'
        if state=='CONTRADICTED' or (state=='INSUFFICIENT' and overall!='CONTRADICTED'):overall=state
        previous=hash_value('coordination-round',round_)
        rows.append({'phase':index,'status':state,'round_hash':previous,'recognized_agreements':sorted(signed),
                     'recognized_withdrawals':sorted(denied),'ineligible_records':sorted(ignored)})
    if len(record['rounds'])-1 < p['required_phase'] and overall=='MATCH':overall='INSUFFICIENT'
    return outcome({'coordination.same-terms':overall}, {'rounds':rows,'terms_hash':th,'assessed_subject':record['subject']},
       ceiling='All specified recognized keys endorsed identical terms in ordered finite rounds; not key independence, consensus safety/liveness or permission.')
