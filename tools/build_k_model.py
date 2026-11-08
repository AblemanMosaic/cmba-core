"""AUTHORING ONLY. Bind K to the deliberately authored current I/J commitments."""
from pathlib import Path
import sys,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tools')]
from cmba_core import canonical,decode
from cmba_workbench.k1.common import hash_value
import build_model

O=[
 ('K-01','I1 semantics and DKN baseline retained; scoped core and corpus transitions disclosed','session.py','test_k_workspace.py','test_core_evaluator_identity_is_unchanged_from_frozen_j'),
 ('K-02','All thirteen application profiles operate through the workbench','session.py','test_k_workspace.py','test_all_application_profiles_through_workbench'),
 ('K-03','Reader context never silently adopted from an opened object','session.py','test_k_workspace.py','test_explicit_context_ownership_and_no_adoption'),
 ('K-04','Failed input clears active selection rather than displaying current success','app.py','test_k_workspace.py','test_failed_import_clears_active_context'),
 ('K-05','Task snapshots and generation changes reject stale or forged results','session.py','test_k_workspace.py','test_task_source_change_cancellation_and_rehashed_forgery'),
 ('K-06','Single worker cancellation discards results without claiming termination','jobs.py','test_k_views_interfaces.py','test_jobs_cancel_discard_and_refuse_concurrent_workers'),
 ('K-07','Deadline is a result-acceptance deadline, not an OS sandbox','jobs.py','test_k_views_interfaces.py','test_jobs_timeout_is_discard_not_a_claim_of_termination'),
 ('K-08','Workspace restore selects no context and marks historical results unverified','session.py','test_k_workspace.py','test_workspace_roundtrip_does_not_restore_trust'),
 ('K-09','Receipt comparisons replay both inputs and retain independent object identity','views.py','test_k_views_interfaces.py','test_receipt_comparison_replays_then_exposes_changed_context'),
 ('K-10','Authoring changed data does not carry previous approvals','authoring.py','test_k_workspace.py','test_authoring_preserves_no_stale_approvals'),
 ('K-11','Navigation is finite local evidence with exact schemes and visible truncation','session.py','test_k_workspace.py','test_navigation_resolution_scope_and_truncation'),
 ('K-12','Selective export contains only the verified selected openings','views.py','test_k_views_interfaces.py','test_disclosure_export_contains_only_selected_openings'),
 ('K-13','Finite design combinations do not create security rankings or code','views.py','test_k_views_interfaces.py','test_explorer_explicit_unsupported_combinations'),
 ('K-14','Realization comparison cannot promote unverified claims to qualification','views.py','test_k_views_interfaces.py','test_qualification_never_promotes_declarations'),
 ('K-15','Integration handoffs are references, not automatic submissions','views.py','test_k_views_interfaces.py','test_handoff_references_only_no_submission'),
 ('K-16','Data-shaped approval cannot invoke a local file write','effects.py','test_k_effects.py','test_serialized_data_cannot_approve'),
 ('K-17','Plan cancellation, one-shot approval and create-only exact output enforced','effects.py','test_k_effects.py','test_prepare_cancel_approve_commit_exact_and_no_overwrite'),
 ('K-18','Expired or changed input invalidates approved effects','effects.py','test_k_effects.py','test_expiry_and_input_substitution'),
 ('K-19','Portable filenames, symlinks and root replacement refuse','effects.py','test_k_effects.py','test_parent_replacement_refused'),
 ('K-20','Cooperating writers cannot overwrite a competing destination','effects.py','test_k_effects.py','test_cooperating_writer_race_never_overwrites'),
 ('K-21','Postcommit durability uncertainty is reported as an actual effect','effects.py','test_k_effects.py','test_postcommit_directory_fsync_uncertainty_is_not_no_effect'),
 ('K-22','Read-only ABI never exposes signing, approval or arbitrary effects','abi.py','test_k_views_interfaces.py','test_k_json_interface_cannot_request_effects'),
 ('K-23','Actual native GUI workflows and host confirmation path executed','app.py','test_k_gui_contract.py','test_actual_integrated_native_gui'),
 ('K-24','Headless workbench remains usable without Tk, DKN or cryptography','session.py','test_k_workspace.py','test_k_library_no_tk_crypto_or_native_import_by_default'),
 ('K-25','Finite history budgets refuse without silent eviction','session.py','test_k_workspace.py','test_history_budget_refuses_without_silent_eviction'),
 ('K-26','Frozen conformance compares complete canonical typed outputs','abi.py','test_k_contracts.py','test_frozen_k_conformance')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    bound=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in build_model.bound_paths()]
    pins={folder:decode((ROOT/folder/'COMMITMENT.json').read_bytes())['digest_hex']
          for folder in ('model','model/j1')}
    for folder,pin in pins.items():
        path=ROOT/folder/'REALIZATION-BINDING.json';r=decode(path.read_bytes());r['files']=bound;path.write_bytes(canonical(r))
    refs=sorted((ROOT/'docs/batch-k').glob('*.md'))+sorted((ROOT/'schemas/k1').glob('*.json'))+[
      ROOT/'interop/workbench-k1.json',ROOT/'src/cmba_workbench/k1/data/qualification.json']
    contract={'schema':'cmba.semantic-contract.k1','profile':'WB-K1','status':'EXPERIMENTAL_BOUNDED',
      'base_semantic_commitments':pins,
      'obligations':[{'id':i,'realized_guarantee':g,'scope':'FINITE_OFFLINE_HOST_AND_DATA_PROFILE'} for i,g,_,_,_ in O],
      'references':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in refs],
      'assumptions':['operator-owned local filesystem','cooperating processes','trusted installed host','reader-supplied policy/time/recognition'],
      'exclusions':['independent security approval','hostile administrator/kernel custody','physical power-loss proof','live network/publication',
        'arbitrary code sandbox','forced termination of Python worker','automatic trust adoption','encryption/secret scrubbing','domain truth','whole-program equivalence'],
      'authority_effect':'NONE','local_effect':'SEPARATELY_APPROVED_CREATE_ONLY_JSON'}
    h=hash_value('semantic-contract',contract)
    commitment={'schema':'cmba.semantic-commitment.k1','algorithm':'SHA-256','digest_hex':h,'authority_effect':'NONE'}
    realization={'schema':'cmba.realization-binding.k1','semantic_commitment':h,'files':bound,
      'traceability':[{'id':i,'implementation':'src/cmba_workbench/k1/'+f,'test_file':'tests/'+t,'test_function':fn} for i,_,f,t,fn in O],
      'claim_ceiling':'HASH_SYMBOL_AND_EXECUTED_TEST_TRACEABILITY_NOT_EQUIVALENCE','authority_effect':'NONE'}
    for name,data in [('CONTRACT.json',contract),('COMMITMENT.json',commitment),('REALIZATION-BINDING.json',realization)]:
        (ROOT/'model/k1'/name).write_bytes(canonical(data))
    print('K1',h,'obligations',len(O),'bound-files',len(bound))
if __name__=='__main__':main()
