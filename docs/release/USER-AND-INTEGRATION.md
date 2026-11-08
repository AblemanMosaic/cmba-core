# Using and integrating the frozen CMBA candidate

## Installation and version selection

Install the supplied `cmba_core-0.1.0a7-py3-none-any.whl` in an explicitly selected Python
3.12+ environment. The tested interpreter/platform appears in the release receipt.
The core library has no third-party runtime dependencies. Tk is an optional platform GUI
component. The `signing` capabilities require genuine `cryptography>=46,<47`. DKN adapters
require the exact bundled `dkn_core-0.2.0rc5-py3-none-any.whl` and its dependencies; they
never install themselves. Legacy BLAKE3 remains optional for consumers that need that capability;
the Windows qualification environment installed and replayed the genuine implementation.

For Windows, an operator can prepare an isolated environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install .\cmba_core-0.1.0a7-py3-none-any.whl
.\.venv\Scripts\cmba-workbench
```

These are operator commands, not a claim that Windows was executed here. Do not infer
production recognition from public example signing keys or embedded demonstration contexts.

Use `importlib.metadata.version('cmba-core')` for the distribution version. The intentionally
preserved module `__version__` identifies the older core implementation, not the cumulative
package. DKN retains independent `dkn_v02` and legacy `dkn_core` interfaces.

## The architecture in one workflow

1. Choose an exact installed profile contract. Construct typed dimensions and a binding.
2. Supply the values and any referenced material needed by that profile.
3. Select a reader-owned expected root, policy, recognized authorities, evidence and time.
4. Evaluate the supplied material; inspect each result and its explicit limits.
5. Replay the receipt to recompute the assessment, rather than trusting stored PASS text.
6. Separately authorize any local export through the trusted host's prepare/approve/commit path.

The binding is the object commitment. The receipt commits a particular evaluation context
and result. The signing envelope, native DKN root and transport digest are separate objects.
Changing one does not silently redefine the others.

## Python library

```python
from cmba_core import dimension, bind, inspect, profile_reference
from cmba_core.registry import contract

profile = profile_reference(contract('cmba.generic'))
value = {'title': 'An exact declaration', 'revision': 1}
item = dimension('description', 'metadata', 'example.description.v1', value,
                 critical=False)
obj = bind(profile, [item])
report = inspect(obj, {'description': value})
assert report['semantic_truth'] == 'NOT_ESTABLISHED'
```

For J1 application evaluations:

```python
from cmba_core.j1.evaluation import bind_application, evaluate, replay

# record must satisfy the selected application's exact schema.
# reader_context must come from your own accepted recognition/policy path.
obj = bind_application('cmba.kasd', record)
receipt = evaluate(obj['binding'], obj['values'], reader_context)
replay(receipt, obj['binding'], obj['values'], reader_context)
```

The second example intentionally names application inputs rather than inventing a generic
trusted policy. `context_for` is a demo/authoring helper: taking the expected root from an
untrusted object authenticates nothing. A profile's supported predicates are not a universal
semantic interpreter. Require your own dimensions and handlers where the built-ins do not
meet your application contract.

Complete executable examples are in `examples/`: first_binding, dkn_bridge, j1_profiles,
joint_applications, workbench_k, and workbench_k_receipts.

## Workbench

`cmba-workbench` launches the integrated ten-view native UI. `cmba-workbench-i1` selects
the historical inspector. Opened data never installs code or adopts a reader context.
A demonstration context requires explicit selection and is not a trust ceremony.

Use the object inspector and authoring view to create/inspect bindings. The application
catalogue distinguishes implemented profiles from historical templates. Local navigation
follows only material already held. The assessment view retains predicate-level missing,
contradictory and unsupported results. Receipt history compares changed context inputs
and replays claimed results. Imported history remains NOT_REPLAYED until recomputed.
The disclosure view exports only explicitly selected openings. Workspaces can contain
private material and are neither encrypted nor scrubbed.

Local file export is create-only: prepare exact bytes/name/root/state/deadline, inspect the
plan, explicitly approve through the trusted host, and commit once. A successful assessment
never serves as that approval. Existing files are not overwritten. A failed post-link
readback is reported as an actual file creation with uncertainty, not a no-effect failure.

## Interfaces and result interpretation

`cmba` exposes I1 data operations; `cmba-app` exposes J1; `cmba-wb` exposes read-only
workbench operations. `cmba-export` is a separately confirmed terminal effect path.
`cmba-agent` provides a unified discovery and dispatch envelope over the three read-only ABIs;
it does not expose `cmba-export`.
Canonical JSON is required by the data protocols. Exit zero means computation completed:
CONTRADICTED, INSUFFICIENT and NO_MATCH can all be valid computed results.

`MATCH_FOR_SUPPLIED_EVIDENCE` is scoped to supplied material and reader policy.
`NATIVE_REPORT_COMPUTED` means a pinned DKN operation ran; read its nested native result.
Neither implies install/execute permission, globally current state, verified physical truth,
or institutional legitimacy. The host/integrator supplies real custody, recognition,
clock, protected floors, transport deadlines and actual effect enforcement.
