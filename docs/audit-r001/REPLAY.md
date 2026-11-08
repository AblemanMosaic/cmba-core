# Replaying audit r001

The repaired source retains distribution 0.1.0a4 and the original runtime wheel. Use the new
source archive checksum for source qualification; use the original wheel checksum for the
unchanged runtime. Do not mix prior L stage files with new review-tool stages.

In a prepared local environment, extract the repaired archive and run:

```sh
python tools/package.py --verify /absolute/path/CMBA-Core-0.1.0a4-AUDIT-r001-CANDIDATE.zip
python tools/unpack_baseline.py /absolute/path/empty-dkn-h
python tools/verify_l.py --dkn-source /absolute/path/empty-dkn-h --out /absolute/path/new-cmba-run --phase tests
python tools/verify_l.py --dkn-source /absolute/path/empty-dkn-h --out /absolute/path/new-cmba-run --phase workflows
python tools/verify_l.py --dkn-source /absolute/path/empty-dkn-h --out /absolute/path/new-cmba-run --phase audit
python tools/verify_l.py --dkn-source /absolute/path/empty-dkn-h --out /absolute/path/new-cmba-run --phase assemble
```

Run native phases collect, group0, group1, group2, group3 and assemble separately with
`tools/verify_native_l.py`, a distinct empty evidence directory and the same selected native
source tree. Stage outputs are create-only, not overwritten in place. Test overrides from
PYTEST_ADDOPTS/PYTEST_PLUGINS are deliberately removed; --confcutdir bounds local pytest hooks.
The verification scripts do not invoke the realization-binding authoring tool.

`--require-legacy` remains a mandatory-refusal gate without genuine BLAKE3. These instructions
are not evidence of a native Windows/WSL/macOS run. No network, installation, signing,
publication or native P/PPI registration follows from invoking the scripts.

The prior Batch L envelope still verifies the original eight artifacts, not this repaired
source. Its omitted screenshot is supplied with the audit delivery, restored from the
already bound raw replay archive. The audit's own external envelope binds the new source,
review reports, unchanged runtime wheel and raw evidence separately; all remain unsigned.
