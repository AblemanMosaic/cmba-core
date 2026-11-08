# Threat boundaries and claim register

The new core is a bounded engineering candidate, not an independently approved security product.
Its original source papers are input research, not normative security evidence for this code.

## Claims established by executed I1 cases

* Exact admitted JSON values have deterministic canonical bytes under I1; ambiguous forms and
  unsupported values refuse. This is not every JSON format or arbitrary object serialization.
* Dimension roles, schemas, identifiers and values are bound. Binding roots commit complete
  admitted bodies. Relative to an accepted expected root, substitutions are detectable under
  the selected hash assumptions. A recomputed self-hash alone does not authenticate anything.
* Known profile contract hashes are exact; unknown profile execution and unsupported critical
  semantics do not become a successful application check.
* The CHC example recomputes one precise JSON normalization. A false output can have a valid
  binding and still be contradicted by that predicate.
* GenDev verifies recorded quote spans and attribution fields. It does NOT authenticate the
  source author, prove a recorded decision's interpretation, capture hidden reasoning, or infer
  that a partial transcript is complete.
* Evaluation receipts bind all supplied context and the evaluator realization. Exact replay
  rejects rehashed forged conclusions. Receipts are UNSIGNED and are not independent witnesses.
* The optional DKN adapter checks exact installed runtime files and calls native verification.
  Hash checking does not secure a malicious Python process/host, loader, OS or dependency.
* The workbench does not silently use document-supplied pins as reader authority. Its explicit
  demonstration mode still grants no permission and should not be substituted for trust setup.

## Deliberate limits

I1's authority and evidence snapshots are committed but not interpreted by the example predicates.
The same result may recur under different snapshots; the receipt changes because its context
changed. Do not call this full admissibility evaluation. J must implement the relevant policies.
No signature, encryption, Merkle inclusion, key custody or revocation service is newly implemented
in CMBA I1. Existing DKN capabilities remain separate, frozen and optionally invoked.

There is no payload secret scrubber. Raw source documents may contain personal paths, research
claims or private contextual material. Packaging them here for the user is not publication.
There is no compression-based privacy, unlinkability, ballot secrecy, knowledge-source truth,
compiler semantic-preservation proof, automatic consensus or exponential security from dimensions.

All local code executes under a trusted host. Python plugins are not sandboxed; I1 does not load
plugins from inputs at all. Same-process mutation, hostile administrators, malicious imported
standard libraries, TOCTOU file attacks, broken cryptography and fraudulent external pins remain
outside this bounded profile. Finite byte/node/depth limits are not universal wall-clock deadlines.

## Refusal and result classes

Structural or cryptographic mismatch raises Refusal with a stable CMBA_* code. A validly admitted
but contradicted profile statement returns CONTRADICTED. Missing required material returns
INSUFFICIENT. Unsupported profile semantics returns UNSUPPORTED or refuses unsupported profile
selection. A successful finite predicate evaluation returns MATCH_FOR_SUPPLIED_EVIDENCE. None
of these grants execution or publication authority. A comparison's same_binding field concerns
exact binding identity; same_profile is exact profile identity, not proof of semantic equivalence.

## Findings retained

I-001 SOURCE COUNT: recovered section 4.3 has 52 rows in eight sections, contrary to its 51/ten
heading. Preserve the source; record both claims and observed count. No domain completeness or
implementation proof follows from the taxonomy.

I-002 SOURCE COVERAGE: three primary research documents and two supplied session/review sources
were recovered. Five historical titles mentioned by the review were not located in this retrieval.
Their detailed findings remain attributed secondary evidence. Other editions of the admissibility
paper were not silently merged with the selected exact-name Library edition.

I-003 FILE ADMISSION: the initial new suite had 151 passes and one failure. A directory opened
through fdopen before the regular-file test yielded CMBA_INPUT_IO instead of the specified
CMBA_INPUT_KIND. Admission now uses fstat before fdopen and closes the descriptor on every early
refusal. The failed run is preserved and a regression checks the exact refusal code.

I-004 TERMINOLOGY: legacy aggregate semantic_hash, semantic-contract hash, binding-root role,
and native logical roots remain distinct. Reported alternate CHC/CPC meanings are not merged
by acronym. DKN's code identity is preserved; a CMBA reference is not a root migration.

## Sources external to the implementation

Primary comparison targets consulted: DSSE protocol (typed authenticated payload envelopes),
in-toto Statement specification (artifact subjects and typed predicates), and official Python Tk
API documentation. They motivate separation and integration boundaries, not compatibility claims
or security approval. I1 does not implement DSSE/in-toto exchange. Source URLs and retrieval context
are in SOURCE-REGISTER.json. No benchmarks or legal/patent claims were externally validated.

## Receipt evaluator identity

The I1 evaluator identity commits the installed `cmba_core` Python/JSON code and data. It does
not measure the Python interpreter, native cryptography dependency, operating system, hardware
or complete runtime environment. Replay requires that same evaluator identity and exact supplied
context. Cross-realization qualification compares normalized behavior through the separate
conformance protocol, not equality of evaluator-specific receipt hashes. Build-generated egg-info
is excluded from the source replay fingerprint; actual source changes remain included.
