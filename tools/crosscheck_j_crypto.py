"""Explicit local cross-check against installed libsodium; no alternate Python mock."""
from pathlib import Path
import ctypes,ctypes.util,hashlib,json,sys,argparse,importlib.metadata
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from cmba_core.j1.demo import fixture_key
from cmba_core.j1.endorsements import public_key,seal,SIGN_DOMAIN,admitted_public_key
from cmba_core import canonical

def run():
    path=ctypes.util.find_library('sodium')
    if path:
        lib=ctypes.CDLL(path);lib.sodium_init()
        lib.sodium_version_string.restype=ctypes.c_char_p
        point=lib.crypto_core_ed25519_is_valid_point;point.argtypes=[ctypes.c_void_p];point.restype=ctypes.c_int
        verify=lib.crypto_sign_verify_detached;verify.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulonglong,ctypes.c_void_p];verify.restype=ctypes.c_int
        valid_point=lambda raw:bool(point(ctypes.create_string_buffer(raw)))
        valid_signature=lambda sig,message,pub:verify(ctypes.create_string_buffer(sig),ctypes.create_string_buffer(message),len(message),ctypes.create_string_buffer(pub))==0
        backend=path;version=lib.sodium_version_string().decode();backend_sha256=None
    else:
        # PyNaCl's Windows wheel contains the genuine libsodium backend in its
        # compiled extension even when no system DLL is registered for find_library().
        try:
            import nacl._sodium as sodium_backend
            from nacl.bindings import crypto_core_ed25519_is_valid_point
            from nacl.signing import VerifyKey
            from nacl.exceptions import BadSignatureError
        except ImportError as e:raise RuntimeError('GENUINE_LIBSODIUM_UNAVAILABLE') from e
        valid_point=crypto_core_ed25519_is_valid_point
        def valid_signature(sig,message,pub):
            try:VerifyKey(pub).verify(message,sig);return True
            except BadSignatureError:return False
        backend_path=Path(sodium_backend.__file__).resolve()
        backend='PyNaCl.libsodium:'+backend_path.name
        version=importlib.metadata.version('PyNaCl')
        backend_sha256=hashlib.sha256(backend_path.read_bytes()).hexdigest()
    keys=[bytes.fromhex(public_key(fixture_key(i))) for i in range(1,33)]
    keys += [hashlib.sha256(('point-fixture-'+str(i)).encode()).digest() for i in range(32)]
    keys += [b'\x00'*32,b'\x01'+b'\x00'*31,b'\xff'*32,bytes.fromhex('ed'+'ff'*30+'7f')]
    for raw in keys:
        assert valid_point(raw)==admitted_public_key(raw)
    for i in range(1,17):
        e=seal('observation',{'case':i},fixture_key(i));message=SIGN_DOMAIN+canonical(e['body'])
        sig=bytes.fromhex(e['signature_hex']);pub=bytes.fromhex(e['body']['public_key'])
        assert valid_signature(sig,message,pub)
        bad=bytes([sig[0]^1])+sig[1:]
        assert not valid_signature(bad,message,pub)
    return {'status':'PASS','backend':backend,'backend_version':version,'backend_sha256':backend_sha256,
            'point_admission_cases':len(keys),'valid_signature_cases':16,'mutated_signature_cases':16,
            'independent_review':'NOT_PERFORMED','authority_effect':'NONE'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args()
    try:r=run();code=0
    except Exception as e:r={'status':'FAIL','reason':str(e)};code=2
    raw=canonical(r)+b'\n';sys.stdout.buffer.write(raw)
    if a.out:a.out.write_bytes(raw)
    raise SystemExit(code)
