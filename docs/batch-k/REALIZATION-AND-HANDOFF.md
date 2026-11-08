# Models, replay and the Batch L boundary

I1 and J1 semantic contract/commitment/corpus bytes are preserved. All inherited runtime code
and installed core data remain exact. No old receipt is rewritten. Because K adds only to the
workbench package, cmba_core.evaluation.realization_identity remains unchanged. The new K host
has its own source/model binding and cannot inherit approval from that identity.

model/k1/CONTRACT.json describes finite WB-K1 obligations, assumptions, reference hashes and
exclusions. COMMITMENT.json identifies that exact contract. REALIZATION-BINDING.json separately
binds implementation/tests and their named evidence references. Source hash/test-symbol checking
and recorded successful tests establish traceability, not whole-program semantic equivalence.

The existing base/J realization bindings are deliberately refreshed for the cumulative build
metadata and test tools; their semantic commitments do not change. Old bindings are preserved
in history. Verification never calls the authoring tools that regenerate models or corpus values.

A replacement must preserve exact canonical values, refusal behavior, context isolation, stale
result disposal, no-overwrite effect semantics, disclosure exclusions and imported-receipt status.
Passing the read-only  K corpus does not establish GUI, filesystem, concurrency, or platform
semantics; those require their own tests and threat-model review. A different filesystem/toolchain
can be used only with renewed evidence for the same stated properties and explicit changed limits.

## Replay in a prepared environment

```sh
python tools/unpack_baseline.py /path/to/empty-dkn-source
python tools/verify_k.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase tests
python tools/verify_k.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase workflows
python tools/verify_k.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase audit
python tools/verify_k.py --dkn-source /path/to/empty-dkn-source --out /path/to/new-run --phase assemble
```

The audit separately executes the frozen conformance interfaces, native GUI smoke and model
checks. Tests require an actual display or Xvfb; a missing GUI prerequisite is a failed gate,
not a skipped PASS. Native dependencies must be genuine and explicitly provided. Replay does
not install them. A full separately recorded native DKN suite leg is available in verify_native_k.py.

Phases pin the source fingerprint and environment. Assembly checks all required logs/results
against their stage receipts, not merely a total test count. External post-freeze clean replay
remains outside the source archive to avoid circular final hashes. Deterministic rebuild means
serializing the same frozen tree; regenerated timings/absolute paths need not recreate that tree.

## Stop after K construction; L is qualification

L audits integrated model/schema/code/result/effect correspondence, expands hostile conformance
and cross-language checks, consolidates packaging/dependencies/migration documentation, and
produces one frozen review dispatch. It is not another feature batch. Neither K nor L can turn
an unexecuted target machine, missing genuine legacy dependency, unsigned self-review or simulated
human confirmation into independent security approval.

No automatic external Courthouse submission is authorized. All integration envelopes are local
reference material. Public release remains NOT_CLEARED; operational recognition remains external.
