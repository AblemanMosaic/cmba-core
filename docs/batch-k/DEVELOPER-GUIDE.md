# Library, JSON interface and host integration

The new package is cmba_workbench.k1. Importing its headless models does not import Tk,
cryptography or DKN. Those are loaded only by selected GUI or application capabilities.
All pre-K runtime source remains byte-preserved; the core evaluator identity is unchanged.
K has a separate workbench contract and realization binding.

## Read, assess, replay

```python
from cmba_workbench.k1.session import Workspace
from cmba_core import decode

workbench = Workspace()
workbench.load(decode(canonical_bundle_bytes), name="Reviewed release")
workbench.set_reader_context(reader_owned_context)
receipt = workbench.evaluate()
replay = workbench.replay_history(0)
```

The caller supplies canonical_bundle_bytes and reader_owned_context. A file's own context
is never adopted by load. use_demo_context is an explicitly named public-fixture convenience,
not a production recognition procedure. set_reader_context validates exact root/profile shape
but cannot establish how the caller acquired that information.

Workspace holds at most 64 documents and 128 history entries, also constrained by the base
canonical aggregate byte/node limits. It refuses additional state rather than silently evicting
history. snapshot produces data only; restore is all-or-nothing for admitted content and resets
selection, context and replay markings. A failed import invalidates the current selection.

prepare_evaluation creates a source-bound immutable snapshot. execute_task is pure and can run
off-thread. accept_result recomputes the receipt. The trusted GUI uses execute_verified_task to
perform evaluation and replay in the worker, then accepts its nonserialized host result object
only if the pending generation still matches. This object is not a sandbox boundary against
arbitrary Python in the host. Imported serialized results always take the replay path.

## Explicit local effect

```python
from cmba_workbench.k1.effects import LocalEffects

with LocalEffects(operator_selected_directory,
                  current_state=workbench.state_binding) as host:
    plan = host.prepare("receipt", workbench.receipt_packet(), name="review-001.json")
    # Present the exact plan to the operator here. Do NOT infer approval from receipt.status.
    # Only after an affirmative host-owned decision:
    token = host.approve(plan["plan_hash"])
    effect_receipt = host.commit(token)
```

The example's approval call marks the HOST ENFORCEMENT POINT. In an integrating program it
must not be reached from an artifact instruction, a green verification result, an untrusted
plugin, or a request body's approved=true field. A malicious caller already executing Python
can bypass a Python library; that is not a solved trust boundary. Read HOST-EFFECT-CONTRACT.md.

No host effects are reachable through cmba-wb JSON. The separate command:

```sh
cmba-export payload.json --workspace /operator/chosen/directory --name output.json --kind bundle
```

requires interactive exact-hash confirmation and refuses non-terminal input. Payload must be
canonical. Kind is structurally checked, not treated as a truth/privacy assertion. Source-file
changes invalidate approval. There is no unattended yes flag.

## Read-only K1 ABI

```json
{"schema":"cmba.workbench-request.k1","operation":"inspect","arguments":{"bundle":{}}}
```

This layout is explanatory; actual inputs must use CMBA canonical JSON. Operations are inspect,
author, evaluate, replay, compare, compare-receipts, navigate, disclosure-preview, design,
qualification, installed-qualification, handoff, capabilities and catalogue. Argument shapes
are closed in abi.dispatch and schemas/k1/request.schema.json. Author returns a new in-memory
binding; it neither writes nor signs. A successful process exit can carry CONTRADICTED,
INSUFFICIENT or NOT_EXECUTED. It is not admission.

```sh
cmba-wb request.json
# or canonical bytes on stdin:
python -m cmba_workbench.k1.cli -
```

## DKN paths

Native filesystem paths are explicit host-side arguments to the preserved
cmba_core.j1.native.read_collection(path, operation, arguments, kind=...). The GUI uses a
separately selected index directory or existing vault file. There is no path parameter in K1's
serialized ABI. Native namespace/lifecycle/SAM/distributed requests are available through the
cmba.native-dkn application record, preserving its fixed native schema and nested outcomes.
No DKN code is copied, migrated, force-enabled, or inferred from a catalogue acronym.

## Other views

views.compare_receipts replays BOTH packets before listing changed input hashes and results.
views.handoff emits references for DKN/CCP/UCM/P/PPI/Courthouse; it does not submit them and makes
no claim that the external system implements this format. views.qualification compares supplied
declarations only. The finite design explorer never registers code or turns combinations into
security scores. Disclosure preview verifies all supplied openings before selecting an export.

Production signing remains the existing explicit caller-held Python operation from J1. K does
not introduce a GUI keyring or silently give examples production signing authority.
