# DKN Batch H — frozen review handoff

Distribution **0.2.0rc5**. The A–H / F–H construction program ends at a bounded review
candidate. This is not independent security approval or production release clearance.

## Exact artifacts

Source: `DKN-core-0.2.0rc5-BATCH-H-REVIEW-CANDIDATE.zip`

SHA-256: `c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3`

Wheel: `dkn_core-0.2.0rc5-py3-none-any.whl`

SHA-256: `6cc2d9e21c1c26b9b9104bb84a27b8e873f17c7e52bed15228230775e005ccf8`

Predecessor: `DKN-core-0.2.0rc4-BATCH-G-CANDIDATE.zip`

SHA-256: `cb659af507734796c8b69602449b7fe93efb31a3c66407b997f6e2d882994e97`

The 668-file source archive has a closed BATCH-H inventory. All 43 inherited runtime files,
six semantic body/commitment files and three frozen corpora retain their bytes. Earlier
inventories/certificates remain historical. All engineering receipts are unsigned.

## Completed scope

1,173/1,173 tests pass: 1,075 inherited cases plus 98 H regressions, no failures/errors/skips.
Seven executable workflows pass. All results repeat from the extracted frozen archive.
The three repaired-oracle conformance runs pass 47 + 24 + 28 cases; these are included in
the cumulative suite. Existing Node comparisons total 68 scoped cases, not a full second
runtime. Native crypto checks cover 89 point admissions and 24 valid/24 mutated signatures.

Source ZIP and wheel rebuild byte-identically from the extracted tree. The installed wheel
passes base, lifecycle/vault and distributed probes outside source; 43 installed payload
files compare exactly. Dependencies are copied genuine preinstalled distributions, not
fresh downloads. The actual environment is Linux/Python 3.13.5, SQLite 3.46.1, Node v22.16.0.

Source fingerprint: `bc8dd48db155b863a1f5b7579697b9b3df81fec8693716ab15aaf8b6c3cf9870`.

## Material findings

H-001: the old conformance oracle accepted bool/int substitutions under Python equality.
H-002: a JSON null response bypassed mismatch checking. Both are reproduced, repaired and
regression-tested. Runtime modules and expected corpus values did not change.
H-003: current security/inventory pointers are consolidated; older prose is preserved as
history. H-004: explicit review phase context, source and outputs are bound and checked,
with strict JUnit completeness and authority-boundary checks.

The three semantic commitments remain unchanged; 42 obligations have checked code/reference/
recorded-test traceability. The original fifty-obligation ledger remains 35 scoped passes
and fifteen explicitly partial, blocked, deferred or unperformed/unrun obligations.

## Replay and operator path

Start at `docs/release/README.md`. Install dependencies in a reviewed environment, then:

```sh
python tools/verify_batch_h.py --out /path/to/evidence --phase tests
python tools/verify_batch_h.py --out /path/to/evidence --phase examples
python tools/verify_batch_h.py --out /path/to/evidence --phase audit
python tools/verify_batch_h.py --out /path/to/evidence --phase assemble
```

Add `--require-legacy` to each command for a mandatory legacy replay. The explicit mandatory
probe returns exit 2 while genuine BLAKE3 is unavailable; it does not turn BLOCKED into PASS.
Use `tools/replay_windows_h.ps1` or `sh tools/replay_posix_h.sh` in an already prepared target
environment. Those scripts are instructions, not evidence of Windows/WSL/macOS execution.

## Remaining gates and stop condition

Genuine BLAKE3 legacy behavior; native Windows/WSL/macOS; fresh dependency resolution;
full alternative-language realization; independent security review; real deployment/custody/
clock/floor/authority validation remain open. No live transport, consensus or globally current
namespace guarantee was introduced. No external review submission or publication occurred.

A separately selected reviewer should inspect the security priorities in
`docs/release/REVIEW-HANDOFF.md` and record their own artifact-bound findings. Target-machine
operators should produce their own exact replay receipts. Do not infer approval from these
same-author records or open another feature batch merely to relabel external prerequisites.

**Authority effect NONE; G0 CLOSED; real A5 false; public release NOT_CLEARED.**
