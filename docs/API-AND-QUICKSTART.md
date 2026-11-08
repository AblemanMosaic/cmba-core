# Library and workbench quickstart

## Installation

The `cmba_core-0.1.0a7-py3-none-any.whl` distribution contains the standalone core, built-in data,
evaluators, and native workbench. The core needs no third-party runtime dependency. Tk is an
optional system/Python GUI component; a graphical session is required for the workbench.

```
python -m pip install ./cmba_core-0.1.0a7-py3-none-any.whl
cmba-workbench
```

For the native DKN bridge, install the exact bundled DKN wheel in an environment with its genuine
dependencies. It is retained under `baseline/dkn/` in the source package:

```
python -m pip install ./baseline/dkn/dkn_core-0.2.0rc5-py3-none-any.whl
```

Do not assume that an unreleased package is available on a public registry. No install command
has been run on the user's machine. This turn's installed-wheel checks use only local wheels
and preinstalled dependencies; see the receipt for the exact environment/evidence boundary.

For source development, install the source repository or set PYTHONPATH to its src directory.
Use a separately unpacked, unchanged Batch H `src` for tests needing the optional DKN adapter.
Legacy `dkn_core` still requires genuine BLAKE3; CMBA does not replace that dependency with a mock.

## Create, inspect and compare

```python
from cmba_core import dimension, bind, inspect, profile_reference
from cmba_core.registry import contract

profile = profile_reference(contract('cmba.generic'))
description = {'name': 'example', 'revision': 1}
item = dimension('description', 'metadata', 'example.description.v1',
                 description, critical=False)
obj = bind(profile, [item])
report = inspect(obj, {'description': description})
assert report['status'] == 'BINDING_STRUCTURE_VALID'
assert report['semantic_truth'] == 'NOT_ESTABLISHED'
```

A noncritical generic description is inspectable without a semantic handler. Mark a dimension
critical when a selected profile must understand it; the generic evaluator will then refuse to
call its semantics supported. `inspect` checks commitments only. `compare(a,b)` lists exact
changed dimensions and relations; it never establishes semantic equivalence.

## Evaluate one selected profile

```python
from cmba_core.demo import chc
from cmba_core.evaluation import evaluate, replay

bundle = chc()  # public deterministic demonstration, not trusted external input
receipt = evaluate(bundle['binding'], bundle['values'], bundle['context'])
assert receipt['body']['result']['status'] == 'MATCH_FOR_SUPPLIED_EVIDENCE'
replay(receipt, bundle['binding'], bundle['values'], bundle['context'])
```

The correct and incorrect CHC examples both have valid commitments. The evaluator actually
recomputes canonical JSON and returns CONTRADICTED for the incorrect output. No compiler, shell,
network request or user-supplied Python is invoked. This proves one finite transformation check,
not the historical CHC compiler-correctness claims.

`context_for` is an example authoring convenience: it takes its pin from the supplied binding.
Production readers must acquire expected roots and policies through their own accepted path.
The workbench explicitly labels embedded contexts as demonstration inputs and requires selection
before using one. The headless model also accepts a separately supplied reader_context.

## Optional DKN bridge

```python
from cmba_core.profiles.dkn import bind_archive

# expected_native_root must come from the reader's accepted configuration.
result = bind_archive(archive_bytes, expected_logical_root=expected_native_root,
                      certificate=optional_native_certificate)
```

The actual frozen DKN verifier checks the archive. Native manifest/certificate semantics remain
unchanged. CMBA produces a NEW wrapper root referencing the native root. Generic DKN-profile
evaluation checks the supplied manifest and transport-description shape only; it does not
reverify unavailable payload bytes or trust a submitted PASS report as evidence.

## API surface

| Module | API | Effects / boundary |
|---|---|---|
| codec | canonical, decode, clone | Pure finite encoding; explicit noncanonical authoring decode only |
| bindings | dimension, bind, reference, relation, inspect, compare | Pure structural/commitment operations; no network resolution |
| registry | catalogue, contracts, contract, resolve_profile, capability_descriptors | Read installed trusted data only; no plugin loading |
| evaluation | context_for, evaluate, replay, realization_identity | Read installed evaluator identity; no authority effects |
| profiles.dkn | load_native, bind_archive | Optional exact installed DKN code; no automatic installation |
| profiles.chc | evaluate | One finite canonical-JSON transformation |
| profiles.session | evaluate | Exact UTF-8 byte spans and explicit attribution; no truth/coverage inference |
| abi | dispatch | Closed read-only JSON request operations |
| cmba_workbench.model | Workbench | Testable local selection, inspection, explicit-context evaluation and replay |
| cmba_workbench.app | Application, main | Native Tk rendering and explicit local-file opening |

## CLI and JSON interface

`cmba REQUEST.json` or `cmba -` reads one exact canonical request. Structure:

```
{"schema":"cmba.request.v0.1-i1","operation":"...","arguments":{...}}
```

Canonical ordering is required on actual input, unlike this explanatory layout. Construct files
with `canonical(request)`. Available operations: inspect, compare, evaluate, replay, catalogue,
capabilities. Exact argument shapes are in the exported request schema and `abi.dispatch`.
There is no sign, execute, fetch, write, publish, import-plugin or trust-update operation.
Successful computation exits 0 even for CONTRADICTED/UNSUPPORTED/INSUFFICIENT. A typed refusal
exits 2. Output is canonical JSON plus one framing newline. Process success is not acceptance.

## Workbench controls

Open bundle admits a canonical local JSON file, not arbitrary archives/URIs or executable code.
The sample buttons select deterministic in-memory records. Binding inspector displays commitment
results, values, profile reference and embedded context. The checkbox permits a demonstration
assessment under that displayed context; it does not recognize a publisher. Evaluate opens the
receipt tab. Replay recomputes the last result. Application catalogue shows all source and family
records with implementation status. Program & boundaries gives the I–L plan. All loaded content
is rendered as text; markup or instructions inside it are not interpreted as commands.

For a unified machine-facing entry point, use `cmba-agent version`, `cmba-agent manifest`,
and `cmba-agent schema core|app|workbench`; see `docs/AGENT-CLI.md`. The historical I1 command
remains byte-contract compatible and does not gain effect operations through that wrapper.
