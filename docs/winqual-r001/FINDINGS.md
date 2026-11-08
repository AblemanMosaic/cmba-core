# Findings and dispositions

## W001 — Windows create-only export unavailable

The a4 portable fallback attempted hard-link installation. The reviewed Windows host refused
that operation, so valid exports could not commit. The a5 realization uses same-directory
`os.rename` only on Windows. Windows refuses an existing destination; POSIX keeps hard-link
creation because POSIX rename would replace. Approval is still consumed before the first write,
temporary creation remains exclusive, and collision tests require exactly one winning writer.

## W002 — qualification harness was not target-portable

Default text encoding, very long parameter identifiers, privileged symlink creation and
`os.mkfifo` assumptions caused non-semantic Windows failures. Current tests use explicit UTF-8,
bounded identifiers, real junctions where the host permits them, scoped synthetic branch tests
where it does not, and a typed synthetic special-file stat on Windows.

## W003 — Windows junction traversal was not refused

The a4 local-file reader rejected ordinary symbolic links but did not classify Windows directory
junctions as link-like. An unrestricted replay followed a junction and failed the negative test.
The a5 reader rejects `Path.is_junction()` for the selected path and every parent. This changes
the core realization identity; J/K conformance receipts are therefore renewed. Their contracts
commit the corpus hashes, so the J1/K1 commitments are deliberately renewed. Their 28/26 counts
and operational guarantees remain, while the J-01/K-01 retention clauses are revised to disclose
the successor transition. Protocol identifiers remain stable.

## W004 — system libsodium discovery was not portable on Windows

The audit cross-check originally required `ctypes.util.find_library('sodium')`, which does not
discover PyNaCl's bundled genuine libsodium backend on Windows. The cross-check now prefers a
system libsodium and otherwise uses PyNaCl's compiled `_sodium` backend. Its package version and
binary SHA-256 are recorded, and the same 68 point-admission, 16 valid-signature and 16 mutated-
signature cases execute. This is qualification evidence, not a new runtime dependency.

## W005 — pytest 9 expands legacy unittest subtests only in the JUnit header

The exact DKN legacy suite exits successfully with 28 parent testcase elements, while pytest 9
declares 33 tests after counting five successful `unittest` subtests in the suite header. The
legacy evidence parser accepts only that exact 28/33 shape, rejects failures/skips/duplicates and
rejects every other count mismatch. The 759-case native-v02 replay retains ordinary exact identity
coverage and is reported separately.

## Preserved boundaries

The I1 semantic contract, native DKN roots and I1 small-core corpus are preserved. J1/K1
operational obligations remain stable apart from the explicit J-01/K-01 transition clauses. The audit
r001 stage-admission repairs remain active. This qualification requires and records a real Windows
junction replay, genuine legacy BLAKE3 and fresh optional dependencies. Independent review,
WSL/macOS and public release remain open.
