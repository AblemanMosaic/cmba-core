"""Host-selected bridge to frozen DKN. No changes to native commitments or packages."""
from __future__ import annotations
from importlib import util, import_module
from importlib.resources import files
from pathlib import Path
import hashlib
import io
import zipfile
from ..codec import decode
from ..bindings import (exact, hex_digest, dimension, bind, reference, relation, profile_reference)
from ..errors import Refusal, require
from ..registry import contract


def load_native():
    spec=util.find_spec('dkn_v02')
    require(spec is not None and spec.origin is not None, 'CMBA_DKN_DEPENDENCY_UNAVAILABLE')
    parent=Path(spec.origin).parent.parent
    record=decode(files('cmba_core').joinpath('data/dkn-runtime.json').read_bytes(), canonical_required=False)
    # Verify every inherited v0.2 module before importing it. Host/process integrity still assumed.
    for path, expected in record['files'].items():
        if not path.startswith('dkn_v02/'):
            continue
        try:raw=(parent/path).read_bytes()
        except OSError as exc:raise Refusal('CMBA_DKN_RUNTIME_MISMATCH') from exc
        require(hashlib.sha256(raw).hexdigest()==expected,'CMBA_DKN_RUNTIME_MISMATCH')
    try:return import_module('dkn_v02.core')
    except ImportError as exc:raise Refusal('CMBA_DKN_DEPENDENCY_UNAVAILABLE') from exc


def evaluate(values: dict) -> dict:
    native=load_native()
    try:native.validate_manifest(values['manifest'])
    except native.Refusal as exc:raise Refusal('CMBA_DKN_NATIVE_REFUSED') from exc
    t=values['transport'];exact(t, {'algorithm','digest_hex','byte_length'})
    require(t['algorithm']=='SHA-256','CMBA_DKN_TRANSPORT_ALGORITHM');hex_digest(t['digest_hex'])
    require(type(t['byte_length']) is int and 0<=t['byte_length']<=native.MAX_TRANSPORT,
            'CMBA_DKN_TRANSPORT_SIZE')
    return {'dkn.native-manifest':'MATCH','dkn.transport-description':'MATCH'}


def bind_archive(raw: bytes, *, expected_logical_root: str, certificate: dict | None = None) -> dict:
    """Explicit payload check; this returned report is not accepted in place of raw evidence."""
    hex_digest(expected_logical_root)
    native=load_native()
    try:
        report=native.verify_archive(raw)
        # Parse the manifest only AFTER the native verifier admits the exact archive.
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            manifest=native.read_canonical(archive.read('.dkn/manifest.json'))
        require(manifest['logical_root']==expected_logical_root, 'CMBA_DKN_EXPECTED_ROOT_MISMATCH')
        cert_report=native.verify_certificate(certificate,manifest) if certificate is not None else None
    except native.Refusal as exc:raise Refusal('CMBA_DKN_NATIVE_REFUSED') from exc
    values={'manifest':manifest,'transport':{'algorithm':'SHA-256','digest_hex':hashlib.sha256(raw).hexdigest(),'byte_length':len(raw)}}
    c=contract('cmba.dkn.artifact')
    dims=[dimension(d['dimension_id'],d['role'],d['schema_id'],values[d['dimension_id']]) for d in c['required_dimensions']]
    obj=bind(profile_reference(c),dims,relations=[relation('native-identity','references-native-root',
                reference('dkn.logical.v0.2-candidate',expected_logical_root))])
    return {'binding':obj,'values':values,'native_report':report,'certificate_report':cert_report,
            'native_logical_root':expected_logical_root,'root_translation':'NONE_NEW_WRAPPER_ROOT',
            'authority_effect':'NONE'}
