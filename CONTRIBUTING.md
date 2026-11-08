# Contributing

Thank you for reviewing CMBA Core. Contributions should preserve exact claim
boundaries and distinguish structural integrity from truth, authority, and
authorization.

1. Open an issue describing the problem, affected protocol, and expected claim.
2. Keep incompatible protocol changes behind a new schema identifier.
3. Add negative tests as well as successful cases.
4. Run `python tools/run_contributor_tests.py --lane core`.
5. Explain any effect, dependency, compatibility, or evidence-boundary change
   in the pull request.

Do not commit secrets, production keys, private evidence, generated virtual
environments, or rebuilt release artifacts. See
[Contributor testing](docs/CONTRIBUTOR-TESTING.md) and [ABI](docs/ABI.md).
