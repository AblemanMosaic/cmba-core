"""Actual Tk interaction checks. Requires a display; never relabels headless as PASS."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,tempfile
ROOT=Path(__file__).resolve().parents[1]
if '--installed' not in sys.argv:sys.path.insert(0,str(ROOT/'src'))
import tkinter as tk
from tkinter import messagebox,filedialog
from cmba_core import canonical,decode,Refusal,reference,relation
from cmba_core.j1.registry import contracts
from cmba_workbench.k1.app import Application
from cmba_workbench.k1 import authoring,views


VISUAL_PALETTE={(16,23,32):10000,(23,34,46):10000,(28,42,56):1000,(43,64,82):1000}


def validate_visual_witness(image,expected_size):
    """Reject a desktop or occluding-window capture before it becomes evidence."""
    image=image.convert('RGB')
    if image.size!=expected_size:raise AssertionError('CMBA_WORKBENCH_VISUAL_SIZE')
    colors={color:count for count,color in (image.getcolors(maxcolors=image.width*image.height) or [])}
    if any(colors.get(color,0)<minimum for color,minimum in VISUAL_PALETTE.items()):
        raise AssertionError('CMBA_WORKBENCH_VISUAL_PALETTE')
    return image


def capture_window(root,path):
    """Raise the actual Tk window, capture its client bounds, validate, then seal."""
    from PIL import ImageGrab
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    root.deiconify();root.lift();root.focus_force();root.attributes('-topmost',True)
    try:
        root.update_idletasks();time.sleep(.25);root.update()
        x,y=root.winfo_rootx(),root.winfo_rooty();size=(root.winfo_width(),root.winfo_height())
        image=validate_visual_witness(ImageGrab.grab(bbox=(x,y,x+size[0],y+size[1])),size)
        image.save(path)
    finally:
        root.attributes('-topmost',False);root.update()
    return {'status':'PASS_VALIDATED_CMBA_WORKBENCH','capture_method':'RAISED_TOPMOST_TK_CLIENT_BOUNDS',
            'width':size[0],'height':size[1],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def run(screenshot=None):
    root=tk.Tk();app=Application(root);checks=[];visual_witness='NOT_REQUESTED'
    def record(name,condition):
        if not condition:raise AssertionError(name)
        checks.append(name)
    def pump():
        deadline=time.monotonic()+25
        while app.jobs.busy and time.monotonic()<deadline:root.update();time.sleep(.005)
        root.update();record('job-completed-'+str(len(checks)),not app.jobs.busy)
    try:
        root.update();record('ten-native-pages',len(app.pages)==10)
        record('initial-context-unselected',app.model._context is None)
        app.safe(app.evaluate);record('evaluation-without-reader-refused',app.last_error=='CMBA_READER_CONTEXT_REQUIRED')
        for contract in contracts():
            pid=contract['profile_id'];app.load_bundle(authoring.example(pid),name='PUBLIC fixture — '+pid)
            app.use_demo_context();app.evaluate();pump()
            record('native-profile-'+pid,app.last_error is None and app.model.history()[-1]['status'] in ('MATCH_FOR_SUPPLIED_EVIDENCE','NATIVE_REPORT_COMPUTED'))
        # Expiry shows a changed assessment without rewriting binding identity.
        app.load_bundle(authoring.example('cmba.consent'),name='Consent expiry example');app.use_demo_context();app.evaluate();pump()
        prior=app.model.receipt_packet();c=app.model.context();c['time']['epoch']=201
        app.settext(app.context_editor,c,editable=True);app.apply_context();app.evaluate();pump()
        after=app.model.receipt_packet();record('expiry-does-not-rewrite-object',prior['receipt']['body']['binding_root']==after['receipt']['body']['binding_root'] and prior['receipt']['body']['result']['status']!=after['receipt']['body']['result']['status'])
        app.show('history');ids=app.history_tree.get_children();app.history_tree.selection_set(ids[-2:]);app.compare_history();pump()
        record('receipt-comparison-visible','time_hash' in app.history_text.get('1.0','end'))
        # Data authoring and clickable local relationship navigation.
        app.author_profile.set('cmba.generic');app.settext(app.author_editor,{'title':'Authored target','instructions':'do not execute me'},editable=True)
        app.settext(app.author_options,{'now':0,'parameters':{},'relations':[]},editable=True);app.bind_draft()
        target=app.model.selected()['binding']['binding_root']
        b=authoring.author('cmba.generic',{'source':1},relations=[relation('dependency','depends_on',reference('cmba.binding',target))])
        app.load_bundle(b,name='Relationship source');app.show('graph');app.refresh_graph()
        ids=app.graph_tree.get_children();app.graph_tree.selection_set(ids[-1]);app.follow_target()
        record('explicit-follow-selected-target',app.model.selected()['binding']['binding_root']==target and app.model._context is None)
        # Wrong input never leaves a current successful matrix.
        app.settext(app.context_editor,{'invalid':True},editable=True);app.safe(app.apply_context)
        record('failed-context-clears-current-assessment',app.last_error is not None and not app.checks_tree.get_children() and app.model._context is None)
        # Selective export through the actual GUI confirmation path.
        app.show('disclosure');app.disclosure_create()
        index=list(app.disclosure_labels.get(0,'end')).index('public-title');app.disclosure_labels.selection_set(index);app.disclosure_select()
        record('selected-preview-omits-private-value','Do not disclose this value.' not in canonical(app.disclosure_preview).decode())
        with tempfile.TemporaryDirectory() as directory:
            app.set_workspace(directory);app.show('files');app.export_kind.set('disclosure');app.export_name.set('view.json')
            app.prepare_export();record('preview-is-not-a-write',list(Path(directory).iterdir())==[])
            old=messagebox.askyesno
            try:
                messagebox.askyesno=lambda *a,**kw:False
                app.approve_export();record('gui-cancellation-no-write',list(Path(directory).iterdir())==[])
                app.prepare_export();messagebox.askyesno=lambda *a,**kw:True
                app.approve_export()
                raw=(Path(directory)/'view.json').read_bytes()
                record('explicit-gui-export-exact-view',raw==canonical(app.disclosure_preview['view']) and b'private-note' not in raw)
                app.safe(app.prepare_export);record('gui-overwrite-refused',app.last_error=='CMBA_K_OVERWRITE_REFUSED')
                app.export_kind.set('workspace');app.export_name.set('workspace.json');app.prepare_export();app.approve_export()
                saved=(Path(directory)/'workspace.json').read_bytes()
                record('explicit-workspace-export',decode(saved)['trust_state']=='NOT_SERIALIZED')
                old_dialog=filedialog.askopenfilename
                try:
                    filedialog.askopenfilename=lambda **kw:str(Path(directory)/'workspace.json')
                    app.open_file()
                    record('gui-workspace-import-does-not-adopt-trust',app.model._selected is None and app.model._context is None and all(r['verification']=='IMPORTED_NOT_REPLAYED' for r in app.model.history()))
                finally:filedialog.askopenfilename=old_dialog
            finally:messagebox.askyesno=old
        for page in app.pages:app.show(page);root.update()
        record('all-pages-rendered',True)
        record('keyboard-actions-bound',all(root.bind(k) for k in ('<Control-o>','<Control-e>','<Control-s>','<Escape>')))
        app.design_assess();record('design-view-no-implicit-qualification',app.design_preview['body']['status']=='SUPPORTED_COMPONENTS_NOT_DEPLOYMENT_QUALIFIED')
        app.qualify();record('qualification-is-not-an-execution','NOT_EXECUTED' in app.design_text.get('1.0','end'))
        # A representative genuine screen, not an illustrative mock-up.
        app.load_bundle(authoring.example('cmba.kasd'),name='Joint approval — architecture + security')
        app.use_demo_context();app.evaluate();pump();app.show('context');root.update()
        if screenshot:
            visual_witness=capture_window(root,screenshot)
        return {'schema':'cmba.gui-smoke.k1','status':'PASS','checks':checks,'check_count':len(checks),
                'tk':root.tk.call('info','patchlevel'),'operator_approval':'SIMULATED_EXPLICIT_GUI_CONFIRMATION_IN_TEMPORARY_DIRECTORY',
                'platform':'ACTUAL_TK_ON_CURRENT_DISPLAY','visual_witness':visual_witness,
                'authority_effect':'NONE','external_publication':'NONE'}
    finally:app.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--installed',action='store_true');p.add_argument('--out',type=Path,required=True);p.add_argument('--screenshot',type=Path);a=p.parse_args()
    try:
        if a.installed:
            import cmba_core,cmba_workbench.k1.app
            assert Path(cmba_core.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()),'NOT_INSTALLED_CORE'
            assert Path(cmba_workbench.k1.app.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()),'NOT_INSTALLED_WORKBENCH'
        report=run(a.screenshot);report['installed_environment']=a.installed;code=0
    except Exception as e:report={'status':'FAIL','error':type(e).__name__+':'+str(e),'authority_effect':'NONE'};code=2
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report));raise SystemExit(code)
