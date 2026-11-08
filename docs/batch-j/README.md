# CMBA Batch J — bounded application-family candidate

Distribution **cmba-core 0.1.0a2**. Explicit application profile **AP-J1**, endorsement
profile **SE-J1**, disclosure profile **SD-J1**. I1 binding grammar and its four evaluators
remain unchanged. DKN Batch H remains an exact optional dependency, not rewritten code.

Start here, then read PROTOCOL-J1.md, DEVELOPER-GUIDE.md, SECURITY-AND-CLAIMS.md,
APPLICATION-DISPOSITIONS.md, ACCEPTANCE.md, and REPLAY-AND-HANDOFF.md.

## Delivered

Thirteen installed application contracts: CHC transformation graph, GenDev session,
jurisdiction/KASD, direct consent, composed admissibility, disclosure inclusion,
supplied-byte observation, two-round coordination, conflict-preserving reconciliation,
execution-record correspondence, evidence-reference trace, detached endorsements, and
native DKN report adapters. These are bounded predicates, not thirteen complete industry
products. The 52 domain cards have record templates and mappings; none is a domain engine.

Each application has a complete record commitment and separately typed commitments for
selected components. Projection values are derived from exact top-level record fields
under the pinned profile; they need not be duplicated in supplied values. The evaluator
checks every required projection. Hashing a coherent but wrong record does not validate it.

Native DKN evaluation returns **NATIVE_REPORT_COMPUTED**, not a new all-purpose PASS.
Nested reports retain their original distinctions. Other application results distinguish
MATCH_FOR_SUPPLIED_EVIDENCE, INSUFFICIENT, NO_MATCH, CONTRADICTED, and UNSUPPORTED.
No result grants permission. Every receipt remains unsigned unless a caller explicitly
wraps/endorses it through a separate construction. A signed statement also needs recognition.

## Workbench boundary

Batch J includes the callable library/JSON capability layer and a headless workbench
integration seam (`cmba_workbench.applications_j1.Applications`). The existing I1 native
GUI is preserved and replayed; it does not yet present all J1 editors or workflows. Batch K
owns integrated native pages, authoring, local save/export/import, and host effect controls.
`cmba-app` provides the current J1 command-line surface. Neither interface auto-installs code.

## Version and custody

`cmba_core.__version__` remains the frozen I1 module's original implementation label.
Use `importlib.metadata.version('cmba-core')` for the installed distribution version;
`cmba_core.j1.VERSION` identifies the new package line. This preserves all I1 runtime bytes.
The I1 semantic contract/commitment are retained exactly. Its realization binding is renewed
for the cumulative source. J1 has a separate contract/commitment/realization binding.

All release receipts are unsigned same-author engineering evidence. Local tests, alternate
crypto backend checks and clean extraction are different evidence legs, not independent
review. External platform, deployment, key custody and public release gates remain open.
