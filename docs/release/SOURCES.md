# Sources and evidence classes

The authoritative inputs to this batch are the exact Batch K archive and its included
normative I1/J1/K1 contracts, source, schemas and frozen corpora. The original research
papers/transcript are preserved as history; their broad security claims are not
inherited as implemented guarantees. The source-register inventory remains unchanged.

External documentation checked during L (design/API references, not test evidence):
- Node.js official Crypto API: https://nodejs.org/api/crypto.html
- CPython official JSON implementation documentation: https://github.com/python/cpython/blob/main/Doc/library/json.rst

The L Node checker uses Node's SHA-256 implementation and an originally authored,
explicit bounded parser/encoder, not a copied third-party JSON canonicalizer. It
supports signed-64-bit integers through BigInt and orders keys by Unicode scalar
values. Native JSON.parse is used only for a single string literal, never an object
whose duplicate keys or numeric values could be lost. No external source provides
certification of this project's implementation.

Evidence classes are distinguished: inherited reported results; current same-author
execution; separately written language realization; foreign cryptographic library
comparison; fresh archive extraction; installed-package execution. None alone is an
independent human/organizational security review. All release records are unsigned.
