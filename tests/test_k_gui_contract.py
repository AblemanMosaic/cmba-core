"""Actual display tests are a required replay leg, never skipped into a PASS."""
from pathlib import Path
import subprocess,os,sys,json,shutil
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import smoke_workbench_k


def test_actual_integrated_native_gui(tmp_path):
    command=[sys.executable,str(ROOT/'tools/smoke_workbench_k.py'),'--out',str(tmp_path/'gui.json')]
    if shutil.which('xvfb-run'):
        command=['xvfb-run','-a','-s','-screen 0 1600x1100x24']+command
    p=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=90)
    assert p.returncode==0,(p.stdout,p.stderr)
    r=json.loads((tmp_path/'gui.json').read_text(encoding='utf-8'))
    assert r['status']=='PASS' and r['check_count']>=40
    assert len([x for x in r['checks'] if x.startswith('native-profile-')])==13
    assert 'explicit-gui-export-exact-view' in r['checks']

def test_visual_witness_rejects_unrelated_window():
    from PIL import Image
    with pytest.raises(AssertionError,match='CMBA_WORKBENCH_VISUAL_PALETTE'):
        smoke_workbench_k.validate_visual_witness(Image.new('RGB',(1440,960),'#101010'),(1440,960))

def test_visual_witness_accepts_required_workbench_palette():
    from PIL import Image,ImageDraw
    image=Image.new('RGB',(400,400),'#101720');draw=ImageDraw.Draw(image)
    for box,color in [((0,0,199,199),'#17222e'),((200,0,399,199),'#1c2a38'),((0,200,199,399),'#2b4052')]:draw.rectangle(box,fill=color)
    assert smoke_workbench_k.validate_visual_witness(image,(400,400)).size==(400,400)
