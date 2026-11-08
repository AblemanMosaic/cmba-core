# CMBA Core + Native Workbench — Batch K

**Distribution 0.1.0a3 · WB-K1 · bounded engineering candidate**

A standalone typed-binding library, thirteen application-profile evaluators, an optional
native workbench, and separately controlled local file operations. CMBA binds descriptions;
profiles check finite relationships; a host decides whether to perform an effect. Those
responsibilities do not collapse into one “verified” badge.

Start with **docs/batch-k/README.md** and **docs/batch-k/USER-GUIDE.md**. The full program is
**docs/PROGRAM-I-L.md**. I1 and J1 protocol documentation remains historical and normative for
its own profiles; it is not relabeled as a K feature. DKN's exact frozen source and wheel
remain independent under baseline/dkn.

```sh
python -m pip install ./cmba_core-0.1.0a3-py3-none-any.whl
cmba-workbench
```

Core use has no third-party runtime dependency. Tk/display is required only by the GUI.
Genuine optional signing/DKN packages are selected explicitly. No auto-install, network fetch,
remote execution, automatic signing, publication or policy adoption occurs on opening a file.

## Current surfaces

* cmba / cmba-app: unchanged I1/J1 data interfaces.
* cmba-wb: K1 read-only data interface, including authoring in memory.
* cmba-workbench: integrated K1 native UI; cmba-workbench-i1 retains the earlier inspector.
* cmba-export: separate interactive create-only JSON export with exact-plan confirmation.
* Python cmba_workbench.k1: reusable workspace, views, jobs and explicitly constructed host gate.

The GUI has no autosave. Workspace snapshots do not restore trusted context. Imported receipts
need replay. A prepared export writes nothing; it expires, is single-use and never overwrites.
The supported filesystem profile assumes an operator-owned local directory and cooperating
processes, not a malicious host or universally durable network filesystem.

All prior runtime files, I1/J1 semantic contracts/commitments and conformance corpora are retained.
K introduces a new workbench contract and evidence, not silent changes to binding semantics.
The release receipt records exact tested platform, denominators, clean replay and package hashes.
Unsigned engineering evidence is not independent review. **Public release: NOT_CLEARED.**
