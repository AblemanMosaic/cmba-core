# Batch L findings and dispositions

This is a same-author consolidation/review. Findings do not constitute independent
approval. The full prior I/J/K record remains intact; new witnesses and run logs are
retained in `evidence/batch-l/`. No runtime cryptographic bypass is newly demonstrated
by these L findings. No CMBA/DKN runtime module or expected corpus was changed.

## L-001 — source archive path aliases (repaired)

The Batch K `tools/package.py` checker accepted a self-consistent inventory containing
both `a/b.txt` and `a//b.txt`. Those are different inventory strings but can name the same
extracted path. Root/parent traversal was rejected, but canonical path equivalence and
file/directory prefixes were not fully checked. Minimal witness: `path-alias-minimal.zip`.

The release-tool verifier now admits exact nonempty NFC path components, rejects empty,
`.` and `..` components, backslashes, drive/stream syntax, control characters, reserved
portable names, casefold aliases, and file/directory prefix conflicts. Source building
uses the same admission. This is the source-dossier profile, not a change to runtime
DKN/CMBA artifact identities. Tests cover the original witness and additional classes.

## L-002 — nonregular source-archive members (repaired)

The previous inventory checker accepted a member whose ZIP external attributes identify
it as a symbolic link. Hashing its bytes did not establish it was a regular source file.
Minimal witness: `symlink-member-minimal.zip`. This did not demonstrate execution or
exploitation of any particular extraction library.

The source profile now requires explicit regular-file metadata and the emitted stored
ZIP encoding; rejects symlink, FIFO, directory, encrypted and unsupported encodings;
and bounds archive size, count, declared expansion, individual members and manifest size.
The builder refuses FIFOs and other special files instead of silently omitting them.
These are finite admission limits, not an OS memory/CPU sandbox or hostile-writer snapshot.

## L-003 — Boolean size accepted as integer (repaired)

A one-byte member with `"bytes": true` passed the old checker because Python equates
True with 1. Minimal witness: `boolean-size-minimal.zip`. The repair requires exact
integer types and ranges, exact manifest/row fields, fixed nonauthorizing claim fields,
lowercase digests and duplicate-field rejection. The regular-metadata minimal witness
now refuses specifically with MANIFEST_SIZE_TYPE. No cryptographic collision was needed.

## L-004 — qualification scope made explicit (tooling hardening)

The L stage reader checks all directory entries (not just regular files), refuses links,
checks exact typed contexts, and compares audited result files with stage summaries.
It checks mandatory leg names/order/exit types, collected versus executed test identities,
model pins, expected corpus denominators, Node checker scope and actual GUI-check coverage.
Fixtures challenge missing, mixed, extra, modified and type-substituted evidence.

These checks detect the tested inconsistencies. A malicious producer can fabricate unsigned
logs and recompute their hashes; no claim of tamper-proof attestation is made.

## Separately written checker and retained development boundaries

The new Node small-core implementation passed the frozen 33-case I1 corpus and additional
numeric/Unicode/parser/binding cases without changing the expected outputs. It is separately
written in another language by the same author, not an independent auditor or full J1/K1 port.
Signed integers use BigInt; key ordering uses Unicode scalar values; duplicate keys are
preserved long enough to refuse. The six supported operations are explicitly enumerated.

The default package index and an explicit official-index BLAKE3 download attempt both
failed. Their logs remain retained. No mock, alternative digest or made-up legacy PASS
was substituted. The mandatory legacy runner refuses unavailable BLAKE3.

Initial broad ZIP witnesses also used unspecified metadata for their manifest member. They
remain preserved, followed by minimal witnesses with proper regular manifest metadata;
these isolate the three reported defects. This refinement is not concealed by the final pass.

## Execution-window repair

One combined native replay invocation was interrupted after completed group XML existed
but before a terminal runner receipt. It is retained as INCOMPLETE. Native replay now
has independently invokable collect/group0/group1/group2/group3/assemble legs, each
requiring a successful process exit and source-bound stage receipt. The final union must
equal the separately collected identity set; no XML-only pass is adopted.
