# Batch J security model and claim limits

## Trust inputs that remain outside the library

Accepted object/profile/policy roots, authority membership and revocation knowledge, clock,
filesystem/process custody, real instrument/calibration status, protected DKN floors, private-key
custody and institutional approval are not created by a hash or by opening a document. The
installed evaluator and optional crypto/DKN dependencies are part of the host trust base. No
runtime sandbox, universal CPU deadline or isolated signer process is provided.

The threat tests cover mutation, exact-type confusion, unsupported critical data, identity and
scope substitution, replay, missing joint approvals, signed denials, incomplete consent history,
finite graph malformation, disclosure path/salt/root substitution, source-span falsification,
config/target substitution, forged evaluation results and attempted read-ABI effects.

A full adversarial distributed deployment, malicious OS, compromised valid signer, cryptanalytic
break, human identity fraud, physical power loss or comprehensive side-channel analysis is not
established by these tests. A validly signed false statement remains possible. The evaluator
only interprets the finite supplied-view predicates actually implemented.

## Bounded claims

| Mechanism | Establishes in its selected profile | Does not establish |
|---|---|---|
| Binding and projected dimensions | Exact record and typed component commitments agree | Descriptions are true |
| SE-J1 Ed25519 | Admitted key signed the exact typed message | Key ownership is legitimate, human is independent, claim is true |
| Joint jurisdiction | Every configured requirement checked; known overlap/denials retained | Legal authority or truth of supplied facts |
| Direct consent | Matching direct grant, interval, renewal and supplied withdrawals/overrides | Informed human consent or absence of hidden revocation |
| CHC finite graph | Exact supported transformation relations recomputed | Historical compilation, general compiler correctness or homology theorem |
| GenDev / reference trace | Quotes and references match supplied source | Complete capture, original source authorship, inference or diagnosis |
| SD-J1 inclusion | Selected salted openings match the pinned tree | Encryption, unlinkability, low-entropy safety with poor salts, erasure |
| Coordination | Required recognized keys signed identical finite terms/rounds | Consensus, liveness or independence of signers |
| Reconciliation | Proposed map equals exact conflict-retaining rule result | Conflicts resolved or one global canonical state |
| Observation/execution records | Actual supplied bytes/fields and eligible signed testimony correspond | Hardware/runtime testimony is true; permission to run anything |
| DKN adapter | Real frozen native routine computed its original report | Any extra authority, freshness or payload guarantee absent from that report |
| Model/conformance | Hash/reference/test correspondence and finite output agreement | Complete semantic equivalence, independent certification |

## Specific security distinctions

* A signed grant is not an enforcing runtime. `authority_effect=NONE` and
  `authorization=EXTERNAL_DECISION_REQUIRED` remain literal output fields.
* Finite consent evidence cannot prove that an unseen withdrawal does not exist. A stale grant
  may remain eligible under a stale reader view. Application freshness requirements are external.
* Salted commitments improve the construction available for hidden openings but do not encrypt
  them. The library cannot prove a caller-supplied salt has entropy. Public demo salts are not
  secure production salts. Disclosure headers reveal count and proofs reveal selected material.
* A distinct signer key does not establish a distinct human, custodian, administrative domain,
  or honest participant. Joint approval and threshold recovery need separate deployment analysis.
* Successfully recomputing one transformation does not certify an arbitrary installed toolchain.
  Only the fixed built-in rules run here. No command or module path from input is executed.
* Metadata hashes may themselves reveal equality or support guessing. Do not put a private
  opening into a public artifact accidentally. No payload secret scrubber has been added.
* Unsigned release receipts and checksums are integrity commitments relative to trusted expected
  values. They are not self-authentication of this publisher or independent review.

## Findings and corrections during J construction

The first new-suite run retained in evidence had three failing **new test assumptions**:
(a) a native vault query was expected to be a flat result, but DKN wraps a snapshot result;
(b) a transition report was expected to repeat a namespace root, but actually reports the
active key and epoch; (c) frozen native conformance requests were mistaken for full ABI
requests instead of test envelopes. Tests were corrected against actual native interfaces;
DKN was not modified to fit them. A subsequent test correctly refused an empty discovery
query; the test now supplies a literal query. These were not DKN runtime regressions.

Construction review additionally tightened: malformed text/reference admission; native method
argument shapes; envelope policy/requirement binding; preservation of known transformation
contradiction despite another unsupported step; disclosure required-label checks; child-time
and subject equality; and typed projected-dimension correspondence. These refinements occurred
before the J1 corpus/model freeze, not as silent amendments to a released J1 contract.

A semantic review decision gives the native adapter `NATIVE_REPORT_COMPUTED` instead of lifting
successful computation into `MATCH_FOR_SUPPLIED_EVIDENCE`. Detailed native conclusions remain
inside the report. This prevents the convenience wrapper from becoming a new authority label.

## Dependency and cryptographic provenance

`j1/_key_admission.py` is byte-identical to DKN rc5 `dkn_v02/key_validation.py`. Actual private-key
operations remain in cryptography/OpenSSL. RFC 8032's first test vector and a genuine installed
libsodium cross-check are included. These cross-checks are finite implementation evidence, not
an independent security audit or a proof of the entire admission/signature system.

Primary references consulted during implementation: RFC 8032 (EdDSA); cryptography's Ed25519 API;
DSSE's typed pre-authentication construction as a comparison. J1 is not DSSE wire-compatible.
Source URLs and consultation boundary are in SOURCES.md. Existing papers' unsupported claims
about exponential multidimensional security, medical hallucination elimination, voting privacy,
patents and deployment success are NOT inherited as guarantees.

### Interrupted release replay and retained evidence

A combined replay was interrupted by the outer execution limit after its test, four workflow,
and I1 conformance legs completed. It produced no completed release receipt. Partial logs are
retained as incomplete evidence. The J1 conformance runner was changed from one subprocess per
case to at most sixteen cases in each bounded request/result group; the frozen expected corpus
was not modified. The current 53 cases pass in four groups. This is an efficiency change, not
stronger qualification or independent review. Subsequent complete replay is separately recorded.
