"""EXPLICIT AUTHORING ONLY. Preserve I1 contract bytes; separately bind the J1 extension."""
from pathlib import Path
import hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
from cmba_core import canonical,decode
from cmba_core.j1.common import hash_value
import build_model
O=[
 ('J-01','I1 semantic contract/corpus and DKN baseline retained; scoped core repair disclosed','native.py','test_j_contracts.py','test_frozen_i1_and_native_files_preserved'),
 ('J-02','Independent typed component projections recomputed under pinned contract','evaluation.py','test_j_applications.py','test_projection_hashes_independently_bound_and_checked'),
 ('J-03','Unknown critical semantics cannot silently match','evaluation.py','test_j_applications.py','test_unknown_critical_is_not_auto_supported'),
 ('J-04','Genuine Ed25519 primitives with strict public-key admission','endorsements.py','test_j_crypto_disclosure.py','test_rfc8032_test_vector_one_backend_and_admission'),
 ('J-05','Detached signatures follow precommitted body/policy, no circular root','endorsements.py','test_j_crypto_disclosure.py','test_detached_body_signature_envelope_no_cycle'),
 ('J-06','Distinct recognized keys only; no duplicate or same-key threshold inflation','endorsements.py','test_j_crypto_disclosure.py','test_same_signer_distinct_statements_count_once'),
 ('J-07','Finite transformation graph is actually recomputed','transforms.py','test_j_applications.py','test_chc_valid_binding_wrong_relationship'),
 ('J-08','Attributed source spans and capture limits remain explicit','provenance.py','test_j_applications.py','test_source_quote_and_capture_boundary'),
 ('J-09','Every joint jurisdiction requirement is evaluated','governance.py','test_j_applications.py','test_joint_approvals_no_missing_jurisdiction_laundering'),
 ('J-10','Overlapping incompatible jurisdiction constraints remain visible','governance.py','test_j_applications.py','test_joint_constraints_overlap_not_assumed_disjoint'),
 ('J-11','Direct consent scope/time/context/withdrawal checked','governance.py','test_j_applications.py','test_consent_scope_time_and_withdrawal'),
 ('J-12','Same-issuer override is explicit and old consent does not revive','governance.py','test_j_applications.py','test_same_issuer_override_and_renewal'),
 ('J-13','Selective salted openings require exact path/root/value and required labels','disclosure.py','test_j_crypto_disclosure.py','test_wrong_disclosure_opening_refused'),
 ('J-14','Observation checks supplied bytes rather than declaring physical truth','provenance.py','test_j_applications.py','test_observation_recomputes_actual_supplied_bytes'),
 ('J-15','Coordination checks identical terms and required distinct signers','coordination.py','test_j_applications.py','test_coordinator_terms_and_distinct_keys'),
 ('J-16','Reconciliation retains conflicts and distinguishes absence/null','reconciliation.py','test_j_applications.py','test_reconciliation_absent_not_null_and_no_winner'),
 ('J-17','Execution request/config/target/result checks never run payloads','execution.py','test_j_applications.py','test_execution_configuration_substitution'),
 ('J-18','Reference trace does not claim entailment or clinical truth','provenance.py','test_j_applications.py','test_trace_reference_not_truth'),
 ('J-19','Composed admissibility recomputes exact subject/time children','admissibility.py','test_j_applications.py','test_composition_recomputes_same_subject_and_time'),
 ('J-20','Native methods preserve detailed DKN conclusions and read snapshots','native.py','test_j_interfaces.py','test_real_native_vault_and_index_read'),
 ('J-21','Rehashed forged receipts fail exact re-evaluation','evaluation.py','test_j_applications.py','test_receipt_recomputed_not_rehash_certified'),
 ('J-22','Read-only interfaces cannot sign/install/fetch/execute/write','abi.py','test_j_interfaces.py','test_effects_unavailable_in_abi'),
 ('J-23','Pure core works without ambient crypto/DKN/UI imports','evaluation.py','test_j_interfaces.py','test_optional_dependency_is_not_ambient'),
 ('J-24','Domain cards remain templates, not operational domain engines','registry.py','test_j_contracts.py','test_catalogue_preserves_sources_and_does_not_invent_domain_engines'),
 ('J-25','Finite record budgets refuse oversized evidence','common.py','test_j_contracts.py','test_context_budgets'),
 ('J-26','Conformance checks exact types and complete envelopes','abi.py','test_j_contracts.py','test_boolean_vs_integer_exact_oracle'),
 ('J-27','Workbench selection requires explicit reader context','evaluation.py','test_j_interfaces.py','test_workbench_host_context_boundary'),
 ('J-28','Composed demonstration retains object identity as assessment expires','evaluation.py','test_j_applications.py','test_combined_end_to_end_workflow')]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    frozen_body=(ROOT/'model/CONTRACT.json').read_bytes();frozen_commit=(ROOT/'model/COMMITMENT.json').read_bytes()
    # Deliberate cumulative realization rebind; original semantic bytes must not change.
    build_model.main()
    assert (ROOT/'model/CONTRACT.json').read_bytes()==frozen_body
    assert (ROOT/'model/COMMITMENT.json').read_bytes()==frozen_commit
    refs=sorted((ROOT/'docs/batch-j').glob('*.md'))+sorted((ROOT/'schemas/j1').glob('*.json'))+[
       ROOT/'src/cmba_core/data/j1-profiles.json',ROOT/'catalogue/APPLICATIONS-J1.json',ROOT/'interop/applications-j1.json']
    c={'schema':'cmba.semantic-contract.j1','profile':'AP-J1_SE-J1_SD-J1','status':'EXPERIMENTAL_BOUNDED',
      'base_semantic_commitment':decode(frozen_commit)['digest_hex'],
      'obligations':[{'id':i,'realized_guarantee':g,'scope':'FINITE_SUPPLIED_VIEW'} for i,g,_,_,_ in O],
      'references':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in refs],
      'exclusions':['independent approval','live network consensus','domain truth/clinical/election validity',
        'subdelegation','trusted clock/authority/custody','runtime enforcement','general compiler correctness',
        'encryption/unlinkability/erasure','whole-program equivalence','full J1 GUI authoring'],
      'authority_effect':'NONE'}
    commitment={'schema':'cmba.semantic-commitment.j1','algorithm':'SHA-256','digest_hex':hash_value('semantic-contract',c),'authority_effect':'NONE'}
    r={'schema':'cmba.realization-binding.j1','semantic_commitment':commitment['digest_hex'],
       'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in build_model.bound_paths()],
       'traceability':[{'id':i,'implementation':'src/cmba_core/j1/'+code,'test_file':'tests/'+test,'test_function':fn} for i,_,code,test,fn in O],
       'claim_ceiling':'REFERENCE_AND_EXECUTED_TEST_TRACEABILITY_NOT_EQUIVALENCE','authority_effect':'NONE'}
    for name,v in [('CONTRACT.json',c),('COMMITMENT.json',commitment),('REALIZATION-BINDING.json',r)]:
        (ROOT/'model/j1'/name).write_bytes(canonical(v))
    print('J1 model',commitment['digest_hex'],'obligations',len(O))
if __name__=='__main__':main()
