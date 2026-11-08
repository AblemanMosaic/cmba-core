# Using the J1 application library

## Install deliberately

Install the supplied `cmba_core-0.1.0a2-py3-none-any.whl`. The base library and pure
transformation/session/reconciliation/disclosure predicates still use only the Python
standard library. Signature creation/verification requires the optional `signing` extra
(genuine cryptography 46.x). DKN adapters additionally require the bundled exact DKN wheel
and its own dependencies. Nothing auto-installs them or assumes an unreleased package exists
on a public registry. Tk is needed only for the existing native GUI. Target Python is 3.12+;
executed platform evidence is recorded in the current receipt, not inferred from that target.

```
python -m pip install ./cmba_core-0.1.0a2-py3-none-any.whl
# In a prepared environment with genuine cryptography/jsonschema:
python -m pip install ./baseline/dkn/dkn_core-0.2.0rc5-py3-none-any.whl
```

## Demonstrate the complete workflow

From an installed source checkout:

```
python examples/j1_profiles.py
python examples/joint_applications.py
```

The examples use PUBLIC deterministic fixture seeds. Never use fixture keys or embedded demo
context pins for production. The joint workflow checks a recorded session, recomputes a
transformation, packages its actual output with DKN, verifies that archive/certificate, evaluates
joint jurisdiction approvals and direct consent for its exact native root, and verifies a
selective disclosure of that same root. Advancing the assessment time expires approvals/consent
without changing the object. A coherently committed incorrect transform is contradicted.

## Library-level evaluation

```python
from cmba_core.j1.evaluation import bind_application, evaluate, replay

# record follows the selected schema; reader_context comes from your accepted policy path.
obj = bind_application('cmba.kasd', record)
receipt = evaluate(obj['binding'], obj['values'], reader_context)
replay(receipt, obj['binding'], obj['values'], reader_context)
```

`context_for` is an authoring/demo helper. It obtains a pin from the supplied binding, so using it
alone does NOT establish publisher recognition. Real readers supply their own accepted root,
profile/policy, authority membership, evidence, clock and any native rollback floor. Results are
scope-specific; process exit 0 is not acceptance. Bindings and receipts use separate roots.

## Actual module surface

| Module | Principal functions | Boundary |
|---|---|---|
| j1.registry | contracts, contract, resolve, capabilities | Installed fixed registry; no code from data |
| j1.evaluation | bind_application, context_for, evaluate, replay | Pure bounded assessments and exact replay |
| j1.endorsements | seal, verify, endorse, assess_endorsements, envelope, verify_envelope | Explicit caller-held key; no key persistence; recognition separate |
| j1.disclosure | make, select, verify | make generates salts unless explicitly supplied; no encryption |
| j1.transforms | toolchain, transform, assess | Fixed UTF-8/JSON transforms only |
| j1.governance | jurisdiction, consent, consent_context | Joint requirements and direct consent records |
| j1.provenance | session, claim_trace, measure_bytes, observation | Source/byte correspondence, not truth |
| j1.coordination | terms_hash, assess | Two-round record verification, not network consensus |
| j1.reconciliation | reconcile, assess | Deterministic conflict-preserving map merge |
| j1.execution | assess | Record and supplied testimony checks; no execution |
| j1.admissibility | assess | Recompute up to eight whitelisted child evaluations |
| j1.native | dispatch, read_collection | Exact installed DKN; host-selected read paths only in Python |
| j1.abi / cli | dispatch / cmba-app | Closed read-only data interface |
| cmba_workbench.applications_j1 | Applications | J1 selection/context/evaluation/replay seam for K |

## Detached endorsements

Construct a binding with an `endorsement-policy` dimension, exact role
`endorsement-requirements`, schema `cmba.endorsement-policy.j1`. The public policy binds the
required role/jurisdiction/action and unique-key threshold. Each custodian calls `endorse`
with only their own key object. The collector needs only public statements. Assess against
reader-pinned binding and policy roots, explicit authority snapshot and time.

`seal` authenticates a typed statement but does not interpret arbitrary payload claims.
Use the appropriate application handler to interpret that statement. Public envelope integrity
is not signer recognition; a recognition assessment is not an operational capability grant.

## Read-only JSON interface

`cmba-app REQUEST.json` or `python -m cmba_core.j1.cli -` accepts one canonical request:

```
{"schema":"cmba.request.j1","operation":"evaluate","arguments":{"binding":...,"values":...,"context":...}}
```

This explanatory layout is not canonical. Produce actual input with `canonical(request)`.
Operations: evaluate, replay, profiles, capabilities, verify-statement, verify-envelope,
verify-disclosure, dkn-read. The parser refuses unknown fields/operations. No sign, fetch,
execute, write, install or trust-update operation is present. CLI file input uses the preserved
bounded regular-file/symlink admission logic. Stdin is size-bounded, not a universal wall-clock
sandbox. Successful computation returns exit 0, even for NO_MATCH/CONTRADICTED/INSUFFICIENT;
refusal returns exit 2. Output is canonical JSON plus one framing newline.

For `dkn-read`, arguments contain a request with `operation` and `arguments`. Native operations
are archive (archive_hex, expected_root, certificate), namespace (genesis, transitions), lineage
(genesis, chains), lifecycle/assurance/distributed (request with that native ABI's exact schema).
Native results remain nested, with original assumptions and uncertainty.

`read_collection(path, operation, arguments, kind='index'|'vault')` is Python-only. It permits
resolve_exact, discover and traverse; index additionally exposes compare_namespace, and vault
read_namespace. Argument shapes differ where native interfaces differ. Index traverse includes
max_edges; vault traverse has max_depth/max_nodes only, preserving its native default edge cap.
These calls do not create missing vaults, advance heads, write artifacts or migrate indexes.

## Workbench use

The new headless model loads exactly schema `cmba.workbench-bundle.j1`, binding, values, context.
Evaluation requires `reader_context=...` or explicit `accept_document_context=True` for a demo.
Failed load/evaluation clears prior selection/receipt. Loaded data cannot register a handler.
The I1 Tk app remains unchanged in J; K adds actual integrated native workflow pages. Do not
interpret the current lack of J GUI pages as unimplemented J library evaluation.

## Replacement realizations and old receipts

Pin the I1 contract plus the separate J1 contract, profile contracts, signature/disclosure byte
rules, and both frozen conformance corpora. `tools/run_j_conformance.py --command ...` invokes an
explicitly selected local replacement executable and compares exact canonical response envelopes;
that executable is host-authorized code, not sandboxed by this library. Expected fixture results
are reference-assisted, not an independent correctness oracle or proof of program equivalence.

I1 code and binding/contract/corpus bytes are retained, but installed evaluator identity includes
all installed CMBA source/data. Adding J1 changes that realization identity, so an earlier receipt
that pins the old realization may require the old installation for exact replay. This is an
explicit provenance difference, not a silent rewrite of the underlying binding or semantic contract.
A replacement must renew its realization/evidence bindings even when the accepted contract remains
unchanged. A passing corpus never transfers jurisdiction or forces a software upgrade.
