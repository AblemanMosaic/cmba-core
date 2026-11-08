# AP-J1 / SE-J1 / SD-J1 normative bounded protocol

## 1. Encoding and identities

Use the unchanged CMBA-CJSON-I1 grammar and budgets: 1 MiB canonical record, depth 32,
1,024 items per generic collection, 16,384 nodes, 256 KiB per string, signed 64-bit integers.
Booleans are not integers. Duplicate keys, floats, noncanonical input and unsupported types
refuse. Versioned identifiers and lowercase hex are exact; no Unicode normalization or
case folding is implied. Canonical bytes, not host-language equality, establish sameness.

J1 hashes are SHA-256 of UTF-8/ASCII `CMBA:J1:<domain>\0` followed by canonical(value).
The installed finite domain set is enumerated by `j1.common.DOMAINS`; no caller chooses a
new hash algorithm or domain by fallback. I1 binding/profile/dimension domains stay I1.
The J1 profile version is explicit in its profile reference, pinned to the whole contract.

## 2. Application records and materialized dimensions

The installed contracts are in `src/cmba_core/data/j1-profiles.json`. Every contract has
one `record` dimension and two or more typed component dimensions. The component rule is
`source_field`: null means the full record; a string means exactly that top-level field.
There is no general expression language, arbitrary property path or profile-supplied code.

`bind_application` validates the existence of selected fields and builds all commitments.
It returns the binding and `values={record: ...}`. Evaluation verifies the record commitment,
recomputes every projected dimension, checks id/role/schema/criticality against the exact
contract, and rejects coherent record/projection disagreement. Explicitly supplied component
values must also match. Unknown critical dimensions yield UNSUPPORTED. Unknown noncritical
dimensions are retained and listed as uninterpreted; they grant nothing.

## 3. Reader context and receipts

Context is exactly schema, expected_binding_root, policy, authority_snapshot,
evidence_snapshot and time. Policy pins the full profile and complete required-check list;
its finite application parameters are validated by the selected handler. Time is an integer
epoch plus a caller-declared clock source. The library does not supply a trusted clock.
Authority is a finite list of distinct public keys with exact role/jurisdiction memberships,
plus explicitly revoked keys. These are reader inputs, not facts proved by the object.

Evidence is at most 64 supplied J1 signed statements when a handler accepts evidence;
non-evidentiary profiles refuse nonempty evidence rather than laundering uninterpreted
statements into assessed results. Scope-mismatched but well-formed signed records do not
satisfy a requirement. Invalid signatures and malformed applicable statement bodies refuse.
Exact duplicate evidence records refuse; repeated keys never satisfy distinct-key thresholds.

A J1 receipt binds the I1 binding root/profile, supplied-values hash, complete context hash,
separate policy/authority/evidence/time hashes, installed evaluator source/data identity,
full result and `NOT_SIGNED`. Its receipt hash excludes itself by explicit envelope shape.
Replay recomputes evaluation under the supplied material and compares exact canonical bytes.
Changing only policy, authority, evidence or time leaves the object root unchanged while
changing the receipt. Source identity is integrity metadata, not code authenticity.

Positive predicate status is MATCH. CONTRADICTED dominates
UNSUPPORTED, which dominates INSUFFICIENT, which dominates NO_MATCH; all MATCH becomes
MATCH_FOR_SUPPLIED_EVIDENCE. Native DKN computations instead produce NATIVE_REPORT_COMPUTED:
the caller must interpret the original nested report. No status grants an operational effect.

## 4. SE-J1 statement and endorsement construction

A statement body contains exactly schema `cmba.statement-body.j1`, kind, payload,
algorithm `Ed25519`, and raw public-key hex. Sign
`b'CMBA:J1:ed25519-statement\0' + canonical(body)` with cryptography/OpenSSL.
The public statement envelope contains schema, body and signature_hex. Its record_hash is
the J1 `signed-record` digest of that exact envelope WITHOUT record_hash.

The public-key admission checker is an exact copy of DKN rc5 `key_validation.py` (provenance
recorded separately). It rejects noncanonical, off-curve, identity and non-prime-subgroup
public keys. Signature scalar S must be below Ed25519's subgroup order. Actual signatures
are verified by the genuine cryptography backend; there is no substitute crypto fallback.
This is a distinct CMBA protocol, not DSSE/Ed25519ctx and not a DKN signature format.

An endorsement-policy is a dimension with fixed id `endorsement-policy`, role
`endorsement-requirements`, and schema `cmba.endorsement-policy.j1`. Its requirements have
unique id, role, jurisdiction, action, and threshold 1..64. The dimension is committed BEFORE
signing. A public endorsement binds the resulting binding root, policy hash, exact
requirement/role/jurisdiction/action, decision endorse/reject, and half-open validity interval
[not_before, not_after). A verifier independently receives expected object/policy roots,
reader authority membership and time. All requirements must meet their threshold; applicable
recognized rejections dominate. The same recognized key can meet separate roles only when
explicitly configured for both; distinct keys are not claimed to be independent people.

An optional endorsed envelope includes the binding, its values and signatures sorted by
record hash. A separate envelope hash covers them. Adding signatures changes that envelope
hash, not the earlier binding root. Verification never treats a self-declared hash as a
trusted publisher anchor. No private-key serialization or signing operation exists in the
read-only JSON ABI; the Python authoring API receives a caller-held key object.

## 5. Application-specific predicates

### CHC finite graph

At most 64 text nodes, 32 ordered steps, 16 inputs per step. Each node declares exact UTF-8
bytes via text plus SHA-256. Steps have unique ids, one uniquely produced output, explicit
input ids, versioned rule, and expected built-in toolchain descriptor. Initial nodes are
those without a producer. Every step can use only initially available or earlier produced
nodes; cycles/missing references/unused nodes/duplicate producers refuse. Every selected
output must have a producer. Supported version-1 rules: canonical-json, identity-utf8,
concat-utf8. The evaluator actually recomputes every supported step and checks the complete
output, including intermediates. Toolchain identity is the current `transforms.py` source
hash. This proves the stated finite relation, not historical use of a compiler or all-purpose
semantic preservation. Unsupported rules cannot invoke code. Known mismatches remain
contradictions even when another step is unsupported.

### Session and claim trace

Supplied UTF-8 source, exact SHA-256, and coverage SUPPLIED_RECORD_ONLY. Events have distinct
ids, explicit attribution, byte offsets, quote, interpretation, a declared event type and
references to earlier events. Splitting a UTF-8 code point does not match a quote. Supported
event types include decisions, requirements, alternatives, uncertainty, triggers, outputs
and claims. Claim-trace adds named claims whose citation ids must resolve. Neither a correct
quote nor an existing reference establishes interpretation, entailment or claim truth.

### KASD / jurisdiction

Each required jurisdiction has id, exact role, threshold and equality constraints over
supplied facts. Approvals bind exact subject reference, action, complete terms hash,
requirement, role, jurisdiction, decision and validity. Every requirement is checked, not
just one selected approval. Overlapping constraint fields remain visible. Contradictory
required values are reported even without enough signatures. Supplied facts are not measured
reality; recognized authority is not institutional/legal legitimacy.

### Direct consent

A grant binds exact subject, requesting actor, action, jurisdiction, finite conditions,
renewal-context hash, interval, grant label, delegation_depth=0, and predecessor grant hashes
it supersedes. The issuer must be reader-recognized as consent-issuer for that jurisdiction.
Withdrawal is signed by the same issuing key, targets exact grant hash, and has an effective
epoch. Another key cannot withdraw it. A same-issuer override must retain subject/actor/action/
jurisdiction and start strictly later. Its superseded grant must be supplied. Once effective,
old grants do not revive merely because the override expires. A fresh separate grant may
renew consent. Changed renewal context requires a matching new grant. No subdelegation,
implicit scope widening or hidden freshness inference exists. Grant labels are not global ids.

### Composed admissibility

At most eight child assessments from the explicit whitelist: KASD, consent, observation,
execution-record, coordination. No recursive admissibility profile. The parent pins the
subject and complete child binding/value list; reader parameters supply exact child contexts.
Each child is re-evaluated, not accepted as a submitted PASS. Child time must equal parent
time and its returned assessed subject must match the parent subject. All required children
contribute; their scoped results and receipt hashes remain visible. Parent and child policy
changes do not rewrite the assessed artifacts or earlier historical receipts.

### Observation and execution correspondence

Observation recomputes SHA-256 and size of at most 65,536 supplied bytes, checks the exact
subject and declared instrument/method/calibration references against reader expectations,
and optionally requires recognized observer testimony over the entire record. A public
`measure_bytes` helper measures supplied memory bytes, not a file at a remote instrument.

Execution-record checking compares declared artifact/configuration/target/operation with
supplied observed fields, recomputes supplied result bytes, and requires recognized fresh
testimony over the exact record. Its age limit and validity intervals use reader time. It
never runs an executable or claims that authentic testimony proves actual runtime behavior.

### Coordination and reconciliation

Coordination has one prepare round and optionally one commit round, in that exact order.
Every required distinct participant signs the same terms hash, phase and previous-round hash
with validity interval. A round's envelope hash becomes the next predecessor. Every supplied
round is checked; a commit with incomplete preceding agreement cannot silently pass. This is
record validation, not a distributed consensus implementation or a Byzantine liveness proof.

Reconciliation accepts at most 16 snapshots with at most 64 distinct field keys total. Under
`equal-or-conflict` version 1, a key enters merged only when present and canonically equal in
all snapshots. Otherwise all snapshot-specific presence/value records remain in conflicts.
Missing is not null and true is not 1. A matching proposal may contain unresolved conflicts;
there is no automatically selected winner.

## 6. SD-J1 selective disclosure

At most 64 entries sorted by unique label. A leaf body contains schema, original index, label,
schema_id, value and 32-byte salt. Constructors generate independent random salts unless the
caller explicitly supplies them; supplied duplicate salts refuse. Salt entropy is an external
assumption, not something a verifier establishes. Leaf = J1 disclosure-leaf digest of body.
Pad to the next power of two with `disclosure-empty` digests of exact pad indices. Parent =
J1 disclosure-node digest of {left,right}. Header contains schema, leaf_count, merkle_root;
disclosure_root is J1 disclosure-root digest of the header without its own root field.

An opening supplies leaf + logarithmic sibling path. The verifier checks exact depth from
leaf_count, index range, side at every level, lowercase sibling hashes, no repeated index or
label, and expected reader root. The application also enforces required disclosed labels.
Redaction without a proof is not inclusion. Empty disclosure satisfies no required labels.
The header leaks count; a disclosed entry leaks its label/salt/value. The profile supplies
no encryption, unlinkability, original-collection completeness, erasure or access enforcement.

## 7. Native adapter and effects

DKN archive, namespace, lineage, LC-F1, SAM and DS-G1 operations invoke the actual hash-pinned
native runtime. Existing index/vault reading is a distinct Python API with an explicit
host-selected path, excluded from JSON. Its native reports are nested without redefining
their semantics. There is no auto-installation, hidden migration, pin advance, store write,
URL retrieval or arbitrary plugin path. The native code and trusted host environment remain
part of the caller's trust base. Read-only does not mean hostile-process sandboxed.
