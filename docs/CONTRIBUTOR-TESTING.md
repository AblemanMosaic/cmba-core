# Contributor testing

Install Python 3.12 or newer and the development dependencies:

```sh
python -m pip install ".[dev]"
```

## Lanes

```sh
python tools/run_contributor_tests.py --lane core
python tools/run_contributor_tests.py --lane agent
python tools/run_contributor_tests.py --lane optional
```

`core` is the portable default used by CI. It covers the canonical codec,
bindings, contracts, evaluation, read-only I1 interface, and agent layer.
`agent` is a fast machine-interface lane. `optional` exercises the broader suite
with DKN, cryptography, GUI, and frozen-native preconditions. It deliberately
excludes the mutually incompatible core-only assertion that DKN is absent; that
negative case runs in `core`.

The release dossier uses stricter staged qualification runners in
`docs/release/REPLAY.md`. A normal contributor lane is not a replacement for
fresh-install, GUI, native DKN, cross-platform, reproducibility, or release
envelope evidence.

The runner creates a fresh temporary directory unless `--basetemp` names a
nonexistent path. It refuses to reuse an existing test-custody directory.
