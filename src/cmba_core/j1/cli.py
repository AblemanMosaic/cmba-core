"""Read-only J1 JSON command. Input is data, not commands to install or execute."""
import argparse,sys
from pathlib import Path
from ..codec import canonical,decode,MAX_BYTES
from ..errors import Refusal,require
from .abi import dispatch
from ..cli import read_local


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('request');args=parser.parse_args()
    try:
        if args.request=='-':raw=sys.stdin.buffer.read(MAX_BYTES+1)
        else:raw=read_local(args.request)
        require(len(raw)<=MAX_BYTES,'CMBA_BYTE_LIMIT');result=dispatch(decode(raw));code=0
    except Refusal as e:result={'status':'REFUSED','code':e.code,'authority_effect':'NONE'};code=2
    except OSError:result={'status':'REFUSED','code':'CMBA_J_IO_ERROR','authority_effect':'NONE'};code=2
    sys.stdout.buffer.write(canonical(result)+b'\n');return code
if __name__=='__main__':raise SystemExit(main())
