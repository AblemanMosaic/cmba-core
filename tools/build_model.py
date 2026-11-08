"""AUTHORING ONLY. Freeze model/bindings deliberately; verification never regenerates them."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cmba_core import canonical
from cmba_core.bindings import digest

OBLIGATIONS=[
 ('I-01','Finite canonical values; no ambiguous encodings or coercion','src/cmba_core/codec.py','tests/test_codec.py','test_rejected_encoding'),
 ('I-02','Dimension identifiers, roles, schemas, criticality and values are bound','src/cmba_core/bindings.py','tests/test_bindings.py','test_dimension_scope_bound'),
 ('I-03','Exact body/root and typed native references; no heuristic self-hash exclusion','src/cmba_core/bindings.py','tests/test_bindings.py','test_no_self_reference_projection_loophole'),
 ('I-04','Exact installed profile contract identity, not name-only interpretation','src/cmba_core/registry.py','tests/test_evaluation.py','test_wrong_profile_hash'),
 ('I-05','Unsupported critical semantics never produce a successful application match','src/cmba_core/evaluation.py','tests/test_evaluation.py','test_extension_semantics'),
 ('I-06','Required values and full profile predicate set cannot be silently omitted','src/cmba_core/evaluation.py','tests/test_evaluation.py','test_no_cherrypicked_policy'),
 ('I-07','Unsigned evaluation receipts bind supplied context separately from object identity','src/cmba_core/evaluation.py','tests/test_evaluation.py','test_receipt_tracks_context_without_mutating_object'),
 ('I-08','Replay recomputes conclusions; an internally rehashed forgery is insufficient','src/cmba_core/evaluation.py','tests/test_evaluation.py','test_self_consistent_forged_receipt_refuses_replay'),
 ('I-09','DKN native identity retained alongside a distinct wrapper root','src/cmba_core/profiles/dkn.py','tests/test_dkn_bridge.py','test_native_archive_and_root_preserved'),
 ('I-10','One actual finite transformation check, not a compiler correctness theorem','src/cmba_core/profiles/chc.py','tests/test_evaluation.py','test_true_and_false_transformation'),
 ('I-11','Source spans and attribution checked without asserting interpretation truth','src/cmba_core/profiles/session.py','tests/test_evaluation.py','test_session_true_span_false_interpretation_not_claimed_true'),
 ('I-12','Read-only capability surface cannot install/fetch/execute/publish from input data','src/cmba_core/abi.py','tests/test_interfaces.py','test_effect_operations_refuse'),
 ('I-13','Document contexts require explicit demonstration selection or reader input','src/cmba_workbench/model.py','tests/test_interfaces.py','test_workbench_requires_explicit_context'),
 ('I-14','Recovered taxonomy rows preserve source claims and do not imply implementations','src/cmba_core/data/catalogue.json','tests/test_interfaces.py','test_catalogue_complete_relative_to_table'),
 ('I-15','Schemas are structural aids, never substitutes for cryptographic checks','tools/export_schemas.py','tests/test_contracts.py','test_schema_not_cryptographic_verification'),
 ('I-16','Conformance oracle compares exact canonical typed envelopes','tools/run_conformance.py','tests/test_contracts.py','test_conformance_oracle_bool_int_exact'),
 ('I-17','Finite constructor budgets and typed local-file refusals','src/cmba_core/cli.py','tests/test_interfaces.py','test_cli_cannot_turn_nonregular_file_into_payload'),
 ('I-18','Core is independently usable without importing DKN or GUI runtime','src/cmba_core/__init__.py','tests/test_interfaces.py','test_no_ambient_import_of_dkn')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bound_paths(root=ROOT):
    paths=[]
    for directory in ('src','tests','tools','examples','schemas'):
        paths += [p for p in (root/directory).rglob('*') if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts]
    return sorted(paths+[root/'pyproject.toml'])

def main():
    refs=[ROOT/p for p in ('docs/PROTOCOL-I1.md','docs/ARCHITECTURE.md','docs/SECURITY-AND-CLAIMS.md',
          'docs/MODEL-AND-REPLACEMENT.md','catalogue/APPLICATIONS.json','interop/core-i1.json','SOURCE-REGISTER.json')]
    refs+=sorted((ROOT/'schemas').glob('*.json'))
    contract={'schema':'cmba.semantic-contract.i1','profile':'CMBA-I1','status':'EXPERIMENTAL_ENGINEERING',
      'obligations':[{'id':i,'realized_guarantee':g,'scope':'FINITE_I1_NOT_UNIVERSAL_OR_DEPLOYMENT_APPROVAL'} for i,g,_,_,_ in OBLIGATIONS],
      'references':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in refs],
      'exclusions':['signature authentication except optional frozen DKN certificate check','live distributed services',
        'domain truth, medical/election/weapon-control validation','native CMBA authority or effect grants',
        'full compiler correctness','complete semantic equivalence','independent approval'],
      'authority_effect':'NONE'}
    commitment={'schema':'cmba.semantic-commitment.i1','algorithm':'SHA-256',
                'digest_hex':digest('semantic-contract',contract),'authority_effect':'NONE'}
    realization={'schema':'cmba.realization-binding.i1','semantic_commitment':commitment['digest_hex'],
      'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in bound_paths()],
      'traceability':[{'id':i,'implementation':code,'test_file':test,'test_function':func} for i,_,code,test,func in OBLIGATIONS],
      'scope':'FILE_HASH_AND_TEST_REFERENCE_TRACEABILITY_NOT_PROGRAM_EQUIVALENCE','authority_effect':'NONE'}
    for name,value in [('CONTRACT.json',contract),('COMMITMENT.json',commitment),('REALIZATION-BINDING.json',realization)]:
        (ROOT/'model'/name).write_bytes(canonical(value))
    print('model',commitment['digest_hex'],'obligations',len(OBLIGATIONS),'source files',len(realization['files']))
if __name__=='__main__':main()
