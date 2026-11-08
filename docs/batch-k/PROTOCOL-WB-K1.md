# WB-K1 normative bounded host/data profile

K1 uses the unchanged CMBA-CJSON-I1 grammar. Limits, forbidden floats, duplicate keys,
exact integer/boolean distinctions, UTF-8 and canonical ordering remain unchanged.
No existing I1/J1 hash domain or binding construction is reinterpreted.

K1 commitment: SHA-256(ASCII("CMBA:K1:" + domain + NUL) || canonical(value)). Allowed
new domains are document, workspace, task, context, effect, handoff, design,
semantic-contract and host-realization. They describe K1 objects only. Root equality
across unrelated schemes does not establish identity.

## Objects

A document is an unchanged I1 or J1 workbench bundle. document_id hashes the entire bundle,
including supplied context; two bundles can share a binding root while having different
document IDs. Their contexts remain untrusted until explicitly selected by the reader.

A workspace has schema, documents, history, trust_state=NOT_SERIALIZED and authority_effect=NONE.
Documents are exact document_id/label/bundle rows. History rows contain document_id, bundle,
context, context_source and receipt. Duplicate document IDs are refused; every bundle is
re-inspected. A restored workspace has no selected document or active context. Imported
receipt claims are not automatically recomputed; their UI verification mark is NOT_REPLAYED.

A receipt packet adds schema=cmba.receipt-packet.k1 to one history row. Its receipt remains
an unchanged I1 or J1 receipt with its original evaluator identity. Replaying uses the
original bundle and evaluation context. A forged result with a recomputed receipt hash
still fails the underlying exact re-evaluation.

A workbench task binds generation, document ID, bundle, reader context and its source. The
pending task hash is owned by the host. Results from another document, cancelled generation,
or superseded context are refused. The host-only verified-task object and export approval
have no serialized capability encoding; schemas do not provide a way to mint either.

An effect plan binds kind, CREATE_ONLY_JSON operation, exact destination directory/basename,
observed directory identity, input-state root, output SHA-256 and byte count, TTL, random nonce,
no-overwrite policy and host-approval requirement. The input-state digest commits selected
document, generation, reader context/source and current document/history identity. The GUI
also binds selected export kind/name, handoff target and disclosure/design preview state.
Monotonic expiry is local to the live process; the plan cannot be reused after restart.

A K1 local effect receipt reports the consumed plan, exact output hash, observed durability,
cleanup/readback warnings, host effect, unsigned status and authority boundary. It is not a
signed production attestation. Exact filesystem behavior is defined in HOST-EFFECT-CONTRACT.md
as amended by HOST-EFFECT-PLATFORM-AMENDMENT.md.

## Navigation and comparison

Navigation enumerates the finite admitted local collection, rechecking its bindings. A target
resolves only for scheme cmba.binding and algorithm SHA-256 with an actual locally admitted
root. Other schemes remain unresolved even when their digest bytes happen to match. Explicit
node and edge ceilings set node_limited, edge_limited and truncated. Totals distinguish the
known collection from the displayed slice. No field claims global coverage, absence or truth.
The graph is a local view of declared relationships, not a transitive grant of recognition.

Exact binding comparison is the existing core compare, augmented by exact supplied-value and
document-context equality. Neither establishes semantic equivalence. Receipt comparison first
replays both packets, then lists changed binding/profile/value/policy/authority/evidence/time/
evaluator inputs and both results. It does not infer a causal explanation from changed hashes.

## Disclosure, design and qualification

Disclosure retains SD-J1 bytes. K verifies the complete supplied opening set, selects labels,
verifies that view, and retains it separately from private inputs. Only the retained selected
view is eligible for disclosure export. Root/count/proof/selected-value disclosure is explicit.

The finite design axes and enumerated values live in views.DESIGN_FIELDS. Unsupported topology,
unbounded streams, encryption, popularity-as-authority, global-currentness and silent amendments
are reported as unsupported. Other selections name existing mechanisms and further obligations;
there is no automatic profile registration or security ranking.

Qualification compares exact declared semantic commitment, realization, corpus and claimed
results. It never launches an executable or treats those declarations as verified conformance.
Installed references are self-describing data, not independent root authentication.

## Budgets and outcomes

64 documents, 128 receipts, 256 returned graph edges, caller-selected graph node ceiling <=64,
base one-MiB canonical aggregate, at most one evaluation worker and one pending effect per host.
Maximum effect TTL is 300 seconds. GUI result deadline is 30 seconds by default. Deadline and
cancellation discard results; they do not terminate threads or promise global CPU/memory isolation.
Oversized UI rendering explicitly marks truncation; it never silently changes the verified object.

Evaluation statuses retain the original profile meaning. Imported receipt status text is distinct
from its verification mark. Local effect statuses are separate from assessment success.
Schema validation is structural only: runtime hashes, reader context, signatures, generation,
proofs, receipt replay, directory identity and host confirmation remain necessary.
