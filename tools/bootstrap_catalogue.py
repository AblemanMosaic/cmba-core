"""Explicit authoring: source-derived inventory plus separately labeled engineering proposals."""
from pathlib import Path
import json, re, hashlib
ROOT = Path(__file__).resolve().parents[1]
def write(p,v):
    p.write_text(json.dumps(v,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def profile(pid,title,requirements,checks,ceiling):
    return {'schema':'cmba.profile-contract.v0.1-i1','profile_id':pid,'profile_version':'i1',
            'title':title,'required_dimensions':[{'dimension_id':i,'role':r,'schema_id':s} for i,r,s in requirements],
            'predicates':checks,'unknown_critical':'UNSUPPORTED','unknown_noncritical':'PRESERVE_WITHOUT_INTERPRETATION',
            'authority_effect':'NONE','claim_ceiling':ceiling}
profiles = [
 profile('cmba.generic','Generic binding inspection',[],['binding.structure'],
         'Commitments only; no application semantics or authentication.'),
 profile('cmba.dkn.artifact','DKN frozen native-manifest adapter',
         [('manifest','artifact-state','dkn.logical-artifact.v0.2-candidate'),('transport','transport','cmba.transport-description.i1')],
         ['binding.structure','dkn.native-manifest','dkn.transport-description'],
         'Native manifest structure/root only in evaluator; use explicit archive adapter for payload checking. No namespace authority.'),
 profile('cmba.chc.transform','CHC bounded canonical-JSON transformation',
         [('input','source','cmba.text.i1'),('rule','transformation-rule','cmba.chc-rule.i1'),
          ('toolchain','toolchain','cmba.toolchain.i1'),('output','result','cmba.text.i1')],
         ['binding.structure','chc.supported-rule','chc.recomputed-output'],
         'Exact output of this finite JSON transform only, not arbitrary compiler correctness or a homology theorem.'),
 profile('cmba.gendev.session','GenDev source-span provenance',
         [('source','recorded-source','cmba.text.i1'),('events','attributed-interpretations','cmba.session-events.i1')],
         ['binding.structure','session.source-spans','session.attribution'],
         'Quoted byte spans and explicit attribution only. Interpretation truth, source authorship and complete session capture not established.')
]
write(ROOT/'src/cmba_core/data/profiles.json', profiles)

w=ROOT/'sources/CMBA_Framework_Whitepaper.md'; lines=w.read_text(encoding='utf-8').splitlines()
rows=[]; sector=None; inside=False
for n,line in enumerate(lines,1):
    if line.startswith('### 4.3 '):inside=True
    if line.startswith('### 4.4 '):inside=False
    if not inside:continue
    if line.startswith('#### '):sector=re.sub(r' \(\d+\)$','',line[5:])
    if line.startswith('| **CMBA-'):
        parts=[p.strip() for p in line.strip('|').split('|')]
        label=parts[0].replace('**',''); dims=[s.strip() for s in parts[1].split(',')]
        sensitive=label in ('CMBA-Military','CMBA-Weapons','CMBA-Nuclear')
        rows.append({'catalogue_id':'research.'+label.lower().replace('cmba-',''),
          'label':label,'kind':'SOURCE_DOMAIN_INVENTORY','sector':sector,
          'source_dimensions':dims,'source_use_case':parts[2],
          'source':{'path':'sources/'+w.name,'line_start':n,'line_end':n},
          'source_claim_status':'HISTORICAL_ASSERTION_NOT_IMPLEMENTATION_EVIDENCE',
          'implementation':'CATALOGUE_ONLY','callable':False,
          'planned_scope':'DESCRIPTIVE_RECORD_ONLY_NO_OPERATIONAL_CONTROL' if sensitive else 'DECLARATIVE_DOMAIN_TEMPLATE_WITH_EXPLICIT_UNIMPLEMENTED_PREDICATES',
          'semantic_assurance':'NOT_ESTABLISHED','authority_effect':'NONE'})
assert len(rows)==52 and len({r['label'] for r in rows})==52
families=[
 ('dkn','DKN','Existing frozen library; optional native-identity adapter', 'ADAPTER_IMPLEMENTED','cmba.dkn.artifact','I','transcript',944),
 ('chc-compilation','CHC — Cryptographic Homological Compilation','Transformation records and actual finite validation','BOUNDED_EVALUATOR_IMPLEMENTED','cmba.chc.transform','I','transcript',933),
 ('gendev','CMBA-GenDev','Recorded sessions, attributed decisions, reconsideration triggers','BOUNDED_EVALUATOR_IMPLEMENTED','cmba.gendev.session','I','math',2091),
 ('kasd','KASD — Key-Anchored Semantic Dimensioning','Overlapping jurisdiction requirements and approvals','PLANNED',None,'J','math',774),
 ('consent','Conditional renewable consent','Exact subject/resource/action grants, withdrawal, expiry, renewal','PLANNED',None,'J','assessment',30),
 ('admissibility','CHC — state/claims/admissibility profile','Separate current assessments from historical bindings','PLANNED',None,'J','admissibility',19),
 ('disclosure','Selective disclosure','Commitment inclusion and explicit disclosure limits','PLANNED',None,'J','assessment',38),
 ('observation','Measurement and observation','Observed bytes, method, instrument/calibration references','PLANNED',None,'J','transcript',1045),
 ('coordination','Multiparty coordination','Exact terms, required signers, conflicts and completion observations','PLANNED',None,'J','transcript',1046),
 ('reconciliation','Federated state reconciliation','Bounded merge rules, explicit conflicts, supplied snapshots','PLANNED',None,'J','transcript',1047),
 ('execution','Governed execution/deployment records','Compare declared request with supplied observations; no deployment authority','PLANNED',None,'J','transcript',1044),
 ('pcse','PCSE / CMBA-AI','Evidence/knowledge-source references; no reasoning or truth guarantee','RESEARCH_REFERENCE',None,'J','whitepaper',37),
 ('cara','CARA — Clinical Accountable Reasoning Architecture','Domain research reference, not a clinical decision engine','RESEARCH_REFERENCE',None,'J','math',714),
 ('vote','CMBA-Vote','Historical voting architecture; general consent is separate','RESEARCH_REFERENCE',None,'J','assessment',64),
 ('design-space','CMBA design-space explorer','Finite supported combinations and generated obligations, not a security theorem','PLANNED',None,'K','assessment',40),
 ('ccp','CCP curation integration','Exact curated stack references and reader-specific recognition','INTEGRATION_CONTRACT',None,'K','transcript',1475),
 ('model-realization','Constitutional model / realization binding','Contract, code, conformance and review evidence kept separate','PLANNED',None,'L','transcript',1485),
 ('runtime-enforcement','Runtime measurement/enforcement adapter boundary','Host-selected mechanisms; no ambient effects from documents','PLANNED',None,'K','assessment',18),
 ('evaluation','Policy evaluation receipts','Exact object, values, policy, authorities, evidence, evaluator and supplied time','IMPLEMENTED',None,'I','assessment',86),
]
paths={'transcript':'DKN-core-CMBA-session-transcript-2026-11-07.md','math':'CMBA_Mathematical_Framework.md',
 'whitepaper':w.name,'assessment':'Pasted text(20261108-015154).txt','admissibility':'Cryptographic Admissibility and Jurisdiction.md'}
for fid,label,purpose,status,pid,batch,source,line in families:
    rows.append({'catalogue_id':'family.'+fid,'label':label,'kind':'APPLICATION_FAMILY',
      'purpose':purpose,'source':{'path':'sources/'+paths[source],'line_start':line,'line_end':line},
      'implementation':status,'profile_id':pid,'callable':pid is not None,
      'target_batch':batch,'authority_effect':'NONE',
      'scope_authorship':'ENGINEERING_MAPPING_PROPOSED_IN_BATCH_I; SOURCE_TERMINOLOGY_RETAINED'})
cat={'schema':'cmba.application-catalogue.v0.1-i1','coverage':'RECOVERED_PRIMARY_SOURCES_AND_SUPPLIED_SESSION_ONLY',
 'source_count_discrepancy':{'source_claimed_applications':51,'observed_table_rows':52,
                           'source_claimed_sectors':10,'observed_table_sections':8},
 'entries':rows,'missing_primary_documents':['CMBA_VOTE.md','CMBA_VOTE (outline).md',
 'CRYPTOGRAPHIC_DIMENSIONALITY.md','CMBA_BLOCKCHAIN_COMPARISON.md','CMBA_ROADMAP_11_27_2025.md'],
 'missing_source_policy':'SECONDARY_ASSESSMENT_ONLY; NOT_TREATED_AS_RECONSTRUCTED_OR_REVIEWED_ORIGINALS',
 'claim_ceiling':'Catalogue presence and reusable record shape are not a domain implementation, approval or security guarantee.'}
write(ROOT/'catalogue/APPLICATIONS.json',cat);write(ROOT/'src/cmba_core/data/catalogue.json',cat)
# Pin original DKN runtime bytes; the adapter never rewrites their identifiers or source.
import zipfile
z=zipfile.ZipFile(ROOT/'baseline/dkn/DKN-core-0.2.0rc5-BATCH-H-REVIEW-CANDIDATE.zip')
files={p.removeprefix('src/'):hashlib.sha256(z.read(p)).hexdigest() for p in z.namelist() if p.startswith('src/') and p.endswith('.py')}
write(ROOT/'src/cmba_core/data/dkn-runtime.json',{'schema':'cmba.dkn-frozen-runtime.i1','distribution':'0.2.0rc5',
 'source_sha256':'c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3','files':files})
print('profiles',len(profiles),'domain entries',52,'families',len(families),'native runtime files',len(files))
