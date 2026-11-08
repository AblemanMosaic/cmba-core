# ABI stability and compatibility

CMBA exposes three closed JSON request interfaces and one discovery/dispatch
envelope.

| Interface | Request schema | Legacy command | Standing |
|---|---|---|---|
| Core | `cmba.request.v0.1-i1` | `cmba` | Frozen I1 protocol |
| Application | `cmba.request.j1` | `cmba-app` | Experimental J1 protocol |
| Workbench | `cmba.workbench-request.k1` | `cmba-wb` | Experimental K1 protocol |
| Agent envelope | `cmba.agent-response.v1` | `cmba-agent` | Experimental discovery layer |

## Compatibility rules

1. Schema identifiers select exact contracts; similarly named fields do not.
2. Unknown fields and unknown operations are refused rather than ignored.
3. Existing schema identifiers will not be silently assigned new semantics.
4. Incompatible changes require a new schema identifier and conformance corpus.
5. Additive implementation capabilities are discoverable through the manifest;
   they do not expand an older request schema.
6. A distribution version identifies packaging. It is not itself a protocol
   version, binding root, evaluator identity, or authority statement.
7. Deprecation will be documented in `CHANGELOG.md` for at least one published
   alpha successor before a compatibility entry point is removed.

## Canonical transport

Requests and responses use `cmba-cjson-i1`, not RFC 8785/JCS. The admitted
grammar excludes floats, duplicate object keys, out-of-range integers,
noncanonical encodings, and values over the declared resource ceilings.

## Result and process status

Exit `0` means that the requested computation completed. It does not mean that
the inner assessment matched or that an external effect is authorized. Exit `2`
is a typed refusal. `cmba-agent` reserves exit `3` for an unexpected internal
error represented by a non-sensitive machine error code.

## Conformance

The source tree includes JSON Schemas and frozen conformance corpora under
`schemas/` and `interop/`. Passing them demonstrates agreement for those exact
cases; it does not prove whole-program equivalence, security, or authority.
