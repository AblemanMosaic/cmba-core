"""Finite jurisdiction and consent predicates. Reader recognition is an explicit input.

Only direct grants are supported. Revocation is relative to supplied signed material;
there is no network currentness oracle, human-identity proof or enforcing runtime.
"""
from ..codec import canonical
from ..bindings import exact, identifier, hex_digest, validate_reference
from ..errors import require
from .common import (sequence, integer, text, equal, interval, valid_time, outcome,
                     hash_value, recognized)
from .endorsements import verified_records


def jurisdiction(record, context):
    exact(record, {'subject','action','requirements','facts'})
    validate_reference(record['subject']);identifier(record['action'])
    require(type(record['facts']) is dict,'CMBA_J_FACTS');canonical(record['facts'])
    sequence(record['requirements'],minimum=1,limit=16);requirements={}
    exact(context['policy']['parameters'],set())
    for r in record['requirements']:
        exact(r, {'id','jurisdiction','role','threshold','constraints'})
        for k in ('id','jurisdiction','role'):identifier(r[k])
        integer(r['threshold'],1,64);require(type(r['constraints']) is dict,'CMBA_J_CONSTRAINTS');canonical(r['constraints'])
        require(r['id'] not in requirements,'CMBA_J_DUPLICATE');requirements[r['id']]=r
    terms=hash_value('jurisdiction-terms',record);verified=verified_records(context['evidence_snapshot'])
    checks={};rows=[]
    for r in record['requirements']:
        approved=set();denied=set();ignored=[]
        for rec,b in verified:
            if b['kind']!='approval':continue
            v=b['payload'];exact(v, {'subject','action','terms_hash','requirement_id','role','jurisdiction','decision','not_before','not_after'})
            validate_reference(v['subject']);hex_digest(v['terms_hash']);interval(v)
            for k in ('action','requirement_id','role','jurisdiction'):identifier(v[k])
            require(v['decision'] in ('approve','deny'),'CMBA_J_DECISION')
            applies=(equal(v['subject'],record['subject']) and v['action']==record['action'] and v['terms_hash']==terms
                 and v['requirement_id']==r['id'] and v['role']==r['role'] and v['jurisdiction']==r['jurisdiction'])
            if applies and valid_time(v,context['time']['epoch']) and recognized(context['authority_snapshot'],b['public_key'],r['role'],r['jurisdiction']):
                (approved if v['decision']=='approve' else denied).add(b['public_key'])
            else:ignored.append(rec['record_hash'])
        missing=sorted(set(r['constraints'])-record['facts'].keys())
        violated=sorted(k for k,val in r['constraints'].items() if k in record['facts'] and not equal(val,record['facts'][k]))
        s=('CONTRADICTED' if denied or violated else 'INSUFFICIENT' if missing or len(approved)<r['threshold'] else 'MATCH')
        checks[r['id']]=s;rows.append({'requirement_id':r['id'],'jurisdiction':r['jurisdiction'],'status':s,
             'recognized_approvals':sorted(approved),'recognized_denials':sorted(denied),
             'missing_facts':missing,'violated_constraints':violated,'ineligible_records':sorted(ignored)})
    overlaps=[]
    for a in record['requirements']:
        for b in record['requirements']:
            if a['id']<b['id']:
                keys=sorted(set(a['constraints'])&set(b['constraints']))
                if keys:overlaps.append({'requirements':[a['id'],b['id']],'fields':keys,
                    'incompatible_fields':[k for k in keys if not equal(a['constraints'][k],b['constraints'][k])]})
    if any(x['incompatible_fields'] for x in overlaps):checks['constraints.compatibility']='CONTRADICTED'
    else:checks['constraints.compatibility']='MATCH'
    return outcome(checks, {'requirements':rows,'overlaps':overlaps,'terms_hash':terms,'assessed_subject':record['subject']},
       ceiling='All exact joint requirements checked against reader-recognized signed approvals and supplied facts; not legal legitimacy, fact truth or execution permission.')


def consent_context(record):
    return hash_value('consent-context', {'subject':record['subject'],'actor':record['actor'],
                      'action':record['action'],'jurisdiction':record['jurisdiction'],'renewal_context':record['renewal_context']})


def consent(record, context):
    exact(record, {'subject','actor','action','jurisdiction','facts','renewal_context'})
    validate_reference(record['subject']);identifier(record['actor']);identifier(record['action']);identifier(record['jurisdiction'])
    require(type(record['facts']) is dict and type(record['renewal_context']) is dict,'CMBA_J_FACTS');canonical(record)
    exact(context['policy']['parameters'],set());records=verified_records(context['evidence_snapshot']);now=context['time']['epoch']
    grants={};withdrawals=[]
    for rec,b in records:
        v=b['payload']
        if b['kind']=='consent-grant':
            exact(v, {'grant_id','subject','actor','action','jurisdiction','conditions','context_hash','not_before','not_after','delegation_depth','supersedes'})
            for k in ('grant_id','actor','action','jurisdiction'):identifier(v[k])
            validate_reference(v['subject']);hex_digest(v['context_hash']);interval(v)
            integer(v['delegation_depth'],0,0);require(type(v['conditions']) is dict,'CMBA_J_CONDITIONS')
            sequence(v['supersedes'])
            for h in v['supersedes']:hex_digest(h)
            require(len(set(v['supersedes']))==len(v['supersedes']),'CMBA_J_DUPLICATE')
            grants[rec['record_hash']]=(b['public_key'],v)
        elif b['kind']=='consent-withdrawal':
            exact(v, {'grant_hash','at'});hex_digest(v['grant_hash']);integer(v['at']);withdrawals.append((b['public_key'],v))
    superseded=set();withdrawn=set()
    # Exact references, same issuer, same scope, later validity start; never let another issuer erase a grant.
    for h,(key,v) in grants.items():
        for old in v['supersedes']:
            require(old in grants,'CMBA_J_SUPERSEDED_GRANT_MISSING')
            oldkey,oldv=grants[old]
            require(oldkey==key and v['not_before']>oldv['not_before'] and all(equal(v[k],oldv[k]) for k in ('subject','actor','action','jurisdiction')),
                    'CMBA_J_OVERRIDE_SCOPE')
            if v['not_before']<=now and recognized(context['authority_snapshot'],key,'consent-issuer',v['jurisdiction']):superseded.add(old)
    for key,v in withdrawals:
        if v['grant_hash'] in grants and key==grants[v['grant_hash']][0] and v['at']<=now:withdrawn.add(v['grant_hash'])
    eligible=[];rows=[];applicable=0
    for h,(key,g) in sorted(grants.items()):
        reason=None
        if not all(equal(g[k],record[k]) for k in ('subject','actor','action','jurisdiction')):reason='WRONG_SCOPE'
        elif not recognized(context['authority_snapshot'],key,'consent-issuer',record['jurisdiction']):reason='UNRECOGNIZED_ISSUER'
        else:
            applicable+=1
            if h in withdrawn:reason='WITHDRAWN'
            elif h in superseded:reason='SUPERSEDED'
            elif not valid_time(g,now):reason='OUTSIDE_VALIDITY'
            elif g['context_hash']!=consent_context(record):reason='RENEWAL_REQUIRED'
            elif any(k not in record['facts'] or not equal(record['facts'][k],v) for k,v in g['conditions'].items()):reason='CONDITIONS_NOT_MET'
        if reason is None:eligible.append(h)
        rows.append({'grant_hash':h,'disposition':reason or 'ELIGIBLE'})
    state='MATCH' if eligible else 'NO_MATCH' if applicable else 'INSUFFICIENT'
    return outcome({'consent.direct-grant':state}, {'grants':rows,'eligible_grants':eligible,'assessed_subject':record['subject'],
      'revocation_coverage':'SUPPLIED_RECORDS_ONLY','human_consent':'NOT_ESTABLISHED'},
      ceiling='Direct finite signed grants, same-issuer overrides, withdrawal and renewal in supplied evidence only; no subdelegation, actual informed consent or enforcement.')
