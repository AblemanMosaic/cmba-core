# Replay and custody

The source archive has a closed FILE-MANIFEST.json covering every other member. Its transport
checksum is external. Original DKN archives and wheel bytes are pinned under baseline/dkn.
Research source bytes have independent entries in SOURCE-REGISTER.json. No receipt is signed
by an invented publisher or independent reviewer.

## Local replay

Use an environment with Python 3.12+ and genuine test dependencies. Tk/Xvfb are needed only for
the GUI smoke. The exact tested environment is in the release receipt; native Windows/macOS
qualification is not implied by a universal wheel tag.

```
python tools/unpack_baseline.py /tmp/dkn-h-reference
PYTHONPATH=src:/tmp/dkn-h-reference/src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  python -m pytest tests --junitxml=/tmp/cmba-i-tests.xml
PYTHONPATH=src:/tmp/dkn-h-reference/src python examples/first_binding.py
PYTHONPATH=src:/tmp/dkn-h-reference/src python examples/dkn_bridge.py
python tools/check_model.py --junit /tmp/cmba-i-tests.xml
PYTHONPATH=src python tools/run_conformance.py
PYTHONPATH=src xvfb-run -a python tools/smoke_gui.py \
  --out /tmp/cmba-gui.json --screenshot /tmp/cmba-gui.png
python tools/package.py --out /tmp/cmba-i-rebuilt.zip
```

On Windows use `;` for PYTHONPATH and run the GUI smoke in an actual desktop session without
xvfb-run. These are instructions, not evidence of an executed Windows leg. Tests requiring
POSIX filesystem facilities need a separately declared target-platform disposition, not a silent
skip relabeled as the same passing suite.

To rerun DKN's full v0.2 suite, select the unpacked baseline, its original test runner and its own
required dependencies. Do not modify its source or test expectations. Genuine legacy BLAKE3
remains a separate prerequisite. This session replayed DKN v0.2 tests without claiming legacy
execution or all original DKN release stages again.

## Evidence interpretation

The new suite, baseline replay, examples, GUI smoke, installed wheel, model checker, conformance
corpus and packaging replay are separate evidence legs. Counts are not combined to disguise
missing legs. A fresh extraction is repeatability evidence, not independent review. Source/wheel
reproducibility means serializing the same frozen tree with the stated build environment; logs
with timings are not promised to regenerate byte-identically.

Model/corpus/catalogue authoring tools are explicit. They must not be invoked by verification to
rewrite accepted expectations. The catalogue claims completeness only relative to the recovered
whitepaper table and explicitly mapped family list, not an unsearched global research corpus.
