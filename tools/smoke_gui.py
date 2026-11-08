"""Explicit UI test; screenshot/report output paths are caller-selected."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import tkinter as tk
from PIL import ImageGrab
from cmba_workbench.app import Application
from cmba_core.demo import chc,session

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--screenshot',type=Path,required=True);a=p.parse_args()
    r=tk.Tk();app=Application(r);r.update()
    assert len(app.dims.get_children())==4
    app.evaluate();assert app.last_error=='CMBA_READER_CONTEXT_REQUIRED'
    app.consent.set(True);app.evaluate();assert app.last_error is None;app.replay()
    assert 'MATCH_EXACT' in app.status.cget('text')
    app.load(chc(wrong_output=True));app.consent.set(True);app.evaluate()
    assert 'CONTRADICTED' in app.status.cget('text')
    app.load(session());app.consent.set(True);app.evaluate();assert app.last_error is None
    assert len(app.catalogue_tree.get_children())==71
    app.load(chc());app.tabs.select(0);r.update()
    a.screenshot.parent.mkdir(parents=True,exist_ok=True)
    ImageGrab.grab(bbox=(r.winfo_rootx(),r.winfo_rooty(),r.winfo_rootx()+r.winfo_width(),r.winfo_rooty()+r.winfo_height())).save(a.screenshot)
    a.out.write_text(json.dumps({'status':'PASS','checks':8,'display':'Xvfb Linux','tk':r.tk.call('info','patchlevel'),
      'scope':'creation,render,explicit-context gate,positive/negative evaluation,replay,session,catalogue',
      'native_windows':'NOT_RUN','authority_effect':'NONE'},indent=2)+'\n')
    r.destroy()
if __name__=='__main__':main()
