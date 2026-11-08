# Replaying Windows qualification r001

Use a fresh evidence directory and the exact source candidate. Set no ambient pytest overrides;
the qualification runner removes them, disables plugin autoload, disables bytecode writes and
sets `PYTHONUTF8=1`. Use `tools/verify_l.py` for tests, workflows, audit and assembly, and
`tools/verify_native_l.py` for the separately staged DKN replay.

The GUI leg requires a real Tk desktop. On Windows, `verify_l.py` sets
`CMBA_REQUIRE_REAL_LINK=1`; junction creation failure is therefore a qualification failure rather
than synthetic branch coverage. Run the four phases again with `--require-legacy` to record the
genuine BLAKE3 legacy leg. Synthetic branch coverage is useful only outside the target-platform
qualification receipt.
