# Windows qualification r001

Distribution `cmba-core 0.1.0a5` is a bounded successor to audit-r001. It preserves the I1
semantic contract and small-core corpus. The local-file reader now rejects Windows junctions.
WB-K1's create-only export installation uses same-directory `os.rename` on Windows, whose
no-replacement behavior is tested, while POSIX retains hard-link installation. J/K conformance
receipts are renewed because they bind evaluator realization identity. Since the J1 and K1
contracts commit those corpora by hash, their commitments are also deliberately renewed. Their
28/26 counts and operational guarantees remain, while J-01/K-01 are explicitly revised to describe
the successor transition rather than falsely promise exact predecessor-byte retention.

The qualification harness uses explicit UTF-8 mode, bounded pytest identifiers, Windows-aware
special-file fixtures and link/junction negative tests. General restricted test runs may use a
narrowly scoped synthetic branch, but the Windows qualification runner requires a real junction.
The independent-library Ed25519 cross-check prefers system libsodium and can use PyNaCl's compiled
genuine libsodium backend while recording its package version and binary hash.

No native P/PPI admission, independent approval, publication, deployment, network effect or
authority grant follows from this review. Public release remains `NOT_CLEARED`.
