# Architecture and extraction boundary

CMBA is the working research architecture. CMBA Core is the reusable library. DKN and CHC
are application profiles, not authorities over each other. The optional workbench presents
capabilities; the host owns effect enforcement and recognition. The current implementation is
an experimental **I1** profile in distribution **0.1.0a1**, not a ratified universal standard.

## Five layers

1. **Core** admits finite typed values, creates canonical commitments, binds dimensions and
   references, inspects structure, and compares exact records. It has no DKN dependency.
2. **Profiles** define what dimension roles mean at one layer. Their exact contracts are
   committed; a name alone never selects a different interpretation. Unknown critical semantics
   cannot produce a successful semantic evaluation.
3. **Evaluators** recompute finite predicates. A transformation declaration is evaluated as a
   transformation only by its particular implementation. A session extractor's interpretation
   is not made true by quoting a real span.
4. **Workbench** displays data and invokes only host-installed, explicitly selected capabilities.
   Opening an object does not install a plugin, fetch a URI, update pins or execute content.
5. **Host governance/enforcement** supplies accepted roots, policies, authorities, clocks and
   resource controls; decides whether evidence is sufficient for an effect; enforces that decision.
   I1 creates no such effects or authority. An in-process Python package is not a hostile-code sandbox.

## Dimensions are roles, not an eternal taxonomy

The same document can be a semantic contract relative to one program and state relative to a
revision process. Each dimension therefore binds an identifier, role, value schema, codec,
algorithm, criticality and exact value commitment. New role names do not require a core release.
Each actual binding is finite: I1 allows 1–64 dimensions and 0–256 relations.

Older papers require object+causal dimensions everywhere. The supplied later conversation makes
application dimensions open-ended. I1 deliberately moves required dimensions into profiles and
records this as a new construction, not claimed wire compatibility with those papers. CHC's
profile requires input/rule/toolchain/output; DKN keeps its own native inventory/root rules.

## Sibling compatibility, not renaming

The Batch H ZIP/wheel and all their native commitments remain untouched under `baseline/dkn/`.
The optional CMBA adapter checks installed DKN v0.2 runtime file bytes against the frozen hashes
before using it. It invokes the actual native verifier. Its CMBA wrapper has a new root and an
explicit typed reference to the native logical root. There is no assertion that the two digests
are numerically equal or interchangeable. Reference-scheme and algorithm fields are part of
identity; a digest alone is not a universal object identifier.

For the shared codec, the admitted overlapping value grammar agrees with the DKN codec in tested
cases. I1 has its own budgets, domain prefixes and refusals. It is not a silent replacement for
DKN's codec and is not JCS. Do not extract frozen DKN modules into this package by modification
until a future compatibility program has qualified that change.

## Binding, endorsement, envelope, evaluation

The binding body contains the typed dimensions and relations; a domain-separated root commits
that body. The transmitted binding record contains the body and its root in separate fields.
No heuristic stripping of any field named `hash` occurs. Unknown fields refuse. I1 has no native
signature constructor; DKN certificates may be checked by the optional native adapter.

J's native endorsement profile is planned as body/root → detached endorsements → optional exact
envelope commitment. Signature values cannot be part of the message whose identity they sign.
A self-consistent root without an accepted external expectation is not publisher authentication.

Evaluation is another object. Its receipt commits the binding, supplied values, exact profile,
reader policy, authority/evidence snapshots, supplied time and evaluator realization, plus the
result. Changing the context creates another receipt without changing the evaluated object.
I1 records authority/evidence snapshots but does not interpret them as permission. A changed
receipt is not automatically an admissibility change; that requires J's actual policy predicates.

## Application inventory is a separate evidence class

The recovered whitepaper table has 52 rows and eight sections while its heading claims 51 and ten.
The original text remains intact. Every row is preserved as a catalogue record, not an asserted
implementation. Nineteen family records map the immediate program, explicitly distinguishing
new engineering mappings from source assertions. Missing originals stay missing; secondary review
claims do not become a substitute primary document.

No universal proof engine, cryptographic exponential dimension-security claim, quantum-resistance
claim, automatic zero-hallucination guarantee or live global authority is part of this realization.
