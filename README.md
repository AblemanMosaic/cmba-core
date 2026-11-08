# CMBA Core

CMBA Core is an experimental reference implementation of **Cryptographic
Multidimensional Binding Architecture**: a way to commit typed state,
descriptive dimensions, relationships, and exact interpretation profiles into
independently recomputable binding roots.

Version `0.1.0a7` is a public research-preview candidate. It is suitable for
experiments, interoperability work, and independent review. CMBA is a working
research architecture, not a ratified standard, production trust root, or
claim that bound metadata is true.

## What it provides

- finite canonical JSON and domain-separated SHA-256 commitments;
- typed dimensions, relationships, profile contracts, and binding roots;
- bounded evaluators with exact replayable receipts;
- I1 core, J1 application, and K1 workbench JSON interfaces;
- a unified `cmba-agent` discovery and dispatch command;
- a local workbench with effects separated from read-only assessment;
- JSON Schemas, conformance vectors, examples, tests, and release evidence.

Hashes bind exact admitted representations. They do not establish truth,
completeness, recognized authority, authorization, confidentiality, or semantic
equivalence. See [Security and claims](docs/SECURITY-AND-CLAIMS.md).

## Install

CMBA Core requires Python 3.12 or newer.

```sh
python -m pip install .
```

For development:

```sh
python -m pip install ".[dev]"
python tools/run_contributor_tests.py --lane core
```

Optional Ed25519 support uses `.[signing]`. The DKN adapter requires the exact
compatible DKN distribution and never installs or activates itself.

## Five-minute Python example

```python
from cmba_core import bind, dimension, inspect, profile_reference
from cmba_core.registry import contract

value = {"name": "example", "revision": 1}
profile = profile_reference(contract("cmba.generic"))
item = dimension(
    "description",
    "metadata",
    "example.description.v1",
    value,
    critical=False,
)
binding = bind(profile, [item])
report = inspect(binding, {"description": value})

assert report["status"] == "BINDING_STRUCTURE_VALID"
assert report["semantic_truth"] == "NOT_ESTABLISHED"
```

## Agent and CLI use

Discover the installed machine interface before sending requests:

```sh
cmba-agent version
cmba-agent manifest
cmba-agent schema core
```

Dispatch one exact canonical JSON request from a file or stdin:

```sh
cmba-agent request core request.json
cmba-agent request app -
cmba-agent request workbench request.json
```

Every successful agent response and every typed refusal is canonical JSON.
Legacy protocol-specific commands remain available as `cmba`, `cmba-app`, and
`cmba-wb`. The separate interactive `cmba-export` command is deliberately not
reachable through the agent ABI.

Read [Agent CLI](docs/AGENT-CLI.md) and [ABI stability](docs/ABI.md) before
building an integration.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Concepts and terminology](docs/CONCEPTS.md)
- [API and quickstart](docs/API-AND-QUICKSTART.md)
- [Agent CLI](docs/AGENT-CLI.md)
- [ABI stability](docs/ABI.md)
- [Applications](docs/APPLICATIONS.md)
- [Contributor testing](docs/CONTRIBUTOR-TESTING.md)
- [Current release dossier](docs/release/README.md)
- [Publication boundary](docs/PUBLICATION.md)

Historical batch dossiers are retained as evidence and may name older
distribution versions. [Document status](docs/release/DOCUMENT-STATUS.md)
distinguishes current guidance from historical records.

## Project status

The bounded offline implementation has extensive same-author qualification,
including fresh-install, Windows, POSIX-native DKN, conformance, GUI, and
reproducibility evidence. Independent security review, macOS qualification,
production key/clock custody, and full alternative-language realization remain
open. Those limits do not prevent publication as a research preview; they do
prevent stronger assurance claims.

Licensed under Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
