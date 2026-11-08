# CMBA Core Batch K — frozen workbench handoff

Distribution **cmba-core 0.1.0a3**; opt-in workbench profile **WB-K1**.

Source: `CMBA-Core-0.1.0a3-BATCH-K-WORKBENCH-CANDIDATE.zip`  
SHA-256: `e2fd92eddb6fd5138665c016b4dc94f54196b8dc7de9995c4370cdbd01c911da`  
Members: **480**.

Wheel: `cmba_core-0.1.0a3-py3-none-any.whl`  
SHA-256: `4ad2cceeb6edff17ae45622f2b6a1708111551cfa3ab65da9bcfb2bbaa6df95a`.

Predecessor J source: `91c70d7f9c5bf4af335c45931ee997f873a9664e713e74ca4a0bfb3a75f2fb15`.

## Completed scope

Ten integrated native pages; all thirteen J1 profiles; explicit reader-context selection;
finite local graph navigation; JSON data authoring; per-predicate jurisdiction/consent views;
receipt history/replay and comparison; selective public views; finite profile-design exploration;
realization declaration comparison; read-only native DKN collection access; and separately
approved, expiring, create-only local JSON exports. No arbitrary executable runner is introduced.

759/759 CMBA tests pass (561 inherited, 198 new), with no errors/failures/skips. Six workflows,
48 actual Tk checks and 33 I1 + 53 J1 + 42 K1 conformance cases pass. Conformance and GUI cases
are also exercised in pytest and are not added again to inflate unique test totals.
Fresh extraction repeats these legs and both source ZIP and wheel rebuild byte-identically.
The preserved DKN v0.2 suite separately passes 1173 cases in four disjoint groups whose identities
match independent full collection. Genuine BLAKE3-dependent legacy execution remains unperformed.

The core-only and optional-dependency installed environments both pass outside-source probes;
52 installed package/data files match the wheel. Actual installed Tk GUI checks pass as well.
The core needs no third-party runtime dependency. The optional environment uses inventoried
copies of genuine installed dependencies, not fresh download/resolution evidence.
Executed environment: Linux/Python 3.13.5, SQLite 3.46.1, Tk 8.6.16 under Xvfb.

## Preservation and models

All 41 inherited CMBA source/data files are unchanged. I1/J1 contract/commitment/corpus bytes
remain unchanged, as does the core evaluator identity. Frozen DKN source/wheel and all 668
unpacked source members remain byte-identical. K only adds an explicitly selected workbench
layer and updates distribution metadata/entrypoints, ledger and realization bindings.

WB-K1 semantic commitment: `d248731d2654095abd1de21f0d7bcb09fc146f603c44dc16c9bbd5e1e9936431`.

Source fingerprint: `94004ff09eaede6711a6aa23ba585341acca8bc8050b2ee290f21c20b9f12884`.

72 obligations have checked hash/reference/symbol/recorded-test traceability: 18 I1, 28 J1,
26 K1. This is not a proof of full semantic equivalence. All receipts are unsigned same-author
engineering evidence; accepted roots/keys/models still require an independent recognition path.

## Material repair and retained failures

A fault-injection test showed the initial export path could pass its deadline while staging
was flushed and still install the final filename. A second deadline check immediately before
link installation now refuses that case and cleans staging. The pre-repair failure is retained.
Other retained corrections cover unavailable inherited DISPLAY, DKN collection verbosity,
and an installed-probe API typo. None is hidden by the final successful denominator.

## Install and replay

```sh
python -m pip install ./cmba_core-0.1.0a3-py3-none-any.whl
cmba-workbench
# Historical I1 inspector remains explicitly selectable:
cmba-workbench-i1
```

Tk and a graphical session are required by the optional GUI. Genuine signing and DKN dependencies
are optional; install the frozen native wheel only when those capabilities are selected.
Public demonstration keys and document contexts must not become production recognition pins.

From source in a prepared environment:

```sh
python tools/unpack_baseline.py /path/to/empty-dkn-source
python tools/verify_k.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase tests
python tools/verify_k.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase workflows
python tools/verify_k.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase audit
python tools/verify_k.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase assemble
python tools/verify_native_k.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-native-run
```

Start at `docs/batch-k/README.md`; the user guide, developer guide, host-effect contract,
protocol, acceptance map, findings and realization/handoff document are adjacent.

## Batch L entry boundary

Consolidate qualification rather than expanding features: audit cross-profile/effect boundaries,
independently challenge frozen results, add scoped cross-language checks, reconcile source,
schema, model and claims, package dependency inventory and one review dispatch. Do not relabel
missing native Windows/WSL/macOS runs, real custody/time/floor enforcement, fresh optional
package resolution, live network integration or independent review as passing evidence.

The local effect mechanism assumes an operator-owned filesystem, cooperating processes and
trusted host code. It does not sandbox hostile Python/kernel/admins, encrypt exports, prove
physical power-loss durability, overwrite files, or terminate a stuck evaluator thread.
Cancellation/deadline discards worker results, not arbitrary running native code.

No external review submission, publication or authority promotion occurred. Explicit test
exports did create temporary local files. **Public-release gate NOT_CLEARED.**
