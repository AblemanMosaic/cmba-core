# Agent CLI

`cmba-agent` is the unified machine-facing entry point introduced in
`0.1.0a7`. It composes the existing protocol-specific ABIs without changing
their request schemas or making effectful operations agent-callable.

## Discovery

```sh
cmba-agent version
cmba-agent manifest
cmba-agent schema core
cmba-agent schema app
cmba-agent schema workbench
```

The manifest reports interfaces, exact request-schema identifiers, operations,
framing, input limit, effect class, and legacy command names. The bundled
schemas are the same bytes as the source-tree request schemas.

## Dispatch

```sh
cmba-agent request INTERFACE FILE
cmba-agent request INTERFACE -
```

`INTERFACE` is `core`, `app`, or `workbench`. Input is one exact canonical JSON
value, read to EOF, with a maximum encoded size of 1 MiB. Output is one
canonical JSON value followed by LF.

A successful dispatch uses this envelope:

```json
{
  "authority_effect": "NONE",
  "interface": "core",
  "result": {},
  "schema": "cmba.agent-response.v1",
  "status": "OK"
}
```

The explanatory layout above is not canonical. Typed refusals exit `2` and
return `status: REFUSED` with an error code. An unexpected implementation error
exits `3` and returns `CMBA_AGENT_INTERNAL_ERROR` without serializing exception
details. Computed negative results such as `CONTRADICTED`, `INSUFFICIENT`, or
`NO_MATCH` remain successful computations and therefore exit `0`.

## Effect boundary

All three dispatched interfaces are read-only/data-only. They cannot write,
publish, fetch, install, execute arbitrary code, load plugins, update trust, or
hold private keys. The interactive `cmba-export` command is excluded from the
manifest and cannot be reached through `cmba-agent`.

## Compatibility

Existing clients may continue using `cmba`, `cmba-app`, and `cmba-wb`, which
return their historical raw results. `cmba-agent` adds a stable outer response
envelope and protocol discovery; it does not reinterpret those results.
