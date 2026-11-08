# Exact DKN native platform coverage

The preserved DKN v0.2 suite has **1,173 exact collected identities**. `759` is a historical
CMBA inherited-test subtotal and is not a DKN native-suite denominator. Qualification compares
the complete collected identity set with the complete JUnit identity set.

Each collected identity receives exactly one disposition:

- `PASS`: the test executed successfully;
- `NOT_APPLICABLE`: only an exact identity and environment predicate listed in
  `baseline/dkn/DKN-NATIVE-PLATFORM-COVERAGE.json` may receive this disposition;
- `BLOCKED`: an exact declared environment blocker, or any undeclared skip/failure, prevents a
  passing qualification receipt.

The three bounded `NOT_APPLICABLE` conditions are absence of `os.mkfifo`, absence of POSIX
permission semantics, and presence of BLAKE3 for the test whose sole purpose is the
missing-BLAKE3 branch. They are not counted as passes. The final native receipt enumerates all
1,173 identities with their dispositions and reports separate `passed`, `not_applicable`, and
`blocked` totals. No test is filtered out of collection or silently converted from skip to pass.

On the current Windows qualification host, 11 exact symlink-defense identities are declared
`BLOCKED` when their failure begins with Windows error 1314 (the process lacks the privilege
required to create the attack-fixture symlink). These are environment-blocked tests, not passes
and not platform exemptions. A Windows receipt containing any such disposition remains
`BLOCKED`; it cannot clear the public-release gate. The same identities must execute normally in
a suitably privileged Windows environment or a POSIX qualification environment.

This plan is source-archive-specific. Its archive SHA-256 is
`c3d10a4fb42c85f01cab909b627f986fdac2198a9af6a372871d537c5ff10ee3`.
Changing the frozen native source requires a new coverage contract.
