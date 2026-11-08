# Post-L findings and dispositions

## R001 — P/PPI process posture omitted from current consolidated documentation

**Finding:** the original DKN session explicitly reported SIDECAR_PARTIAL. The current CMBA
release has a program ledger, acceptance/model maps, and local staged test runners. It does
not contain a native P/PPI program/interpreter/validator receipt or prove all agent effects
passed through such a host. The shipped handoff itself reports REFERENCES_ONLY,
operational_integration=NOT_ESTABLISHED and EXTERNAL_DECISION_REQUIRED.

**Disposition:** corrected current documentation and machine-readable PROCESS-POSTURE.json;
added a native admission work order. Actual native admission/host enforcement remains OPEN.
This finding does not erase the measured software tests. The process description is not a
newly ratified native mode, and historical work is not retroactively relabeled enforced.

## R002 — release delivery was not a closed transport set

**Finding:** the accessible delivery had seven of eight envelope-listed members. The missing
CMBA-BATCH-L-WORKBENCH.png was recoverable at clean-replay/audit/workbench.png in the exact,
already committed CMBA-BATCH-L-CLEAN-REPLAY-EVIDENCE.zip. This was an outer delivery omission,
not evidence that the screenshot's bytes never existed or were newly generated in the audit.

**Disposition:** recovered the identical 145102 bytes with SHA-256
1ad120ffae2a4935e0e3369a1b7ab0232949735083883593692d5b8c10ed281b. The original envelope was not
edited. Its eight listed artifacts now verify. Include the entire delivery directory when
transferring; a link in prose is not proof that the file was actually supplied.

## R003 — native source preservation did not exclude additional collection hooks

**Finding:** verify_l.native_inventory compared all 668 expected files but did not reject
extra files outside src. Adding a root conftest.py to a disposable DKN extraction removed
one known test: collection returned 1172 rather than 1173, while inventory still returned
PASS. The witness does NOT show that historical evidence used this contamination; the clean
original replay reproduced all 1173 tests.

**Disposition:** closed noncache native file-set validation before collection; reject links,
special files and executable source disguised as cache data. Hash root test configuration
in the CMBA phase context, clear ambient explicit pytest plugin/argument overrides, and set
--confcutdir to the selected source root. Native phases now bind the fuller qualification
context; assembly also checks collection terminal status and exact group-count summaries.

This is reproducibility/source-admission hardening under a trusted local interpreter/OS.
It is not a sandbox against an attacker controlling Python, cache bytecode, the kernel,
all evidence files, or the reviewer. Ordinary generated caches remain explicitly excluded.

## R004 — stage headers and duplicate JSON fields could be silently normalized

**Finding:** on copies of real successful stage evidence, replacing the tests stage schema
with foreign.success.v99, changing authority_effect to EXECUTE, or supplying duplicate
status fields (FAIL followed by PASS) still yielded the final scoped PASS. No execution
authority was actually granted by these probes; the defect is acceptance and suppression
of inconsistent qualification metadata.

**Disposition:** exact stage field/schema/phase/type/claim checks; strict bounded JSON loading
rejecting duplicate keys and unsupported numeric representations; exact terminal-leg checks.
Raw pre-repair witnesses are retained. A successful self-consistent unsigned receipt still
is not proof that a hostile producer ran the claimed computation.

## Interrupted audit invocation

One initial combined native replay call was terminated by the outer tool window without a
terminal receipt for group2. It was not counted as complete. The incomplete attempt was
retained, and the local non-external test group was rerun under a distinct capture before
native assembly. Streaming container sessions were unavailable; no successful run was
inferred from that tool error.

## Scope left unchanged

No runtime evaluator or host-effect implementation changed in this audit. No new native
P/PPI engine was invented, no missing Windows/BLAKE3/independent-review result was relabeled
PASS, and no expected behavioral conformance output was rewritten.
