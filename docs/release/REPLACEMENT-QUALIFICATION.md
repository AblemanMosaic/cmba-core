# Qualifying a replacement realization

Keep definition, implementation, evidence and adoption separate. The model commitment
identifies one exact declared contract, not abstract meaning independent of representation.
Matching that commitment does not prove the implementation obeys it.

Pin the exact I1/J1/K1 semantic contracts, normative byte specifications, schemas, frozen
corpora and result/refusal vocabularies. The existing Python code is a reference realization,
not the sole definition of correctness. A replacement gets its own source/build/toolchain
binding and renewed evidence; it does not inherit acceptance or force an upgrade.

## Existing portable surfaces

- I1: 33 complete-result/refusal cases; six operations: canonical, decode, dimension, bind,
  inspect, compare.
- J1: 53 application/crypto/disclosure/native cases with exact typed response comparison.
- K1: 42 headless workbench cases; storage/GUI/host effects additionally require direct tests.

All expected values remain frozen from the prior batches. The runner invokes an explicitly
selected local executable; it does not sandbox that executable. Do not regenerate expected
answers merely to make a port pass.

```sh
python tools/run_conformance.py --command node interop/node-l1/core.mjs
python tools/run_j_conformance.py --command /reviewed/path/application-port
python tools/run_k_conformance.py --command /reviewed/path/workbench-port
```

The latter two commands illustrate external candidate executables; none is supplied as a
full independent J1/K1 implementation.

## What the new Node implementation establishes

A separately written small core computes all six I1 operations without importing Python,
calling its implementation, or reading expected results. It has explicit finite parsing,
duplicate-key rejection, signed-64-bit BigInt integers, Unicode scalar key order and typed
commitment construction. The frozen I1 cases and additional numeric/Unicode/mutation and
seeded-binding checks compare exact canonical envelopes.

This is same-author cross-language evidence, not independent review. It does not implement
J1 applications, WB-K1 GUI/storage/host effects, DKN, signatures or the entire protocol.
It is supplied as qualification source, not silently substituted as the production runtime.
Use independent tests and security review before adopting any replacement.

## Failure classes that must survive a rewrite

No bool/int coercion; no missing/null collapse; no duplicate-key last-wins parsing; exact
codec/domain/profile identifiers; exact output and refusal envelopes; unknown critical
semantics cannot match; required evidence cannot disappear; negative evidence retains
precedence; stale receipts do not become fresh permissions; output effects need independent
host approval; traversal limits remain visible; profile data never becomes an import path.

Storage/GUI and process assumptions need new tests on the new substrate. SQLite behavior
cannot be inherited by choosing another database; a GUI confirmation is not a trusted UI
against a compromised OS. Preserve the externally visible semantic contract or explicitly
version a changed one. The 72-obligation traceability checks are not a universal equivalence
proof and do not establish real-world legitimacy or domain truth.
