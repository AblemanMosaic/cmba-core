# CMBA Core Batch J — frozen application-family handoff

Distribution **cmba-core 0.1.0a2**. Explicit extensions **AP-J1 / SE-J1 / SD-J1**; I1 base unchanged.

## Exact artifacts

Source: `CMBA-Core-0.1.0a2-BATCH-J-APPLICATIONS-CANDIDATE.zip`  
SHA-256: `91c70d7f9c5bf4af335c45931ee997f873a9664e713e74ca4a0bfb3a75f2fb15`  
Members: 285; bytes: 22243083.

Wheel: `cmba_core-0.1.0a2-py3-none-any.whl`  
SHA-256: `a1614789d65a93199ac1399bd27ce870be4c744a3172522b3141b00fe0651920`

Predecessor: `CMBA-Core-0.1.0a1-BATCH-I-FOUNDATION-CANDIDATE.zip`  
SHA-256: `429c4317088e91ba0ef29c678665db01da07b7823cb12b182f769c78b549a2d5`.

Frozen native DKN H: `c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3`.

## Completed evidence

561/561 CMBA tests pass: 213 inherited and 348 new, no failures/errors/skips. Four executable
workflows pass. Both repeat from the final extracted source archive. 33 I1 + 53 J1 conformance
cases pass exact canonical response comparison; these are included in the 561 count. The oracle
is reference-assisted, not a complete second implementation or semantic-equivalence proof.

The unchanged DKN suite separately passes 1,173/1,173 tests in four disjoint execution groups,
whose identity union equals a separately collected full suite. All 668 native source-archive
files remain byte-identical. This is not a re-execution of every historical DKN release stage
or genuine BLAKE3-dependent legacy tests. Incomplete combined runs remain recorded as incomplete.

All 19 inherited CMBA runtime/data files retain their bytes. The base contract, commitment and
33-case corpus retain their bytes. New profiles/components are additive. Evaluator realization
identity intentionally changes, so old realization-bound receipts may require the old installation.

Core-only and optional signing/DKN environments pass installed wheel probes outside the source
tree; 41 package files compare exactly. Core requires no third-party runtime dependency. The
optional environment uses inventoried copies of genuine preinstalled distributions and passes
pip check; it is NOT fresh dependency download/resolution evidence. The source ZIP and wheel
rebuild byte-identically from extraction. Linux/Python 3.13.5 is the executed target.

Native cryptography cross-check: 68 point admissions + 16 valid and 16 mutated signatures
against installed libsodium. This is a finite same-author comparison, not independent crypto review.
The inherited I1 Tk GUI smoke passes eight checks under Xvfb, including after extraction.

## Models and application scope

I1 semantic commitment: `2f7ae78f19f7c06e85b176a9f2e1eb83383b41edb158e61c4fb16b653ca34e32`.

J1 semantic commitment: `8734691fb74b3697a09c4eb67b57860fb3c95b2050a0185cd1c651db64dc97a8`.

46 obligations have checked reference/code/recorded-test bindings (18 I1 + 28 J1), not a proof
of whole-program equivalence. Verification never regenerates accepted models or expected results.

Thirteen J1 evaluators, 24 schemas and 53 frozen cases implement bounded transformation graphs,
source-linked sessions, overlapping joint approvals, direct consent/withdrawal/renewal, composed
admissibility, salted selective openings, supplied-byte observation, multiparty record coordination,
conflict-preserving reconciliation, execution-record checks, source/claim traces, detached
endorsements and preserved native DKN reports. Profile policies and supplied facts do not grant
operational authority. `NATIVE_REPORT_COMPUTED` is not a blanket native PASS.

All 52 historical domain rows and 19 family mappings remain in the catalogue. Domain templates
are not implemented domain engines; PCSE/CARA/Vote and sensitive historical labels acquire no
clinical/election/operational-control guarantees. Endorsement records authenticate a statement,
not its truth or the legitimacy of its signer. Disclosure is inclusion, not encryption/unlinkability.

## Replay

Start with `README.md`, `docs/batch-j/README.md` and `docs/batch-j/DEVELOPER-GUIDE.md`.

```sh
python -m pip install ./cmba_core-0.1.0a2-py3-none-any.whl
# Optional: genuine cryptography/jsonschema and exact bundled DKN wheel in a prepared environment.
python tools/unpack_baseline.py /path/to/dkn-h
python tools/verify_j.py --dkn-source /path/to/dkn-h --out /path/to/new-evidence
python examples/j1_profiles.py
python examples/joint_applications.py
python tools/check_j_model.py --junit /path/to/new-evidence/tests.xml --expected-commitment 8734691fb74b3697a09c4eb67b57860fb3c95b2050a0185cd1c651db64dc97a8
python tools/package.py --verify /path/to/CMBA-Core-0.1.0a2-BATCH-J-APPLICATIONS-CANDIDATE.zip
```

The `cmba-app` CLI is read-only. Signing is an explicit Python call with caller-held keys, not
an input-document effect. Public example keys are deterministic TEST FIXTURES, never production.
Native filesystem paths are host-selected Python arguments, not accepted from the JSON ABI.

## Batch K entry boundary

Integrate J1 into native GUI pages: authoring, profile/capability browsing, jurisdiction/consent
matrix, receipt history, disclosure preview and explicit controlled local exports/imports.
The existing GUI remains I1 in this batch; J1 provides a tested headless integration model only.
Do not describe an unavailable J GUI page as delivered. Keep effects separate from assessment,
require host-enforced approval, bind output target/input/context, and retain version sovereignty.
No new network service, payload execution, automatic verifier installation, trust update or
external publication follows from opening a document. Batch L consolidates qualification.

External gates: native Windows/WSL/macOS, genuine legacy BLAKE3, independent review, fresh optional
dependency resolution, real custody/clock/recognition, deployment enforcement and domain approvals.
No live consensus/network, subdelegation, general compiler verification or global freshness claimed.

**Authority effect NONE; independent review NOT_PERFORMED; public release NOT_CLEARED.**
All release checksums/receipts are unsigned same-author engineering evidence.
