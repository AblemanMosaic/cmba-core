# Threats, construction findings and remaining risks

## Adversarial questions exercised

Can an opened document approve a save? Can an old result attach to a new selection? Can
one endorsement mask another missing jurisdiction? Can a saved PASS bypass replay? Can
an export overwrite an existing target, follow a symlink, outlive approval, or silently
include undisclosed values? Can an application descriptor import a handler? Can cancelled
workers proliferate? These have named tests and bounded negative outcomes.

The actual thirteen application evaluators remain unchanged. K's job is to preserve their
meaning in a host interface, not smooth away uncertainty or add implicit permission.

## Construction findings retained

K-001 — Initial native screen sizing clipped footer/status content. The layout was adjusted
to reserve the status area, reduce minimum text heights and preserve scrolling. Later native
screenshots and actual interaction checks supersede the first rendering. This is a UI repair,
not a cryptographic finding.

K-002 — A prior assessment matrix could remain visible while a newly edited context was
refused. Cancellation/refusal now clears the current matrix and labels the context state;
history remains separately available. Tests exercise a real Tk invalid-context path.

K-003 — Imported historical receipts require explicit verification marks. Restoring a snapshot
now leaves all imported results NOT_REPLAYED and selects neither an object nor reader policy.
A forged but rehashed result is rejected by replay. The stored status can be inspected as a
claim, never silently promoted to current evidence.

K-004 — Post-link uncertainty is not a no-effect failure. Directory fsync/readback warnings
are distinguished from precommit refusals. The effect receipt accurately reports that a local
file may already have been created. Fault-injection tests preserve this distinction.

These are development findings recorded with their scope, not claims of an independently
performed security audit. Raw early and final runs are retained where available.

## Unclosed boundaries

* Existing CMBA and DKN parser/resource/cryptographic assumptions remain; this batch is not a
  full re-review of their cryptography. The inherited conformance/source bytes are retained.
* Tk interaction tests on one Linux/Xvfb environment do not establish native Windows, WSL,
  macOS, accessibility tooling or high-DPI behavior.
* A read-only worker thread is not a sandbox. Cancellation discards results but cannot stop
  arbitrary Python. Only fixed installed handlers are reachable from data. No second worker
  begins until the current one exits.
* LocalEffects assumes a cooperating operator-owned local filesystem. It does not resist a
  malicious kernel/admin, guarantee network filesystem semantics, implement overwrite CAS,
  or prove power-loss durability. Unsupported exclusive-link operations refuse.
* Orphan staging files can remain after process crash; no recursive automatic cleanup or
  background service is installed. A receipt/plan hash is not authentication.
* No production signing UI, private-key persistence, automatic trust-root adoption, remote
  plugin loading, shell execution, external connector submission or live network deployment.
* Exported workspaces can contain private data. They are not encrypted or scrubbed. Inclusion
  proofs are not secrecy, unlinkability or erasure.
* The finite profile explorer and realization view cannot certify arbitrary new profiles,
  program equivalence, election/clinical/legal truth or domain-specific authorization.

## Operational integrity

An imported context can be internally valid yet chosen by the wrong party. A GUI confirmation
can be fooled by a compromised host. An external clock can be wrong. These are explicit trust
inputs, not facts established by matching SHA-256 strings. Actual deployment acceptance,
independent review, custody, recognition and fresh evidence remain separate gates.

## K-005 — test-display environment repair

The first complete K replay passed 757 tests and failed one GUI leg because the inherited DISPLAY variable named an unavailable server. The automated GUI legs now explicitly select an isolated Xvfb display when available rather than treating a nonempty DISPLAY variable as availability evidence. Actual Tk operations remain required; there is no headless-success fallback. The failed run is retained in the dossier.

## K-006 — deadline at final install

A fault-injection test advanced the host clock during staging-file fsync. The initial implementation checked the deadline before consuming approval but did not recheck it after staging; the test demonstrated an output installation after that deadline. The repair retains the original deadline and refuses before final os.link when it has expired. The regression requires staging cleanup and absence of the final file. This bounds the host check at the pre-link point, not real-time completion inside an arbitrarily delayed filesystem syscall.

## Replay/probe corrections (not runtime cryptographic defects)

The inherited DKN pytest configuration added a second quiet flag to collection, producing file counts rather than test identities. The native replay tool now overrides the inherited addopts during independent collection. The first installed K probe also used a nonexistent convenience method; it now calls the actual replay_history API. The failed collection and installed probe records remain preserved.
