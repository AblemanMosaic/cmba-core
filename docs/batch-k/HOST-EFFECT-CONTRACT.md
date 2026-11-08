# WB-K1 host effect contract

## Security boundary

A cryptographic assessment and a local effect are different operations. None of the I1,
J1, or K1 data interfaces exposes approve, commit, signing, payload execution, network
retrieval, trust-store update, plugin loading or publication. LocalEffects is an explicit
Python host object; the optional interactive CLI and native UI are trusted callers.
An application running arbitrary hostile Python in this process is outside this boundary.

The implemented filesystem profile assumes an operator-owned local directory, cooperating
processes and a nonhostile OS. It does not establish exclusive custody against a local
administrator, malicious kernel, network filesystem, removable-media controller, physical
power interruption, or another process capable of altering the host executable.

## State machine

UNSELECTED_DIRECTORY -> DIRECTORY_SELECTED -> PREPARED -> HOST_APPROVED -> CONSUMED

From PREPARED or HOST_APPROVED, cancellation, expiry, changed host state, replacement of
the selected directory or appearance of the target invalidates the plan. A consumed token
is never reusable, including after an I/O failure. A new plan cancels its predecessor.
There is at most one live plan per host object.

prepare(kind, value, name, ttl) performs structural output admission, canonicalization,
root-directory checks, target absence check and input-state capture. It performs NO writes.
It retains private immutable output bytes and returns a detached copy of the displayed plan.
Mutating that displayed copy does not change the bytes or target to be written.

approve(plan_hash) is a separate host action. It rechecks state, deadline, directory and
target. The returned approval is an in-process object. A JSON document containing an
approval-shaped dictionary cannot substitute for it. In the GUI the host asks an explicit
confirmation showing file, directory, byte count, digest and privacy warning. The operator
CLI requires a real terminal and exact plan-hash confirmation. These are local host controls,
not a remote identity, trusted hardware UI, human-intent proof or organizational authority.

commit(approval) checks object identity and every live precondition again, consumes the token,
and creates a fresh hidden staging file with exclusive-create semantics and mode 0600.
It writes the exact retained bytes, flushes and fsyncs the file, then rechecks directory,
input state and the captured deadline immediately before installation. os.link installs the final name only if it does not exist. There is no replace,
truncate or overwrite fallback. The staging name is removed. Where supported, the directory
is fsynced, then the final bytes are read back and compared with the plan digest.

## Paths and replacement detection

Only a flat ASCII .json basename is admitted. Path separators, traversal, drive/alternate-stream
syntax, hidden names, doubled dots and reserved Windows device names are refused. The directory
must already exist and may not contain a symlink/junction in its ancestor chain. Its device/inode
identity is retained and rechecked. POSIX hosts use a retained directory file descriptor and
relative operations where available; the portable route retains preflight/identity checks.
Neither route claims full protection against a malicious administrator racing path replacement.

A destination created by a competing writer is preserved. Even a race between final absence
checking and os.link cannot cause overwrite. Two cooperating writers for the same output name
can produce one winner and one typed refusal, not interleaved content. Readers see either no
final name or the staged complete file under the assumed filesystem semantics.

## Failure reporting

Before linking, failures attempt to remove staging and return a typed refusal. A process crash
can leave an orphan .cmba-k1-*.tmp; no automatic recursive cleanup is performed. An operator may
inspect and remove it. K1 is not a transactional database, a crash-recovery daemon, or a physical
power-loss proof.

After linking, the write has happened. Directory-fsync failure is therefore a recorded durability
warning, not a false claim of no effect. Failed readback returns LOCAL_FILE_CREATED_READBACK_INDETERMINATE.
The receipt reports output hash, plan, warnings, durability observation, host_effect=CREATE_LOCAL_FILE,
authority_effect=NONE and signature=NOT_SIGNED. NONE means no jurisdictional authority promotion;
it does not deny the explicitly reported local filesystem effect.

## Deliberate limitations

No in-place overwrite, directory creation, binary executable export, arbitrary subprocess,
network service, automatic publication, production key storage, or export grant across restart.
All output is finite canonical JSON. Caller-owned time/clock, root recognition, payload privacy
and OS custody remain explicit assumptions. A restarted process must prepare and approve again.
