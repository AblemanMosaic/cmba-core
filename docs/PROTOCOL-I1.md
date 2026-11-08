# CMBA I1 — normative experimental byte and verification contract

## Canonical values (CMBA-CJSON-I1)

Allowed values: null, exact boolean, exact signed 64-bit integer, Unicode scalar strings, arrays,
and string-keyed objects. Floats, nonfinite numbers, surrogate code points, host-object subclasses,
non-string keys and duplicate decoded keys refuse. Strings are NOT Unicode-normalized. Object
keys sort by Unicode scalar-value sequence, not UTF-16 units. UTF-8 encoding is direct;
JSON uses no whitespace and the escaping produced by Python's JSON encoder with ensure_ascii=False,
compact separators and sorted keys. Control characters/quote/backslash have the conventional JSON
escapes. Exact canonical bytes are required by protocol readers. Explicit authoring decode may
accept whitespace/order variants, but never duplicate keys/floats or malformed values.

Limits: 1,048,576 encoded bytes; depth 32 with root depth zero; 1,024 entries per collection;
16,384 nodes including object keys; 262,144 UTF-8 bytes per string. Preflight nesting bounds raw
JSON before parsing. These are finite input budgets, not a measured constant-time guarantee or
host memory sandbox. The final encoded-byte limit also applies after validation.

## Domain hash

For one of the closed domains D listed in `bindings.DOMAINS`:

`H_D(v) = SHA-256(b"CMBA:I1:" + D.encode("ascii") + bytes([0]) + canonical(v))`

The domain terminator is one NUL byte (integer value zero), not printable escape characters. Digests
are 64 lowercase hex characters. Unsupported domains/algorithms refuse; no downgrade fallback.
The evaluator-realization hash is separately documented below and is not an arbitrary caller domain.

## Dimension

The dimension descriptor has exactly dimension_id, role, schema_id, codec, algorithm, critical,
and value_hash. IDs use `[a-z][a-z0-9._:/-]{0,191}`. Codec is `cmba-cjson-i1`, algorithm SHA-256,
critical is a boolean. Its value hash commits `dimension-value` over the same fields except
value_hash, plus the field value containing the exact JSON value. Therefore role, schema,
criticality, codec and identifier are bound, not just the value bytes.

The full enclosing binding also commits the descriptor. This is distinct from DKN's own dimension
construction. Reusing names does not imply digest compatibility.

## Binding and references

Binding record: exactly schema=`cmba.binding.v0.1-i1`, body, binding_root.
Body: exactly schema=`cmba.binding-body.v0.1-i1`, profile, dimensions, relations.
Profile reference: exactly profile_id, profile_version, contract_hash. The hash is H_profile-contract
of the complete installed profile-contract object. Dimensions sort by dimension_id with no duplicates.
Relations sort by relation_id with no duplicates. The constructor sorts; the verifier refuses
noncanonical order rather than silently repairing an incoming body.

Relation: exactly relation_id, predicate, target. Target: exactly scheme, algorithm, digest_hex.
Only SHA-256 and BLAKE3-256 are allowed reference-algorithm labels; BLAKE3 is NOT computed by the
core. A reference is a declaration, not a fetch, proof of existence, or permission. `binding_root`
is H_binding-root(body). No other projection/exclusion mechanism exists.

An inspector checks shape, root and any supplied dimension values. Extra unbound values refuse;
a missing value and a supplied null are distinct. Optional expected_root is a caller-owned pin.
Its absence reports NOT_PROVIDED; its presence only establishes equality with that expectation.
No cryptographic signature or authority is inferred.

## Profile evaluation

Only installed built-in profile contracts/evaluators are executable in I1. The installed contract
hash must match exactly. Required dimensions need exact role/schema and critical=true. Missing
dimensions or values yield INSUFFICIENT; unknown critical dimensions yield UNSUPPORTED; unknown
noncritical dimensions remain explicitly uninterpreted. Bad commitments are refusals, not an
assessment of a different object. Invalid predicate inputs refuse.

The policy names the exact profile and its complete sorted predicate list. I1 does not allow a
caller to omit the transformation-correctness predicate while asking for a successful CHC result.
Checks return MATCH, CONTRADICTED, UNSUPPORTED or NOT_CHECKED. Result precedence is:
CONTRADICTED; then UNSUPPORTED; then INSUFFICIENT; otherwise MATCH_FOR_SUPPLIED_EVIDENCE.
The result names every predicate and every missing/uninterpreted field.

## Evaluation context and receipts

Context: schema, expected_binding_root, policy, authority_snapshot, evidence_snapshot, time.
Time contains a nonnegative signed-64-bit epoch and a clock_source identifier. It is supplied,
not observed or independently attested. Authority snapshot is an object; evidence snapshot is
an array. Both are bound but NOT_EVALUATED by I1's profile checks. They are not portable grants.

Receipt body binds: binding_root, exact profile reference, H_supplied-values(values), H_policy(policy),
H_authority-snapshot(authority), H_evidence-snapshot(evidence), H_evaluation-time(time), expected root,
evaluator identifier and realization SHA-256, exact result, and signature=NOT_SIGNED.
Receipt root is H_evaluation-receipt(body). The evaluator realization hash is SHA-256 over
`b"CMBA:I1:evaluator-realization" + bytes([0])` followed by canonical mapping of relative `.py`/`.json`
files within the installed cmba_core package to their raw SHA-256 digests, recursively sorted,
excluding __pycache__. This is code/data identification, not evidence of the code actually executing
on a trustworthy host; the caller still owns that trust boundary.

Replay validates the receipt commitment, recomputes evaluation from all original supplied inputs
and current selected evaluator, then compares exact canonical receipt bytes. An internally
rehashable forged result is not accepted. A replacement evaluator with another realization hash
produces a new receipt even when predicate results match; qualification compares the declared
behavioral obligations separately, never blindly requires equal code identity across languages.

## Authority, signatures and effect boundaries

All result authority effects are NONE; authorization remains EXTERNAL_DECISION_REQUIRED.
Native CMBA signing is NOT_IMPLEMENTED in I1. The DKN bridge can verify a provided certificate
with the frozen native DKN verifier and retains authorization=NOT_CHECKED. Receipt integrity is
not receipt authentication. Registry descriptors are trusted installed host data; manifests cannot
register code. The CLI accepts no arbitrary URLs, import paths, shell commands or write operations.

## Schemas and compatibility

Ten exported JSON Schemas describe shapes. They do not prove canonical bytes, sorted/unique
identity lists, hashes, source-span correspondence, correct transformations, code execution or
trusted clock/authority inputs. The runtime performs its specified additional checks. Unsupported
schema/profile/digest changes require a new version; no implicit coercion to a historical CHC/DKN
meaning is permitted. This profile is an engineering candidate and can change only with an
explicit successor/migration decision and preserved old evidence.
