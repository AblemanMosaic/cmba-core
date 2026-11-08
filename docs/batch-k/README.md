# Batch K — integrated native workbench and controlled local workflows

Distribution **cmba-core 0.1.0a3**. Workbench profile **WB-K1**. The I1 core and J1
application, signature and disclosure profiles retain their source and semantic bytes.

This is an offline engineering candidate, not independent approval or an unattended
production trust root. It adds a usable host around existing evaluators, not another
cryptographic protocol pretending to replace them.

## Read in this order

1. USER-GUIDE.md — install, pages, reader context, receipt replay, authoring and local export.
2. HOST-EFFECT-CONTRACT.md — the historical prepare/approve/commit state machine and assumptions;
   HOST-EFFECT-PLATFORM-AMENDMENT.md is the current normative installation-mechanism amendment.
3. DEVELOPER-GUIDE.md — reusable host model, pure interfaces, GUI and native DKN path boundary.
4. PROTOCOL-WB-K1.md — exact data formats, domains, budgets and outcome meanings.
5. SECURITY-AND-FINDINGS.md — limits, construction observations and known deployment gates.
6. ACCEPTANCE.md — program obligations mapped to concrete tests, including actual Tk interaction.
7. REALIZATION-AND-HANDOFF.md — preserved models, replacement evidence, replay and Batch L.
8. SOURCES.md — design references; these do not constitute validation of this implementation.

## Delivered

Ten native pages cover inspection, applications, data authoring, context/assessments,
local relationships/comparison, receipt history, selective disclosure, design/realization,
native DKN reads and controlled local import/export. Every installed J1 profile is
selectable; PUBLIC examples are explicitly demonstration fixtures. The UI renders data
as text and never treats an embedded import path or instruction as executable code.

The headless Workspace, read-only cmba-wb JSON interface and explicit LocalEffects host
are usable without Tk. LocalEffects can create a file only after a live host approves a
specific, expiring plan. A signed consent assessment cannot call that approval path.

The GUI and library have no automatic saves. The separate cmba-export operator command
requires an interactive terminal and exact plan-hash confirmation. There is no auto-yes
option and no serialized approval operation in the JSON interface.

## Evidence and limits

Exact test counts, environments, installation checks and artifact hashes are in the
external Batch K release and clean-replay receipts. The source dossier includes the
pre-freeze run and retained development attempts. Do not count reruns or conformance
cases already included in pytest a second time as new tests.

Unchanged DKN source/wheel artifacts remain under baseline/dkn. This candidate does not
establish live P2P, global freshness, domain truth, real signing custody, protected host
state, a security sandbox, or full semantic equivalence. No external review submission
or publication is performed. Public release remains NOT_CLEARED; assessment authority
remains NONE. Explicit host test writes are reported as local file effects, not hidden
behind that authority field.
