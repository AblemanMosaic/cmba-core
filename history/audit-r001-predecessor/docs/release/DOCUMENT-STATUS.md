# Document status and compatibility

Current entry points: root README and `docs/release/`. Current distribution and external
qualification boundaries are in `RELEASE-BOUNDARY.json` and the external release envelope.

Normative unchanged runtime contracts:
- I1: `docs/PROTOCOL-I1.md`, exact `model/CONTRACT.json`, schemas and frozen `interop/core-i1.json`.
- AP/SE/SD-J1: `docs/batch-j/PROTOCOL-J1.md`, exact `model/j1/CONTRACT.json`, J1 schemas and corpus.
- WB-K1: `docs/batch-k/PROTOCOL-WB-K1.md` and `HOST-EFFECT-CONTRACT.md`, exact K1 model, schemas and corpus.

The earlier architectural and source-decision documents remain part of their committed
historical profiles. Their batch completion counts and "current" package names refer to
those batches, not the current distribution. L does not silently edit normative references
and then pretend their old model commitment still applies.

Release-tool tightening changes admission for source dossiers containing aliased paths,
nonregular ZIP members, and improperly typed manifest fields. It does not change DKN
archive admission, CMBA binding bytes, signatures, application profiles or WB-K1 effects.

Realization bindings are refreshed to bind current tools/tests/package metadata. The three
semantic contracts and commitments and all three frozen conformance corpora retain exact
Batch K bytes. Qualification evidence does not retroactively approve the historical papers'
stronger claims. Runtime data files retain their original I1/J1/K1 profile identifiers.
