# CMBA Core + Binding Workbench — Batch I

**Distribution 0.1.0a1 · Experimental profile I1 · Authority effect NONE**

A separate successor workspace preserving the DKN Core 0.2.0rc5 Batch H release exactly.
The core creates and inspects finite typed multidimensional bindings. Optional application
evaluators and a native local workbench keep commitments, evidence, interpretation and authority
separate. This is a working engineering foundation, not the completed I–L program.

## Start

- Full minimal-turn program: [docs/PROGRAM-I-L.md](docs/PROGRAM-I-L.md)
- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Install, library API and GUI: [docs/API-AND-QUICKSTART.md](docs/API-AND-QUICKSTART.md)
- Exact byte protocol: [docs/PROTOCOL-I1.md](docs/PROTOCOL-I1.md)
- Application inventory: [docs/APPLICATIONS.md](docs/APPLICATIONS.md)
- Sources and discrepancies: [docs/SOURCES-AND-DECISIONS.md](docs/SOURCES-AND-DECISIONS.md)
- Security and findings: [docs/SECURITY-AND-CLAIMS.md](docs/SECURITY-AND-CLAIMS.md)
- Model and replacement realization: [docs/MODEL-AND-REPLACEMENT.md](docs/MODEL-AND-REPLACEMENT.md)
- Current batch findings and next gate: [docs/BATCH-I-HANDOFF.md](docs/BATCH-I-HANDOFF.md)
- Verification/replay: [docs/REPLAY.md](docs/REPLAY.md)

```
python -m pip install ./cmba_core-0.1.0a1-py3-none-any.whl
cmba-workbench
```

The wheel is supplied separately from this source archive. The core has no third-party runtime
dependency. The GUI requires Tk and a graphical desktop. The optional DKN bridge needs the exact
bundled DKN wheel and its genuine dependencies, installed explicitly. No public package registry
availability is assumed. No command has been run on the user's machine.

Implemented: canonical codec, typed bindings/references, inspection/comparison, pinned built-in
profile contracts, finite profile predicates, exact context-bound unsigned receipts/replay,
closed read-only JSON CLI, native read-only workbench, frozen DKN adapter, actual bounded CHC
transform check, attributed GenDev source-span checks, and a source-backed application catalogue.

The catalogue contains 52 historical domain rows and 19 cross-cutting family records. Most are
not implemented applications. Each records its implementation/disposition separately; presence
in the catalogue does not authenticate a historical claim or supply a domain security guarantee.

Batch J adds bounded application-family evaluators; K integrates the full workbench workflows;
L freezes and qualifies the package. I introduces no native CMBA signing, disclosure proofs,
real compiler pipeline, live network deployment, new authority or independent approval.

Progress is recorded in `PROGRAM-LEDGER.json`; `docs/PROGRAM-I-L.md` is the complete construction and qualification program. Programme entries are scope/status records, not independent approval.
