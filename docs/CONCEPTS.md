# Concepts and terminology

CMBA is the working name for Cryptographic Multidimensional Binding
Architecture. The name describes a research architecture, not an adopted
external standard.

## Binding workflow

1. A value is admitted by the finite `cmba-cjson-i1` codec.
2. A typed dimension commits its identifier, role, schema, codec, algorithm,
   criticality, and admitted value.
3. A binding body combines an exact profile reference, sorted dimensions, and
   typed relations.
4. A domain-separated SHA-256 binding root commits the body. The root is stored
   beside the body and is not included in its own preimage.
5. A profile evaluator checks supplied values and bounded predicates.
6. A receipt commits the binding, context, evaluator realization, and result so
   the evaluation can be replayed exactly.

## Preferred names

- **dimension commitment**: the hash committing one typed dimension and value;
- **state commitment**: a dimension commitment whose role is object state;
- **binding root**: the aggregate commitment to the complete binding body;
- **manifest root**: an application-specific binding root for a manifest;
- **receipt hash**: the commitment to one exact evaluation and its context.

Avoid using “semantic hash” without naming its layer. A state commitment and a
binding root answer different questions.

## Profiles and applications

The core does not impose an eternal list of dimensions. A profile declares the
roles, schemas, and predicates required for one interpretation. CHC and DKN are
application profiles over the shared binding substrate; neither supplies
authority to the other.

## Claim boundary

Commitments make changes, substitutions, omissions, profile identity, and exact
replay testable. They do not prove that descriptions are true, complete,
authorized, private, or institutionally recognized.
