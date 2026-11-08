# Source and provenance notes

## Project sources

The complete I–L program and J scope are inherited unchanged in `docs/PROGRAM-I-L.md`.
The original user clarification that CHC and DKN are sibling applications is retained in
`sources/DKN-core-CMBA-session-transcript-2026-11-07.md`, particularly messages 039–048.
The attached review's proposals for session artifacts, overlapping jurisdictions, consent,
selective disclosure, receipt separation and explicit guarantee boundaries are retained in
`sources/Pasted text(20261108-015154).txt`. Their source text is not rewritten as a claim that
all proposed mechanisms were previously implemented. J1 constructions are engineering choices.

The historical whitepaper and mathematical framework remain in `sources/`. Source-derived
catalogue fields are retained verbatim; new profiles/mappings are explicitly engineering-authored.
The papers' domain performance, adoption, legal/patent and mathematical security claims are not
asserted as validated results. Some previously referenced underlying papers remain unavailable;
this batch does not imply that their full source was independently reviewed.

## External primary references consulted

- RFC 8032, Edwards-Curve Digital Signature Algorithm (EdDSA):
  https://www.rfc-editor.org/rfc/rfc8032
- cryptography Ed25519 signing/verification API:
  https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
- DSSE typed signing protocol (comparison only, not J1 wire format):
  https://github.com/secure-systems-lab/dsse/blob/master/protocol.md

Consulted 2026-11-07 session. Executed dependency versions, not a moving documentation page,
identify the actual tested implementation. References explain established primitives; they do
not certify the new CMBA composition or its application-level guarantees.

## Copied public-key admission

`src/cmba_core/j1/_key_admission.py` retains exact bytes from frozen DKN Batch H
`src/dkn_v02/key_validation.py`. A preservation test compares it to that pinned original.
No private-key algorithm was reimplemented. Actual signing/verification uses genuine
cryptography; a distinct installed libsodium backend provides an additional finite cross-check.
The copied code's existing notice and this provenance are retained; no new external author
approval or security certification is asserted.
