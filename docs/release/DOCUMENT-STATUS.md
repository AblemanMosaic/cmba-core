# Document status and compatibility

Current entry points: root README and `docs/release/`. Current distribution and external
qualification boundaries are in `RELEASE-BOUNDARY.json` and the external release envelope.

The 0.1.0a7 public-research-preview successor adds repository policy, agent discovery/dispatch,
public onboarding, and contributor CI. It preserves the protocol-specific I1/J1/K1 request
schemas. The 0.1.0a6 WINQUAL-r003 evidence remains predecessor qualification rather than being
relabeled as an a7 execution.

Normative unchanged runtime contracts:
- I1: `docs/PROTOCOL-I1.md`, exact `model/CONTRACT.json`, schemas and frozen `interop/core-i1.json`.
- AP/SE/SD-J1: `docs/batch-j/PROTOCOL-J1.md`, exact `model/j1/CONTRACT.json`, J1 schemas and corpus.
- WB-K1: `docs/batch-k/PROTOCOL-WB-K1.md`, historical `HOST-EFFECT-CONTRACT.md`, and current
  `HOST-EFFECT-PLATFORM-AMENDMENT.md`, exact K1 model, schemas and corpus.

The earlier architectural and source-decision documents remain part of their committed
historical profiles. Their batch completion counts and "current" package names refer to
those batches, not the current distribution. L does not silently edit normative references
and then pretend their old model commitment still applies.

Release-tool tightening changes admission for source dossiers containing aliased paths,
nonregular ZIP members, and improperly typed manifest fields. It does not change DKN
archive admission, CMBA binding bytes, signatures, application profiles or WB-K1 effects.

Realization bindings are refreshed to bind current tools/tests/package metadata. I1's semantic
contract, commitment and corpus retain exact predecessor bytes. J1/K1 retain their obligation
counts, operational guarantees and protocol identifiers, but J-01/K-01 now disclose the successor
transition. They receive new contracts and commitments because their
renewed conformance corpora are contract references. Qualification evidence does not retroactively
approve the historical papers' stronger claims.

Post-L audit r001 adds current process posture and tool-admission corrections under
`docs/audit-r001/`. Normative application contracts and historical dossiers remain unchanged.
The 0.1.0a5 wheel superseded a4 for Windows junction refusal and create-only export repairs.
The 0.1.0a6 candidate supersedes a5 only for qualification admission, portable packaging,
platform coverage, evidence binding, and the normative platform amendment.
The 0.1.0a7 candidate supersedes a6 only for publication packaging and the additive agent wrapper.
The I1 semantic contract and small-core corpus remain exact. J/K conformance corpora, their
corpus-bound semantic commitments and all realization bindings are renewed.
