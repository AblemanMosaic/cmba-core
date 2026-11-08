# CMBA Core — current review dossier (Batch L)

Distribution **0.1.0a4**. Runtime profiles: **I1**, **AP-J1**, **SE-J1**, **SD-J1**, **WB-K1**.
This closes the planned I–L construction program for the explicitly bounded offline scope.
It does not clear independent review, target-platform, deployment, or public-release gates.

| Document | Purpose |
|---|---|
| [USER-AND-INTEGRATION.md](USER-AND-INTEGRATION.md) | Install, use, integrate and interpret results |
| [CLAIMS-AND-ACCEPTANCE.md](CLAIMS-AND-ACCEPTANCE.md) | Current scope and evidence limits |
| [REPLAY.md](REPLAY.md) | Staged source-bound operator replay |
| [REPLACEMENT-QUALIFICATION.md](REPLACEMENT-QUALIFICATION.md) | Model/realization separation and language-neutral conformance |
| [FINDINGS.md](FINDINGS.md) | Preserved failures, repairs and scope |
| [SECURITY-AND-REVIEW.md](SECURITY-AND-REVIEW.md) | Trust assumptions and independent reviewer worklist |
| [MIGRATION-AND-ROLLBACK.md](MIGRATION-AND-ROLLBACK.md) | Explicit version selection and rollback boundaries |
| [DOCUMENT-STATUS.md](DOCUMENT-STATUS.md) | Normative specifications versus historical dossiers |
| [COMPONENT-INVENTORY.json](COMPONENT-INVENTORY.json) | Observed dependencies/toolchains; no vulnerability-scan claim |
| [SOURCES.md](SOURCES.md) | Primary project inputs and external API references |

The exact current source ZIP, wheel, replay evidence and model commitments are bound by
the separately supplied **CMBA-BATCH-L-RELEASE-ENVELOPE.json**. It is unsigned. Its own
binding root excludes its self-declaration by an explicit body/envelope structure.
Checksums are useful only relative to accepted expected values. They do not authenticate
a publisher simply because the downloaded file repeats the same hash.

The app inventory contains 71 records (52 historical domain rows and 19 family mappings),
not 71 working domain applications. Thirteen J1 evaluators and four I1 profiles are bounded
implementations; existing application and profile contracts specify their exact meaning.
