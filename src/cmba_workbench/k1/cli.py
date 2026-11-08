"""Read-only K1 JSON CLI and a separate, interactive operator-only export command."""
import argparse,sys,hashlib
from cmba_core import canonical,decode,Refusal
from cmba_core.cli import read_local
from cmba_core.codec import MAX_BYTES
from cmba_core.errors import require
from .abi import dispatch


def main(argv=None):
    p=argparse.ArgumentParser(description='CMBA K1 read-only workbench interface');p.add_argument('request');a=p.parse_args(argv)
    try:
        raw=sys.stdin.buffer.read(MAX_BYTES+1) if a.request=='-' else read_local(a.request)
        result=dispatch(decode(raw));code=0
    except Refusal as e:result={'status':'REFUSED','code':e.code,'authority_effect':'NONE'};code=2
    sys.stdout.buffer.write(canonical(result)+b'\n');return code


def export_main(argv=None):
    """Explicit operator command, never reachable via dispatch. No unattended auto-yes."""
    from .effects import LocalEffects,KINDS
    p=argparse.ArgumentParser(description='Operator-selected create-only JSON export; interactive approval required')
    p.add_argument('input');p.add_argument('--workspace',required=True);p.add_argument('--name',required=True)
    p.add_argument('--kind',choices=sorted(KINDS),required=True);a=p.parse_args(argv)
    try:
        require(sys.stdin.isatty(),'CMBA_K_OPERATOR_TTY_REQUIRED')
        raw=read_local(a.input);value=decode(raw)
        state=lambda:hashlib.sha256(read_local(a.input)).hexdigest()
        with LocalEffects(a.workspace,current_state=state) as host:
            plan=host.prepare(a.kind,value,name=a.name)
            print(canonical(plan).decode())
            print('Exact payload is not scrubbed or encrypted. Existing files will never be overwritten.')
            answer=input('Type the full displayed plan_hash to approve; anything else cancels: ').strip()
            require(answer==plan['plan_hash'],'CMBA_K_OPERATOR_CANCELLED')
            result=host.commit(host.approve(answer))
        print(canonical(result).decode());return 0
    except (EOFError,KeyboardInterrupt):print('CANCELLED');return 2
    except Refusal as e:print(canonical({'status':'REFUSED','code':e.code,'authority_effect':'NONE'}).decode());return 2
if __name__=='__main__':raise SystemExit(main())
