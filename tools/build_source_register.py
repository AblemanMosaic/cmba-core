"""Explicit attribution/custody documentation, not truth certification of papers."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
ids={'CMBA_Framework_Whitepaper.md':'file_00000000daa071fda176d38325f41ec9',
 'CMBA_Mathematical_Framework.md':'file_000000001a0071fdb59da9541925122c',
 'Cryptographic Admissibility and Jurisdiction.md':'file_00000000869c71fd98275bdd3163bbd2',
 'DKN-core-CMBA-session-transcript-2026-11-07.md':'file_00000000a06481fd96c03fe7881fe125',
 'Pasted text(20261108-015154).txt':'file_00000000eea881fd9a810c71fa572fc1'}
records=[]
for p in sorted((ROOT/'sources').iterdir()):
 raw=p.read_bytes();records.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),
  'bytes':len(raw),'file_id':ids[p.name],'origin':'CONVERSATION' if p.name.startswith(('DKN-core-CMBA','Pasted')) else 'USER_LIBRARY',
  'standing':'SOURCE_MATERIAL_NOT_RUNTIME_GUARANTEE','complete_source_bytes_retained':True})
register={'schema':'cmba.source-register.i1','records':records,
 'external_primary_references':[
  {'url':'https://github.com/secure-systems-lab/dsse/blob/master/protocol.md','role':'TYPED_ENVELOPE_COMPARISON_ONLY_NOT_IMPLEMENTED'},
  {'url':'https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md','role':'TYPED_STATEMENT_COMPARISON_ONLY_NOT_IMPLEMENTED'},
  {'url':'https://docs.python.org/3/library/tkinter.html','role':'GUI_API_REFERENCE_NOT_PLATFORM_VALIDATION'}],
 'missing_primary_titles':['CMBA_VOTE.md','CMBA_VOTE (outline).md','CRYPTOGRAPHIC_DIMENSIONALITY.md',
                          'CMBA_BLOCKCHAIN_COMPARISON.md','CMBA_ROADMAP_11_27_2025.md'],
 'missing_status':'NOT_LOCATED_IN_THIS_RETRIEVAL; SECONDARY_ASSESSMENT_RETAINED',
 'older_edition_status':'SELECTED_EXACT_NAME_ADMISSIBILITY_LIBRARY_FILE; OTHER_SEARCH_HITS_NOT_MERGED',
 'authority_effect':'NONE'}
(ROOT/'SOURCE-REGISTER.json').write_text(json.dumps(register,indent=2,sort_keys=True)+'\n')
cat=json.loads((ROOT/'catalogue/APPLICATIONS.json').read_text())
lines=['# Application catalogue and realization map','',
 'Source-derived taxonomy: **52 rows / eight sections**. The original heading says 51 / ten.',
 'This discrepancy is retained, not silently repaired in the original. All domain rows below are',
 '**CATALOGUE_ONLY**. Source use-case wording is historical terminology, not a delivered guarantee.',
 'Nineteen application-family records are a separate engineering mapping, not nineteen additional',
 'independent historical products. The machine-readable source is `catalogue/APPLICATIONS.json`.',
 '', '## Shared application-family work program','',
 '| Family | Present disposition | Target | Meaning / boundary |','|---|---|---|---|']
for e in cat['entries']:
 if e['kind']=='APPLICATION_FAMILY':lines.append(f"| {e['label']} | {e['implementation']} | {e['target_batch']} | {e['purpose']} |")
lines+=['','## Historical domain inventory','',
 '| Original label | Original section | Original dimensions | Original use case | Source line |',
 '|---|---|---|---|---|']
for e in cat['entries']:
 if e['kind']=='SOURCE_DOMAIN_INVENTORY':
  lines.append(f"| {e['label']} | {e['sector']} | {', '.join(e['source_dimensions'])} | {e['source_use_case']} | {e['source']['line_start']} |")
lines+=['','## Coverage and non-equivalences','',
 'The inventory is complete for the recovered whitepaper section 4.3, not a claim that every',
 'CMBA artifact in every user workspace has been found. Other named research sources and all',
 'their evidence are separately listed in SOURCE-REGISTER.json. A proposal can be inspected and',
 'bound before its predicates are implemented; it cannot be invoked as though it were an installed',
 'evaluator. Domain deployment, domain truth and accepted authority remain separate obligations.',
 '', 'CHC compilation and the later admissibility profile are related but separately identified.',
 'The secondary assessment reports another CHC expansion, Consciousness-Harmonized Contracts,',
 'and ambiguous CPC/DKN expansions. No aliases are automatically equated. A future recovered',
 'document may add an explicit mapping; it cannot silently change this catalogue or a binding.',
 '', 'PCSE/CMBA-AI and CARA are research-source identities here, not recovered working code. The',
 'zero-hallucination and clinical-validation assertions remain unestablished by this package.',
 'Military, weapons and nuclear-control labels remain descriptive inventory only.']
(ROOT/'docs/APPLICATIONS.md').write_text('\n'.join(lines)+'\n')
print('source records',len(records))
