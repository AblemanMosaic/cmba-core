"""Host-enforced, create-only local exports. There is deliberately no JSON approval ABI.

Threat model: cooperating processes on an operator-owned local directory, not hostile
kernel/admin custody. A displayed plan is data; approval is a host-process object.
No overwrite, mkdir, trust-store edit, network operation, plugin or executable loading.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib, os, re, secrets, stat, time
from typing import Callable
from cmba_core import canonical, Refusal
from cmba_core.codec import clone
from cmba_core.errors import require
from .common import hash_value, integer

KINDS=frozenset(('bundle','receipt','workspace','disclosure','handoff','design'))
RESERVED={'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]}

@dataclass(frozen=True)
class _Approval:
    token: str
    plan_hash: str


def filename(name):
    require(type(name) is str and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\.json',name) is not None,
            'CMBA_K_EXPORT_NAME')
    require(name.split('.')[0].upper() not in RESERVED and '..' not in name,'CMBA_K_EXPORT_NAME')
    return name


def _directory(path):
    p=Path(os.path.abspath(path))
    try:
        for node in (p,*p.parents):
            require(not node.is_symlink() and not (hasattr(node,'is_junction') and node.is_junction()),'CMBA_K_WORKSPACE_SYMLINK')
        s=p.stat();require(stat.S_ISDIR(s.st_mode),'CMBA_K_WORKSPACE_KIND')
        return p,(s.st_dev,s.st_ino)
    except OSError as exc:raise Refusal('CMBA_K_WORKSPACE_IO') from exc


def validate_payload(kind,value):
    """Structural typing only; an export does not promote a stored assessment."""
    from cmba_core.bindings import exact
    from .session import admit_bundle,Workspace
    if kind=='bundle':admit_bundle(value)
    elif kind=='workspace':Workspace().restore(value)
    elif kind=='receipt':Workspace().import_receipt(value)
    elif kind=='disclosure':
        from cmba_core.j1.disclosure import verify
        require(type(value) is dict and type(value.get('header')) is dict,'CMBA_K_EXPORT_PAYLOAD')
        verify(value,expected_root=value['header'].get('disclosure_root'))
    elif kind=='handoff':
        exact(value,{'schema','body','handoff_hash'})
        require(value['schema']=='cmba.integration-handoff.k1' and hash_value('handoff',value['body'])==value['handoff_hash'],'CMBA_K_EXPORT_PAYLOAD')
    elif kind=='design':
        exact(value,{'body','blueprint_hash'})
        require(hash_value('design',value['body'])==value['blueprint_hash'],'CMBA_K_EXPORT_PAYLOAD')


class LocalEffects:
    """One host-owned pending plan. Explicit prepare -> approve -> commit, or cancel.

    current_state must be a trusted host callback, never a field from an opened object.
    Cancellation/expiry is terminal for a plan. Output bytes are retained privately.
    """
    def __init__(self,path, *, current_state:Callable[[],str], clock:Callable[[],float]=time.monotonic):
        self.path,self._identity=_directory(path);self._state=current_state;self._clock=clock
        self._pending=None;self._approval=None;self._deadline=None;self._dirfd=None
        # Use dir-relative operations where available. Portable fallback retains checks,
        # but neither route claims exclusion of a hostile administrator.
        if all(f in os.supports_dir_fd for f in (os.open,os.link,os.unlink)) and hasattr(os,'O_DIRECTORY'):
            try:
                self._dirfd=os.open(self.path,os.O_RDONLY|os.O_DIRECTORY|getattr(os,'O_NOFOLLOW',0))
                s=os.fstat(self._dirfd);require((s.st_dev,s.st_ino)==self._identity,'CMBA_K_WORKSPACE_CHANGED')
            except OSError as exc:raise Refusal('CMBA_K_WORKSPACE_IO') from exc

    def close(self):
        self.cancel()
        if self._dirfd is not None:os.close(self._dirfd);self._dirfd=None
        self._identity=None

    def __enter__(self):return self
    def __exit__(self,*_):self.close()

    def cancel(self):
        self._pending=None;self._approval=None;self._deadline=None

    def _check_directory(self):
        require(self._identity is not None,'CMBA_K_EFFECT_HOST_CLOSED')
        p,ident=_directory(self.path)
        require(ident==self._identity,'CMBA_K_WORKSPACE_CHANGED')
        if self._dirfd is not None:
            s=os.fstat(self._dirfd);require((s.st_dev,s.st_ino)==ident,'CMBA_K_WORKSPACE_CHANGED')

    def prepare(self,kind,value, *, name,ttl=120):
        self.cancel();self._check_directory();filename(name);integer(ttl,1,300)
        require(type(kind) is str and kind in KINDS,'CMBA_K_EFFECT_KIND')
        validate_payload(kind,value)
        raw=canonical(value)
        target=self.path/name
        require(not os.path.lexists(target),'CMBA_K_OVERWRITE_REFUSED')
        state=self._state();require(type(state) is str and re.fullmatch('[0-9a-f]{64}',state),'CMBA_K_HOST_STATE')
        body={'schema':'cmba.local-effect-plan-body.k1','kind':kind,'operation':'CREATE_ONLY_JSON',
          'workspace':str(self.path),'target_name':name,'workspace_identity':[str(x) for x in self._identity],
          'input_state':state,'output_sha256':hashlib.sha256(raw).hexdigest(),'output_bytes':len(raw),
          'ttl_seconds':ttl,'nonce':secrets.token_hex(16),'overwrite':False,
          'authority_effect':'NONE','host_effect':'CREATE_LOCAL_FILE','approval':'HOST_CONFIRMATION_REQUIRED'}
        plan={'schema':'cmba.local-effect-plan.k1','body':body,'plan_hash':hash_value('effect',body)}
        self._deadline=self._clock()+ttl
        self._pending=(clone(plan),raw)
        return clone(plan)

    def pending(self):
        require(self._pending is not None,'CMBA_K_NO_PENDING_EFFECT')
        return clone(self._pending[0])

    def _check_plan(self):
        require(self._pending is not None,'CMBA_K_NO_PENDING_EFFECT')
        self._check_directory()
        require(self._clock()<self._deadline,'CMBA_K_EFFECT_EXPIRED')
        require(self._state()==self._pending[0]['body']['input_state'],'CMBA_K_INPUT_CHANGED')
        require(not os.path.lexists(self.path/self._pending[0]['body']['target_name']),'CMBA_K_TARGET_CHANGED')

    def approve(self,plan_hash):
        # Only a caller-controlled GUI/CLI can call this. An opened plan cannot call it.
        try:
            self._check_plan()
            require(plan_hash==self._pending[0]['plan_hash'],'CMBA_K_PLAN_MISMATCH')
            require(self._approval is None,'CMBA_K_ALREADY_APPROVED')
            self._approval=_Approval(secrets.token_hex(32),plan_hash)
            return self._approval
        except Exception:
            self.cancel();raise

    def commit(self,approval):
        try:
            require(approval is self._approval and type(approval) is _Approval,'CMBA_K_HOST_APPROVAL_REQUIRED')
            self._check_plan();plan,raw=self._pending;deadline=self._deadline
        except Exception:
            self.cancel();raise
        # Consume before the first write. A failed attempt does not retain a reusable grant.
        self.cancel()
        name=plan['body']['target_name'];temp='.cmba-k1-'+secrets.token_hex(24)+'.tmp'
        fd=None;staged=False;committed=False;warnings=[];durability='NOT_ESTABLISHED'
        def target(n):return n if self._dirfd is not None else self.path/n
        opts={'dir_fd':self._dirfd} if self._dirfd is not None else {}
        try:
            flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_BINARY',0)|getattr(os,'O_NOFOLLOW',0)
            fd=os.open(target(temp),flags,0o600,**opts);staged=True
            with os.fdopen(fd,'wb') as f:
                fd=None;f.write(raw);f.flush();os.fsync(f.fileno())
            self._check_directory()
            require(self._state()==plan['body']['input_state'],'CMBA_K_INPUT_CHANGED')
            require(self._clock()<deadline,'CMBA_K_EFFECT_EXPIRED')
            # Atomic create-only install. POSIX hard-link creation and Windows rename
            # both refuse an existing destination; POSIX rename cannot be used because
            # it replaces the destination. The temporary file is in the same directory.
            if os.name=='nt':
                os.rename(self.path/temp,self.path/name);staged=False
            elif self._dirfd is not None:
                os.link(temp,name,src_dir_fd=self._dirfd,dst_dir_fd=self._dirfd,follow_symlinks=False)
            else:
                os.link(self.path/temp,self.path/name,follow_symlinks=False)
            committed=True
            if staged:
                try:
                    os.unlink(target(temp),**opts);staged=False
                except OSError:warnings.append('TEMP_CLEANUP_NOT_CONFIRMED')
            if self._dirfd is not None:
                try:os.fsync(self._dirfd);durability='FILE_AND_DIRECTORY_FSYNC_COMPLETED'
                except OSError:warnings.append('DIRECTORY_FSYNC_FAILED')
            else:durability='FILE_FSYNC_COMPLETED_DIRECTORY_NOT_ESTABLISHED'
            from cmba_core.cli import read_local
            try:
                observed=read_local(str(self.path/name))
                require(hashlib.sha256(observed).hexdigest()==plan['body']['output_sha256'],'CMBA_K_OUTPUT_CHANGED')
                status='LOCAL_FILE_CREATED_AND_READ_BACK'
            except (Refusal,OSError):
                status='LOCAL_FILE_CREATED_READBACK_INDETERMINATE';warnings.append('READBACK_NOT_CONFIRMED')
            return {'schema':'cmba.local-effect-receipt.k1','status':status,'plan':plan,
                'output_sha256':plan['body']['output_sha256'],'durability':durability,'warnings':warnings,
                'host_effect':'CREATE_LOCAL_FILE','authority_effect':'NONE','signature':'NOT_SIGNED',
                'claim_ceiling':'Cooperative local filesystem only; not hostile-host custody or physical power-loss proof.'}
        except FileExistsError as exc:raise Refusal('CMBA_K_TARGET_CHANGED') from exc
        except OSError as exc:raise Refusal('CMBA_K_EXPORT_IO_OR_UNSUPPORTED_FS') from exc
        finally:
            if fd is not None:os.close(fd)
            if staged:
                try:os.unlink(target(temp),**opts)
                except OSError:pass
