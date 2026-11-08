"""AUTHORING ONLY: source-preserving J1 cards/templates; no domain engine is invented."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cmba_core import canonical,decode
from cmba_core.codec import clone

MAPPING={'dkn':['cmba.native-dkn'],'chc-compilation':['cmba.chc.graph'],'gendev':['cmba.gendev.rich-session'],
 'kasd':['cmba.kasd'],'consent':['cmba.consent'],'admissibility':['cmba.admissibility'],'disclosure':['cmba.disclosure'],
 'observation':['cmba.observation'],'coordination':['cmba.coordination'],'reconciliation':['cmba.reconciliation'],
 'execution':['cmba.execution-record'],'pcse':['cmba.claim-trace'],'cara':['cmba.claim-trace']}


def build():
    original=decode((ROOT/'catalogue/APPLICATIONS.json').read_bytes(),canonical_required=False)
    entries=[];templates=[]
    for row in original['entries']:
        card=clone(row);card['source_record_preserved']=clone(row)
        card['mapping_authorship']='CMBA_BATCH_J_ENGINEERING_MAPPING_NOT_SOURCE_CLAIM'
        if row['kind']=='SOURCE_DOMAIN_INVENTORY':
            sensitive=row['label'] in ('CMBA-Military','CMBA-Weapons','CMBA-Nuclear')
            card['implementation']='DESCRIPTIVE_ONLY' if sensitive else 'RECORD_TEMPLATE_ONLY'
            card['callable']=False
            card['capability_mappings']=[] if sensitive else ['cmba.claim-trace','cmba.kasd','cmba.consent']
            card['unimplemented_predicates']=['Domain truth and source-specific use-case validation','Real-world jurisdiction and deployment approval']
            template={'schema':'cmba.domain-template.j1','catalogue_id':row['catalogue_id'],'label':row['label'],
              'source':row['source'],'source_dimensions':row['source_dimensions'],'source_use_case':row['source_use_case'],
              'record_shape':{'subject':'TYPED_REFERENCE_REQUIRED','claims':'ATTRIBUTED_SOURCE_SPANS_REQUIRED',
                'policy':'READER_SELECTED','evidence':'EXPLICIT_SUPPLIED_RECORDS'},
              'capability_mappings':card['capability_mappings'],'validation':'NOT_IMPLEMENTED_DOMAIN_ENGINE',
              'operational_control':False,'authority_effect':'NONE'}
            templates.append(template);card['template_id']=row['catalogue_id']
        else:
            key=row['catalogue_id'].removeprefix('family.');profiles=MAPPING.get(key,[])
            card['capability_mappings']=profiles;card['profile_id']=profiles[0] if profiles else row.get('profile_id')
            if key in ('pcse','cara'):
                card['implementation']='REFERENTIAL_TRACE_ONLY';card['callable']=True
                card['claim_ceiling']='Callable generic trace check, not the named clinical/reasoning application.'
            elif profiles:card['implementation']='BOUNDED_J1_EVALUATOR';card['callable']=True
            elif key=='vote':
                card['implementation']='RESEARCH_REFERENCE_ONLY';card['callable']=False
                card['capability_mappings']=['cmba.consent','cmba.coordination']
            elif key=='evaluation':card['implementation']='I1_AND_J1_REPLAYABLE_EVALUATION';card['callable']=True
            else:card['implementation']='LATER_BATCH_OR_REFERENCE_ONLY';card['callable']=False
        entries.append(card)
    result={'schema':'cmba.application-catalogue.j1','entries':entries,'domain_templates':templates,
      'coverage':{'source_domains':52,'application_families':19,'actual_domain_engines':0},
      'historical_count_discrepancy':original['source_count_discrepancy'],
      'claim_ceiling':'Source catalogue, bounded common evaluators and descriptive templates; not 71 operational applications.',
      'authority_effect':'NONE'}
    raw=canonical(result)
    (ROOT/'catalogue/APPLICATIONS-J1.json').write_bytes(raw)
    (ROOT/'src/cmba_core/data/j1-catalogue.json').write_bytes(raw)
    print('catalogue',len(entries),'templates',len(templates))
if __name__=='__main__':build()
