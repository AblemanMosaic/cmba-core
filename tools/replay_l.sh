#!/bin/sh
# Operator instructions; no automatic dependency installation or external publication.
set -eu
if [ "$#" -ne 2 ]; then echo 'Usage: sh tools/replay_l.sh ABSOLUTE_NATIVE_DKN_SOURCE ABSOLUTE_NEW_EVIDENCE_DIRECTORY' >&2; exit 2; fi
for phase in tests workflows audit assemble; do
    python tools/verify_l.py --dkn-source "$1" --out "$2" --phase "$phase"
done
# Genuine legacy availability is a separate mandatory gate:
# python tools/verify_l.py --dkn-source "$1" --out "$2-legacy" --phase tests --require-legacy
