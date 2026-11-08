# WB-K1 host-effect platform amendment

This amendment is normative for CMBA Core `0.1.0a5` and later successors that retain the
current WB-K1 implementation. It preserves `HOST-EFFECT-CONTRACT.md` as the historical K1
contract and replaces only that document's claim that `os.link` is the installation mechanism
on every platform.

## Create-only installation

The staging file and final target are in the same admitted directory. Immediately before
installation, WB-K1 rechecks the directory identity, input state, target absence, and deadline.

- On POSIX, WB-K1 creates the final directory entry with `os.link`. Link creation fails if the
  destination exists. After installation it removes the staging name.
- On Windows, WB-K1 calls same-directory `os.rename`. Python's Windows `os.rename` contract
  raises `FileExistsError` when the destination already exists; WB-K1 does not call
  `os.replace`, delete the destination, truncate it, or retry with an overwriting operation.
  The successful rename consumes the staging name.

A competing destination is preserved and reported as `CMBA_K_TARGET_CHANGED`. Other
installation failures are reported as `CMBA_K_EXPORT_IO_OR_UNSUPPORTED_FS`; they do not trigger
an overwrite fallback. Before successful installation, cleanup attempts remove only the fresh
staging name. After successful installation, readback or directory-durability uncertainty is
reported as an actual local effect rather than as no effect.

These mechanisms provide the same bounded create-only state transition under the existing
operator-owned, cooperating-process filesystem assumptions. They do not claim hostile-kernel,
network-filesystem, administrator, physical-power-loss, or cross-restart custody.
