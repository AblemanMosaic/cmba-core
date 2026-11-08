# Constitutional contract and replacement realization

`model/CONTRACT.json` states the finite Batch I obligations, their normative references and
exclusions. `model/COMMITMENT.json` commits that contract. `model/REALIZATION-BINDING.json`
separately binds implementation/test/tool bytes and obligation-to-test references. Verification
checks these records; it does not regenerate the accepted model to fit the current implementation.
The three frozen DKN contracts and their commitments remain inside the unchanged baseline ZIP.

The model explicitly distinguishes described application families from available evaluators.
It preserves source provenance, the read/effect boundary, unknown-critical semantics and unsigned
receipt limits. A new realization may target the same contract with different source/toolchain
identity, but must establish its own behavior and evidence. Preserving a contract hash is not proof
that the new code meets the contract.

Replacement workflow: pin accepted contract/schema/vector versions; supply the frozen fixtures to
a host-authorized local implementation; compare exact canonical results and refusals; run independent
negative cases; compare effect and resource behavior; bind new source/build/evidence separately;
obtain the applicable recognition decision. Do not regenerate expected output to make a port pass.

Receipt realization hashes intentionally differ across implementations. Do not test whole-program
port equivalence by requiring the same realization hash. Test predicate behavior, commitment bytes,
context binding, exact result types, failure interpretation and authority boundaries; then issue new
receipts naming the new evaluator. The I1 conformance corpus focuses on stable core outputs so its
expectations do not depend on this Python package's source hash. A later expanded conformance
contract must explicitly distinguish invariant result fields from realization-specific identity.

`tools/check_model.py` verifies file hashes, cited test functions and optionally successful current
JUnit cases. It is traceability, not a proof of all possible executions or of external source truth.
The alternative-language realization and independent review are Batch L/external obligations, not
implicitly fulfilled by writing the model in JSON.
