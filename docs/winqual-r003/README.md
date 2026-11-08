# Windows qualification r003

This is a bounded evidence-closure successor to r002. It adds no CMBA runtime feature and does
not revise the I1, J1, or K1 semantic commitments.

The GUI witness is captured only after raising the real Tk Workbench, and the resulting pixels
must contain the Workbench's required native palette before the PNG is written or hashed. The
GUI receipt binds the validated PNG hash. This prevents an unrelated foreground window from
being accepted as the Workbench's visual witness.

Each required legacy BLAKE3 replay now records its child process terminal exit code explicitly,
in addition to binding JUnit, stdout, and stderr. Fresh-install terminal stdout, stderr, command,
and exit evidence belongs in the outer delivery envelope rather than being implied by a package
inventory.

The source archive and containing delivery directory remain different exact envelopes. No
publication, deployment, independent acceptance, authentication, native P/PPI admission, or
authority grant follows. Public release remains `NOT_CLEARED`.

See [FINDINGS.md](FINDINGS.md) for the exact closure map.
