"""Explicit local file input or stdin; canonical protocol output and typed refusals."""
from pathlib import Path
import argparse
import os
import stat
import sys
from .codec import decode, canonical, MAX_BYTES
from .errors import Refusal, require
from .abi import dispatch


def read_local(path: str) -> bytes:
    p=Path(os.path.abspath(path))
    for node in (p,*p.parents):
        link_like=node.is_symlink() or (hasattr(node,'is_junction') and node.is_junction())
        require(not link_like,'CMBA_INPUT_SYMLINK')
    flags=os.O_RDONLY|getattr(os,'O_BINARY',0)|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0)
    fd=None
    try:
        fd=os.open(p,flags)
        before=os.fstat(fd);require(stat.S_ISREG(before.st_mode),'CMBA_INPUT_KIND')
        require(before.st_size<=MAX_BYTES,'CMBA_BYTE_LIMIT')
        with os.fdopen(fd,'rb') as f:
            fd=None
            data=f.read(MAX_BYTES+1);after=os.fstat(f.fileno())
            require(len(data)<=MAX_BYTES,'CMBA_BYTE_LIMIT')
            require(before.st_size==after.st_size==len(data) and before.st_mtime_ns==after.st_mtime_ns,'CMBA_INPUT_CHANGED')
            return data
    except OSError as exc:raise Refusal('CMBA_INPUT_IO') from exc
    finally:
        if fd is not None:os.close(fd)


def main(argv=None):
    parser=argparse.ArgumentParser(description='CMBA I1 read-only request processor')
    parser.add_argument('request',help='canonical request file, or - for stdin')
    args=parser.parse_args(argv)
    try:
        raw=sys.stdin.buffer.read(MAX_BYTES+1) if args.request=='-' else read_local(args.request)
        result=dispatch(decode(raw));code=0
    except Refusal as e:
        result={'status':'REFUSED','code':e.code,'authority_effect':'NONE'};code=2
    sys.stdout.buffer.write(canonical(result)+b'\n')
    return code
if __name__=='__main__':raise SystemExit(main())
