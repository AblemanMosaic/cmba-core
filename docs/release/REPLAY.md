# Replaying the frozen review candidate

Use a new working directory and explicitly selected environment. Verify the source transport
SHA-256 against an accepted external value before extraction. The archive's internal inventory
is self-consistency evidence, not an independent publisher authenticator.

## Prerequisites

Python 3.12+ (the actual executed version is in the receipt); genuine pytest, cryptography,
jsonschema, Pillow, setuptools; Node for the required small-core comparison; Tk and a display
(or Xvfb on Linux) for real GUI tests. The runtime core itself has no third-party requirement.
Nothing in the runner downloads packages or silently substitutes mocks.

```sh
python tools/package.py --verify /absolute/path/CMBA-Core-0.1.0a6-WINQUAL-r003-CANDIDATE.zip
python tools/unpack_baseline.py /absolute/path/empty-dkn-h
python tools/verify_l.py --dkn-source /absolute/path/empty-dkn-h --out /absolute/path/new-run --phase tests
python tools/verify_l.py --dkn-source /absolute/path/empty-dkn-h --out /absolute/path/new-run --phase workflows
python tools/verify_l.py --dkn-source /absolute/path/empty-dkn-h --out /absolute/path/new-run --phase audit
python tools/verify_l.py --dkn-source /absolute/path/empty-dkn-h --out /absolute/path/new-run --phase assemble
# Native replay phases are independently completed and assembled by exact identities:
for phase in collect group0 group1 group2 group3 assemble; do
  python tools/verify_native_l.py --dkn-source /absolute/path/empty-dkn-h --out /absolute/path/new-native-run --phase "$phase"
done
```

`tools/replay_l.sh` and `tools/replay_l.ps1` wrap the four CMBA phases. Native Windows needs a
prepared graphical session and Node on PATH. Windows uses explicit UTF-8 qualification and
target-specific special-file/link fixtures. Restricted runners that deny reparse-point creation
exercise a scoped synthetic branch and must keep unrestricted reparse-point replay open. Do not
rerun an output stage in place or mix outputs from changed source/environments.

Add `--require-legacy` to every phase to require genuine BLAKE3-dependent legacy tests.
Unavailable BLAKE3 returns nonzero and no completed legacy PASS. The normal current-suite
path explicitly does not claim that optional historical gate. Native v0.2 replay and legacy
v0.1 replay have different denominators.

## What assembly verifies

The staged runner binds current source/docs/model/schema/corpus/build metadata, release
boundary, predecessor inventory, Python/dependency/Node context, native files, collected
identities, JUnit results, workflow logs, conformance reports, GUI checks and model pins.
Assembly refuses missing or altered files, mixed contexts, absent mandatory legs, nonzero
exit codes, unclassified skips, errors/failures, duplicate identities, incorrect oracle
denominators and substituted result summaries. The native plan records exact `PASS`,
`NOT_APPLICABLE`, and `BLOCKED` dispositions; only three source-bound platform rules may be N/A.
It does not manufacture evidence by regenerating expectations.

## Rebuild versus replay

```sh
python tools/package.py --out /absolute/path/rebuilt-source.zip
SOURCE_DATE_EPOCH=1794009600 python -c "from setuptools.build_meta import build_wheel; build_wheel('/absolute/path/wheels')"
```

Building explicitly authors the source inventory; verification does not. Use a disposable
copy for rebuild checks. The same frozen tree must produce identical source ZIP/wheel bytes.
Fresh evidence contains new durations and paths; rerunning tests is not expected to recreate
the original evidence bytes. The original dossier and post-freeze replay remain distinct.

The separately supplied release envelope hashes the source/wheel plus post-freeze receipts
and replay evidence. Hash all listed members and verify its explicit body commitment. It is
unsigned and does not clear independent review or operator adoption.
