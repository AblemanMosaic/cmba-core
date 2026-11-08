# Replay and Batch K handoff

## Prepared environment

Use Python 3.12+ with genuine pytest/jsonschema and cryptography for development tests. The
optional frozen DKN track needs its real dependencies. The core-only installation probe uses
no third-party packages; signature/DKN probes run in a separate explicitly prepared environment.
No public registry publication is assumed and no user machine is modified by this package.

```
python tools/unpack_baseline.py /tmp/dkn-h
PYTHONPATH=src:/tmp/dkn-h/src python tools/verify_j.py --dkn-source /tmp/dkn-h --out /tmp/cmba-j
PYTHONPATH=src:/tmp/dkn-h/src python tools/run_j_conformance.py --out /tmp/cmba-j-conformance.json
python tools/package.py --verify /path/to/frozen-source.zip
```

Windows uses `;` rather than `:` in PYTHONPATH and native Windows paths. These are replay
instructions, not evidence that Windows/WSL/macOS tests have run. Genuine legacy BLAKE3 is
still required for the separate historical v0.1 runtime; the preserved v0.2 suite is distinct.

To compare a replacement realization, supply its explicit process command to
`tools/run_j_conformance.py --command ...`. It must consume/produce the exact J1 conformance
envelope, with full canonical typed results. The harness is not a sandbox. Its expected
outputs are frozen, reference-assisted engineering fixtures; passing them is not proof of all
behaviors or storage equivalence. Record evaluator/toolchain identity changes explicitly.

The source ZIP and wheel reproduce when serializing the same frozen tree. Regenerating tests,
logs, receipts and timing fields does not claim to regenerate the same complete research dossier.
Verification must not invoke build_j_vectors, build_j_model or other authoring generators.

## What K consumes

Frozen J1 contracts, source projections, signed/public envelope shapes, disclosure proofs,
reader contexts, receipts, catalogue templates, the `Applications` headless model and all J1
Python/JSON APIs. Native DKN reports remain native and separately scoped. The existing I1 GUI
has not silently become a J1 authoring tool.

K implements actual integrated native pages and safe explicit local persistence effects:
open/inspect, typed components, history and relationships, approval/consent matrices, selective
views, receipt replay, finite profile design, replacement qualification and user-selected
save/export/import. Do not make an artifact's instructions executable. Do not auto-enable
signing, network, installation, shell, trust-store writes or publication. Signing still needs
explicit caller custody; UI permission fields alone are not host enforcement.

## External gates

Independent review; native target-machine execution; fresh optional dependency resolution;
full second-language realization; live network, instrument, authority and custody validation;
protected clocks/floors; and domain-specific acceptance remain separate. Public-release gate
NOT_CLEARED. Authority effect NONE. No external court or publisher receives this package
without an explicitly selected external action.

### Segmented frozen-DKN replay

The inherited DKN pytest configuration contains its own quiet option. To independently collect exact
identities rather than file-count summaries, use `pytest tests_v02 --collect-only -q -o addopts=''`.
In this bounded runner environment, the combined native execution was interrupted. Complete replay
was then performed in four disjoint groups: base/RC2, F, G, H. Their JUnit identity union must equal the
separately collected test set, with no duplicate identities or failures/skips. This is still a replay
of the same frozen suite, not an independent review or a replay of all historical release stages.
