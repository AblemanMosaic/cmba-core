# CMBA Core — Batch L frozen review handoff

Distribution **cmba-core 0.1.0a4**. The I–L construction program is complete for the declared
finite offline scope. This is an unsigned same-author engineering review candidate, not
independent approval, production clearance or ratification of every historical CMBA claim.

## Exact artifacts

Source: `CMBA-Core-0.1.0a4-BATCH-L-REVIEW-CANDIDATE.zip`  
SHA-256: `f6c17012e986e83cbb8bdba81dc8eedada335d32c55f02ea8c2b848ddde1213e`  
Members: **641**; bytes: **43400971**.

Wheel: `cmba_core-0.1.0a4-py3-none-any.whl`  
SHA-256: `2a595c06ac64371647eeb9586defde9d3238dbe16271a788ea231de2e15831ce`.

Predecessor K: `e2fd92eddb6fd5138665c016b4dc94f54196b8dc7de9995c4370cdbd01c911da`.
Native DKN H: `c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3`.

The external `CMBA-BATCH-L-RELEASE-ENVELOPE.json` binds the exact source, wheel, checksum,
release receipt, clean replay receipt/evidence, this handoff, and installed-workbench screenshot.
It excludes its own hash and is NOT signed. An accepted external expected root is still needed
for authentication; an internally consistent self-hash is not publisher recognition.

## Completed evidence

**911/911 CMBA tests pass, with no skips/errors/failures: 759 inherited and 152 new.**
Six workflows pass. All repeat from clean extraction. The source ZIP and wheel rebuild
byte-identically from that frozen extracted tree. Source fingerprint:
`f6583f876142965ee200c1694ae33d0b30bba9512d2bc0067dce834e15a32907`.

All 33 I1 + 53 J1 + 42 K1 frozen conformance cases pass; these are included in the suite.
A separately written Node small-core implementation passes all 33 I1 cases and 60 additional
numeric/Unicode/parser/binding boundary or differential tests (93 total suite cases).
It implements only canonical, decode, dimension, bind, inspect, compare: NOT all application
profiles, signatures, DKN, workbench or effects. It is same-author, not independent review.

Native crypto comparison passes 68 point admissions + 16 valid and 16 mutated signatures.
The native Tk workflow passes 48 checks from source, extraction and installed wheel. Actual
operator confirmation in these tests is simulated explicitly in temporary directories.
The unchanged DKN suite separately passes 1,173 cases in completed disjoint groups with exact
identity coverage. It does not include blocked legacy BLAKE3 or every historical release stage.

Installed core-only and optional signing/DKN environments pass outside the source tree; all
52 package files compare exactly. Core uses the standard library only. Optional packages are
inventoried copies of genuine preinstalled dependencies, not fresh resolver/download evidence.
Executed platform: Linux/Python 3.13.5, SQLite 3.46.1, Node v22.16.0, Tk 8.6.16 under Xvfb.

## Findings and preservation

L-001: source-dossier verifier accepted aliased paths. L-002: nonregular ZIP member kinds.
L-003: boolean `true` accepted as a one-byte size. All are reproduced and repaired, with
minimal witnesses and regressions preserved. L-004 strengthens typed phase context,
output closure, test identity coverage and mandatory evidence legs. These are release-tool
findings, not a newly demonstrated runtime cryptographic bypass.

All 52 inherited runtime/data files, six semantic contract/commitment files and three frozen
corpora retain exact bytes. Eight inherited tooling/metadata/binding files change; none is
removed. All 668 native DKN members remain unchanged. Realization bindings are renewed.

The preserved GUI identifies its K1/a3 implementation in its header; `cmba_core.__version__`
is also a historical implementation marker. Check `importlib.metadata.version('cmba-core')`
for the installed distribution (a4). No new runtime is claimed under a changed title.

Semantic pins:
- I1 `2f7ae78f19f7c06e85b176a9f2e1eb83383b41edb158e61c4fb16b653ca34e32`
- J1 `8734691fb74b3697a09c4eb67b57860fb3c95b2050a0185cd1c651db64dc97a8`
- K1 `d248731d2654095abd1de21f0d7bcb09fc146f603c44dc16c9bbd5e1e9936431`

72 obligations have checked reference/code/recorded-test traceability, not a complete
semantic-equivalence proof. Verification never regenerates expected models or corpora.

## Install and replay

```sh
python -m pip install ./cmba_core-0.1.0a4-py3-none-any.whl
cmba-workbench
```

Optional signing/DKN functions require deliberately prepared genuine dependencies and the
exact bundled DKN wheel. Tk and a graphical session are required for the GUI. Public demo
keys and document-supplied contexts are not production identities or reader recognition pins.

From the extracted source in a prepared environment:

```sh
python tools/unpack_baseline.py /path/to/empty-dkn-source
python tools/verify_l.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase tests
python tools/verify_l.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase workflows
python tools/verify_l.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase audit
python tools/verify_l.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase assemble
python tools/verify_native_l.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-native --phase collect
# Run --phase group0, group1, group2, group3 separately, then --phase assemble.
python tools/release_envelope_l.py --verify /path/to/CMBA-BATCH-L-RELEASE-ENVELOPE.json --directory /path/to/artifacts
```

`--require-legacy` refuses without genuine BLAKE3. That mandatory refusal was observed with
exit 2, not counted as a successful legacy test. Shell/PowerShell replay helpers are supplied;
they are not evidence of Windows/WSL/macOS execution. Interrupted native and development
runs remain recorded as incomplete or failed, not silently adopted as completed receipts.

## Review priorities and stop condition

Start at `docs/release/README.md`. Review `SECURITY-AND-REVIEW.md` for prioritized checks of
canonicalization, signature admission/scope, cross-profile joins, evidence truth versus
recognition, disclosure limits, export linearization, imported receipts, source archives,
and parser/effect budgets. The component inventory is not a vulnerability scan or a license
clearance decision. Historical documents remain archived; current claims are in the release
claim map. No operational election/clinical/weapons-control engine is supplied.

Outstanding: native target platforms, genuine legacy BLAKE3, fresh optional resolution,
full alternative realization, independent review, real custody/time/floors and deployment
approval. DKN's original fifty-obligation ledger remains 35 scoped passes and fifteen limits.
Do not start another feature batch to make those external prerequisites disappear. Freeze
these artifacts for target-machine replay and a separately selected independent reviewer.
Do not automatically submit externally, publish, change trust stores or force upgrades.

**Authority effect NONE; explicit local test exports occurred; publication NOT_PERFORMED;
independent review NOT_PERFORMED; public-release gate NOT_CLEARED.**
