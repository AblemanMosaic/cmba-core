# CMBA Core — Batch I frozen handoff

Distribution `cmba-core==0.1.0a1`; experimental profile I1. Four-batch program: I → J → K → L.

## Exact artifacts

Source: `CMBA-Core-0.1.0a1-BATCH-I-FOUNDATION-CANDIDATE.zip`  
SHA-256: `429c4317088e91ba0ef29c678665db01da07b7823cb12b182f769c78b549a2d5`

Wheel: `cmba_core-0.1.0a1-py3-none-any.whl`  
SHA-256: `c0f97fdf44ba1b2cb62a82c1be88303018c6cfc509d032a15a27feda1fd1b35e`

Base DKN: `0.2.0rc5`, source SHA-256 `c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3`.
The frozen source/wheel/receipts remain in `baseline/dkn/`; none are rewritten.

## Executed scope

213/213 new tests, two executable workflows, 33 conformance cases (included in 213), 18 model
obligations and native GUI source smoke pass. The new tests/workflows/model/corpus/GUI repeat from
clean extraction. The 1,173-test inherited DKN v0.2 suite separately replayed without failures or
skips; this is not a rerun of all prior release stages or the blocked legacy BLAKE3 suite.

A separate installed core environment uses no third-party runtime dependencies. The optional DKN
installed environment uses inventoried exact copies of genuine host dependencies and passes pip
check, not fresh network resolution. All 19 installed package source/data files match the wheel.
Installed native GUI checks also pass. Source ZIP and wheel rebuild byte-identically.

Source fingerprint: `638f2d489bb9bdac2f10faec38b95b22f4e93571cabf5a178197cd3f7471b1e2`  
I1 semantic commitment: `2f7ae78f19f7c06e85b176a9f2e1eb83383b41edb158e61c4fb16b653ca34e32`

## Read and run

Start with `README.md`, `docs/PROGRAM-I-L.md`, `docs/ARCHITECTURE.md`,
`docs/API-AND-QUICKSTART.md`, `docs/APPLICATIONS.md` and `docs/BATCH-I-HANDOFF.md`.

```sh
python -m pip install ./cmba_core-0.1.0a1-py3-none-any.whl
cmba-workbench
```

Core requires Python 3.12+; executed Python is 3.13.5/Linux. Tk and a graphical session are
required by the optional GUI. Explicitly install the bundled DKN wheel plus its genuine
cryptography/JSON Schema dependencies only when selecting that adapter. No public package
registry availability is assumed.

```sh
python tools/unpack_baseline.py /tmp/dkn-h
python tools/verify_i.py --dkn-source /tmp/dkn-h --out /tmp/cmba-i-evidence
python tools/package.py --verify /path/to/CMBA-Core-0.1.0a1-BATCH-I-FOUNDATION-CANDIDATE.zip
```

The model checker validates the current reference hashes, code/test links and executed-test
records, not program equivalence. Receipts are unsigned; application context is supplied and
reader-owned. Exact roots require independent recognition/pinning. The workbench's sample context
is explicitly demonstration-only. It cannot fetch, sign, install, execute payloads or publish.

## Application accounting and Batch J

The recovered table actually has 52 rows in eight sections, while its original heading says
51 applications/10 sectors. All rows are preserved with source anchors. Nineteen additional
cross-cutting family mappings make 71 catalogue entries, not 71 working applications. Four
bounded built-in profile contracts are executable: generic, DKN artifact, one CHC JSON
transformation and GenDev source-span validation. Historical PCSE/CARA/Vote and domain-security
claims are not promoted by cataloguing them.

J implements the bounded family predicates and separately versioned endorsement/disclosure
profiles in PROGRAM-I-L; K completes usable integrated workbench workflows and controlled local
effects; L consolidates qualification. Do not replace expected corpus results to make an
alternative realization pass. Do not change DKN IDs or existing semantic commitments silently.

External target platforms, legacy BLAKE3, independent security review, real key custody,
clock/floor protection, network deployment and domain approvals remain open. No automatic external
review submission or publication is authorized by this handoff.

**Authority effect NONE; independent review NOT_PERFORMED; public release NOT_CLEARED.**
