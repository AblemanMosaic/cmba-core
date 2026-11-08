# CMBA Core — Batch J application-family candidate

Distribution **cmba-core 0.1.0a2**. Original I1 and DKN identifiers, runtime files, contracts and frozen
corpora remain unchanged. New **AP-J1 / SE-J1 / SD-J1** application, endorsement and disclosure profiles
are explicitly selected. Start at [Batch J documentation](docs/batch-j/README.md), the
[developer guide](docs/batch-j/DEVELOPER-GUIDE.md), and [the I–L program](docs/PROGRAM-I-L.md).

Thirteen bounded J1 evaluators cover transformations, session provenance, scoped approvals,
consent, composed assessments, selective openings, supplied observations, coordination,
reconciliation, execution records, claim-reference traces, endorsements and native DKN queries.
These are not clinical/election/domain engines, a distributed consensus service or an execution host.

```sh
python -m pip install ./cmba_core-0.1.0a2-py3-none-any.whl
cmba-app request.json
cmba-workbench
```

The optional Tk workbench remains the inherited I1 inspector; its J1 headless adapter is present,
but J1 pages and authoring/effect workflows belong to Batch K. Pure core operations have no third-party
runtime dependency. Signature profiles require explicitly installed genuine `cryptography`; the DKN
adapter requires the exact bundled DKN wheel and its genuine dependencies. No network fetch or automatic
package installation occurs when opening a binding. The distribution version is a2; the preserved
`cmba_core.__version__` still identifies its frozen a1 module and `cmba_core.j1.VERSION` identifies a2.

Source checkout examples (with optional signing/DKN dependencies prepared):

```sh
python examples/j1_profiles.py
python examples/joint_applications.py
python tools/verify_j.py --dkn-source /path/to/extracted-dkn-h --out /path/to/new-evidence
```

Historical I1 evidence/current pointers are retained under `history/i1/` and `evidence/batch-i/`.
Read source claims and current engineering mappings separately. Research-only applications are
noncallable; all 52 historical domain templates explicitly lack operational domain validation.

The default boundary remains **INFORMATION_ONLY / authority effect NONE / public release NOT_CLEARED**.
Hashes/receipts are unsigned engineering evidence unless an explicit SE-J1 signature is supplied;
a signature authenticates its exact statement, not the truth or jurisdiction of that statement.
Independent review, native target-host runs, genuine BLAKE3 legacy behavior, live deployment and real
custody/clock/authority validation are separate gates, not satisfied by local test counts.
