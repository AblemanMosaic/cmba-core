from pathlib import Path
import hashlib,json,sys,shutil
import pytest
from cmba_core import canonical,decode
from cmba_core.bindings import digest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import check_model,unpack_baseline,package


def test_model_reference_integrity():
    assert check_model.check()['obligations']==18


def test_model_external_pin_refuses():
    with pytest.raises(ValueError,match='MODEL_EXPECTED_COMMITMENT_MISMATCH'):check_model.check(expected_commitment='0'*64)


def test_source_register_exact_bytes():
    reg=json.loads((ROOT/'SOURCE-REGISTER.json').read_text(encoding='utf-8'))
    assert len(reg['records'])==5
    for row in reg['records']:
        raw=(ROOT/row['path']).read_bytes()
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']


def test_baseline_exact_closed_inventory():
    assert unpack_baseline.verify()['members']==668


def test_native_wheel_exact_hash():
    raw=(ROOT/'baseline/dkn/dkn_core-0.2.0rc5-py3-none-any.whl').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='6cc2d9e21c1c26b9b9104bb84a27b8e873f17c7e52bed15228230775e005ccf8'


def test_package_closed_and_repeatable(tmp_path):
    root=tmp_path/'source';root.mkdir();(root/'a.txt').write_text('a')
    a=tmp_path/'a.zip';b=tmp_path/'b.zip'
    package.build(a,root);package.build(b,root)
    assert a.read_bytes()==b.read_bytes() and package.verify(a)['members']==2


def test_package_extra_member_refuses(tmp_path):
    import zipfile
    root=tmp_path/'source';root.mkdir();(root/'a').write_text('a');out=tmp_path/'a.zip';package.build(out,root)
    with zipfile.ZipFile(out,'a') as z:z.writestr('extra','x')
    with pytest.raises(ValueError,match='ARCHIVE_CLOSURE'):package.verify(out)


def test_build_metadata_not_source_but_real_changes_are(tmp_path):
    import verify_i
    for dirname in ('src','tests','tools','examples','schemas','interop','model','catalogue','docs'):
        (tmp_path/dirname).mkdir()
    for name in ('pyproject.toml','SOURCE-REGISTER.json','README.md'):
        (tmp_path/name).write_text('fixture')
    source=tmp_path/'src/core.py';source.write_text('original')
    original=verify_i.fingerprint(tmp_path)
    generated=tmp_path/'src/cmba_core.egg-info';generated.mkdir()
    (generated/'PKG-INFO').write_text('generated')
    assert verify_i.fingerprint(tmp_path)==original
    source.write_text('changed')
    assert verify_i.fingerprint(tmp_path)!=original
