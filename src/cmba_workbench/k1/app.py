"""Native WB-K1 UI. Fixed handlers only; data never registers code or effects.

Evaluation runs in one bounded read-only worker. Only Tk's main thread renders or
approves file operations. No auto-signing, trust import, network fetch, or payload run.
"""
from __future__ import annotations
import json,sys,hashlib
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from cmba_core import canonical,decode,Refusal
from cmba_core.cli import read_local
from cmba_core.codec import clone
from cmba_core.errors import require
from cmba_core.j1 import disclosure
from cmba_core.j1.registry import contracts
from .common import MAX_PREVIEW,hash_value
from .session import Workspace,execute_verified_task,engine
from .effects import LocalEffects
from .jobs import Jobs
from . import authoring,views

BG='#101720';SURFACE='#17222e';FIELD='#1c2a38';BORDER='#2b4052'
TEXT='#e6edf5';MUTED='#a6b8c8';ACCENT='#91d0c6';WARN='#f1c67b';ERROR='#f0a2a2'
PAGES=[('inspect','Object inspector'),('profiles','Applications & capabilities'),('author','Author a binding'),
 ('context','Context & assessments'),('graph','Relationships & compare'),('history','Receipt history'),
 ('disclosure','Disclosure preview'),('design','Design & realization'),('native','Native DKN reader'),('files','Local workspace & export')]


def pretty(value):return value if type(value) is str else json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)


class Application:
    def __init__(self,root):
        self.root=root;self.model=Workspace();self.jobs=Jobs();self.job_handler=None;self.last_error=None
        self.host=None;self.plan=None;self._effect_input=None;self.disclosure_preview=None;self.design_preview=None
        self.private_disclosure=None;self.last_effect=None;self._closing=False
        self.profile_ids=['cmba.generic']+[c['profile_id'] for c in contracts()]
        root.title('CMBA Workbench • K1 — local evidence, explicit effects');root.geometry('1440x960');root.minsize(1120,760)
        root.configure(background=BG);root.protocol('WM_DELETE_WINDOW',self.close)
        style=ttk.Style(root);style.theme_use('clam')
        style.configure('.',background=BG,foreground=TEXT,font=('TkDefaultFont',10))
        style.configure('TFrame',background=BG);style.configure('TLabel',background=BG,foreground=TEXT)
        style.configure('TButton',background=FIELD,foreground=TEXT,padding=(9,7));style.map('TButton',background=[('active',BORDER)])
        style.configure('TCombobox',fieldbackground=FIELD,background=FIELD,foreground=TEXT,arrowcolor=TEXT)
        style.map('TCombobox',fieldbackground=[('readonly',FIELD)],foreground=[('readonly',TEXT)])
        style.configure('TEntry',fieldbackground=FIELD,foreground=TEXT,insertcolor=TEXT)
        style.configure('Treeview',background=SURFACE,fieldbackground=SURFACE,foreground=TEXT,rowheight=26)
        style.configure('Treeview.Heading',background=BORDER,foreground=TEXT,padding=5)
        style.map('Treeview',background=[('selected','#335666')]);style.configure('TNotebook.Tab',padding=(12,7))
        outer=ttk.Frame(root,padding=18);outer.pack(fill='both',expand=True)
        header=ttk.Frame(outer);header.pack(fill='x')
        ttk.Label(header,text='CMBA  /  WORKBENCH',font=('TkDefaultFont',21,'bold')).pack(side='left')
        ttk.Label(header,text='K1  ·  0.1.0a7  ·  RESEARCH PREVIEW',foreground=ACCENT).pack(side='right')
        ttk.Label(outer,text='Bindings say what was committed. Evaluators say what was checked. You choose the next effect.',foreground=MUTED).pack(anchor='w',pady=(5,12))
        bar=ttk.Frame(outer);bar.pack(fill='x',pady=(0,12))
        ttk.Button(bar,text='Open data…',command=lambda:self.safe(self.open_file)).pack(side='left',padx=(0,8))
        self.sample_var=tk.StringVar(value='cmba.chc.graph')
        ttk.Combobox(bar,textvariable=self.sample_var,values=self.profile_ids,state='readonly',width=29).pack(side='left',padx=(0,6))
        ttk.Button(bar,text='Load public fixture',command=lambda:self.safe(self.load_fixture)).pack(side='left')
        ttk.Button(bar,text='Assess selected',command=lambda:self.safe(self.evaluate)).pack(side='left',padx=8)
        ttk.Button(bar,text='Cancel pending work',command=self.cancel).pack(side='left')
        ttk.Button(bar,text='Save / export…',command=lambda:self.show('files')).pack(side='right')
        body=ttk.Frame(outer);body.pack(fill='both',expand=True)
        side=ttk.Frame(body,width=235);side.pack(side='left',fill='y',padx=(0,16));side.pack_propagate(False)
        ttk.Label(side,text='VIEWS',foreground=MUTED).pack(anchor='w',pady=(0,5))
        self.navigation=tk.Listbox(side,height=10,background=SURFACE,foreground=TEXT,selectbackground=BORDER,selectforeground=TEXT,
          highlightthickness=0,relief='flat',font=('TkDefaultFont',11),activestyle='none',exportselection=False)
        for _,name in PAGES:self.navigation.insert('end',name)
        self.navigation.pack(fill='x');self.navigation.bind('<<ListboxSelect>>',self.page_selected)
        ttk.Label(side,text='IN-MEMORY WORKSPACE',foreground=MUTED).pack(anchor='w',pady=(24,6))
        self.doc_tree=ttk.Treeview(side,columns=('label',),show='headings',height=5,selectmode='browse')
        self.doc_tree.heading('label',text='Select an admitted document');self.doc_tree.column('label',width=210)
        self.doc_tree.pack(fill='both',expand=True);self.doc_tree.bind('<<TreeviewSelect>>',self.document_selected)
        ttk.Label(side,text='No automatic saves.\nLoaded policy is not a trust anchor.\nPublic fixtures are not real keys.',foreground=WARN,wraplength=215).pack(anchor='w',pady=(14,0))
        self.content=ttk.Frame(body);self.content.pack(side='left',fill='both',expand=True)
        self.page_title=ttk.Label(self.content,text='',font=('TkDefaultFont',16,'bold'));self.page_title.pack(anchor='w')
        self.selection_label=ttk.Label(self.content,text='No selected binding',foreground=MUTED,wraplength=1040,font=('TkFixedFont',9))
        self.selection_label.pack(anchor='w',pady=(7,12))
        self.stack=ttk.Frame(self.content);self.stack.pack(fill='both',expand=True)
        self.pages={}
        for key,_ in PAGES:self.pages[key]=ttk.Frame(self.stack)
        self.build_inspector();self.build_profiles();self.build_author();self.build_context();self.build_graph()
        self.build_history();self.build_disclosure();self.build_design();self.build_native();self.build_files()
        self.status=ttk.Label(outer,text='Ready. Read-only until you separately approve a local export.',foreground=MUTED,wraplength=1300)
        self.status.pack(side='bottom',fill='x',pady=(12,0),before=body)
        root.bind('<Control-o>',lambda e:self.safe(self.open_file));root.bind('<Control-e>',lambda e:self.safe(self.evaluate))
        root.bind('<Control-s>',lambda e:self.show('files'));root.bind('<Escape>',lambda e:self.cancel())
        self.show('inspect');self.load_bundle(authoring.example('cmba.chc.graph'),name='CHC — public transformation fixture')
        self._timer=root.after(60,self.poll_jobs)

    def safe(self,fn):
        try:return fn()
        except Refusal as e:self.error(e.code)
        except (OSError,ValueError,tk.TclError) as e:self.error('CMBA_K_UI_INPUT_ERROR',type(e).__name__)
        except Exception as e:self.error('CMBA_K_INTERNAL_ERROR',type(e).__name__)

    def error(self,code,detail=''):
        self.last_error=code;self.status.configure(text='REFUSED  •  '+code+('  ('+detail+')' if detail else ''),foreground=ERROR)
        self.invalidate_effect()
        if hasattr(self,'context_label'):self.context_label.configure(text='Context: '+self.model._context_source)
        if hasattr(self,'matrix_text'):self.settext(self.matrix_text,'Current operation refused: '+code+'. Historical receipts remain separately labeled.')
        if hasattr(self,'checks_tree'):
            for i in self.checks_tree.get_children():self.checks_tree.delete(i)

    def info(self,text):self.last_error=None;self.status.configure(text=text,foreground=MUTED)

    @staticmethod
    def textbox(parent, *, height=10,editable=False):
        frame=ttk.Frame(parent);frame.pack(fill='both',expand=True,pady=5)
        box=tk.Text(frame,height=min(height,8),wrap='none',background=SURFACE,foreground=TEXT,
          insertbackground=TEXT,relief='flat',padx=12,pady=10,font=('TkFixedFont',10),undo=editable)
        sy=ttk.Scrollbar(frame,orient='vertical',command=box.yview);sy.pack(side='right',fill='y')
        sx=ttk.Scrollbar(frame,orient='horizontal',command=box.xview);sx.pack(side='bottom',fill='x')
        box.configure(yscrollcommand=sy.set,xscrollcommand=sx.set);box.pack(fill='both',expand=True)
        if not editable:box.configure(state='disabled')
        return box

    @staticmethod
    def settext(box,value, *, editable=False):
        s=pretty(value)
        # UI clipping is explicit and never used as the bytes to export or verify.
        if len(s)>MAX_PREVIEW and not editable:s=s[:MAX_PREVIEW]+'\n\n[DISPLAY TRUNCATED — underlying object is unchanged]'
        box.configure(state='normal');box.delete('1.0','end');box.insert('1.0',s)
        if not editable:box.configure(state='disabled')

    @staticmethod
    def json_editor(box):return decode(box.get('1.0','end-1c').encode(),canonical_required=False)

    def notice(self,parent,text):ttk.Label(parent,text=text,foreground=MUTED,wraplength=1000).pack(anchor='w',pady=(0,7))
    def button(self,parent,text,fn):
        b=ttk.Button(parent,text=text,command=lambda:self.safe(fn));b.pack(side='left',padx=(0,7));return b
    def toolbar(self,parent):
        f=ttk.Frame(parent);f.pack(fill='x',pady=5);return f

    def show(self,key):
        for p in self.pages.values():p.pack_forget()
        self.pages[key].pack(fill='both',expand=True);self.page_title.configure(text=dict(PAGES)[key])
        i=[k for k,_ in PAGES].index(key);self.navigation.selection_clear(0,'end');self.navigation.selection_set(i)
        if key=='history':self.refresh_history()
        if key=='graph':self.refresh_document_choices()

    def page_selected(self,_=None):
        n=self.navigation.curselection()
        if n:self.show(PAGES[n[0]][0])

    def refresh_documents(self):
        current=self.model._selected
        for r in self.doc_tree.get_children():self.doc_tree.delete(r)
        for row in self.model.documents():self.doc_tree.insert('','end',iid=row['document_id'],values=(row['label'],))
        if current:self.doc_tree.selection_set(current)
        self.refresh_document_choices()

    def document_selected(self,_=None):
        selected=self.doc_tree.selection()
        if selected and selected[0]!=self.model._selected:
            self.cancel();self.safe(lambda:self.model.select(selected[0]));self.refresh_selection()

    def build_inspector(self):
        p=self.pages['inspect'];self.notice(p,'Exact bindings and supplied values. This view does not establish meaning, signature recognition, or permission.')
        self.dims=ttk.Treeview(p,columns=('id','role','schema','value'),show='headings',height=6)
        for k,w in [('id',150),('role',200),('schema',340),('value',120)]:
            self.dims.heading(k,text=k.title());self.dims.column(k,width=w,minwidth=80)
        self.dims.pack(fill='x');self.inspect_text=self.textbox(p)

    def build_profiles(self):
        p=self.pages['profiles'];self.notice(p,'71 recovered catalogue records are not 71 operational applications. Installed capabilities are fixed; this catalogue cannot install code.')
        bar=self.toolbar(p);self.button(bar,'Show installed capabilities',lambda:self.settext(self.profile_details,views.capabilities()))
        self.profile_tree=ttk.Treeview(p,columns=('label','state'),show='headings',height=10)
        for k,w in [('label',330),('state',570)]:self.profile_tree.heading(k,text=k.title());self.profile_tree.column(k,width=w)
        self.profile_tree.pack(fill='both',expand=True);self.catalogue_rows={}
        for i,row in enumerate(views.catalogue()['entries']):
            self.catalogue_rows[str(i)]=row
            self.profile_tree.insert('','end',iid=str(i),values=(row.get('label',row['catalogue_id']),row.get('implementation','REFERENCE')))
        self.profile_details=self.textbox(p,height=8)
        self.profile_tree.bind('<<TreeviewSelect>>',lambda e:self.show_catalogue())

    def show_catalogue(self):
        ids=self.profile_tree.selection()
        if ids:self.settext(self.profile_details,self.catalogue_rows[ids[0]])

    def build_author(self):
        p=self.pages['author'];self.notice(p,'Author data, not Python. Binding a draft does not validate its behavior or sign it. Old approvals are not carried into a new draft context.')
        bar=self.toolbar(p);self.author_profile=tk.StringVar(value='cmba.chc.graph')
        ttk.Combobox(bar,textvariable=self.author_profile,values=self.profile_ids,state='readonly',width=30).pack(side='left',padx=(0,8))
        self.button(bar,'From selected record',self.author_from_selected);self.button(bar,'Public template',self.author_template)
        self.button(bar,'Bind draft',self.bind_draft)
        self.author_editor=self.textbox(p,editable=True,height=17)
        ttk.Label(p,text='Parameters and typed relations (JSON; no code or import paths)').pack(anchor='w')
        self.author_options=self.textbox(p,editable=True,height=5)
        self.settext(self.author_options,{'now':0,'parameters':{},'relations':[]},editable=True)
        self.settext(self.author_editor,{'description':'Select a template or load a record to begin.'},editable=True)

    def author_from_selected(self):
        b=self.model.selected();pid=b['binding']['body']['profile']['profile_id'];self.author_profile.set(pid)
        self.settext(self.author_editor,b['values'].get('record',b['values'].get('description',{})),editable=True)
        self.settext(self.author_options,{'now':b['context'].get('time',{}).get('epoch',0),
             'parameters':b['context'].get('policy',{}).get('parameters',{}),'relations':b['binding']['body']['relations']},editable=True)

    def author_template(self):
        b=authoring.example(self.author_profile.get())
        self.settext(self.author_editor,b['values'].get('record',b['values'].get('description',{})),editable=True)
        self.settext(self.author_options,{'now':b['context']['time']['epoch'],
           'parameters':b['context']['policy'].get('parameters',{}),'relations':b['binding']['body']['relations']},editable=True)
        self.info('Public fixture template loaded into editor only; no authority or signing key adopted.')

    def bind_draft(self):
        options=self.json_editor(self.author_options)
        from cmba_core.bindings import exact
        exact(options,{'now','parameters','relations'})
        b=authoring.author(self.author_profile.get(),self.json_editor(self.author_editor),**options)
        self.load_bundle(b,name='Authored — '+self.author_profile.get());self.show('inspect')
        self.info('Draft bound in memory. New context is unselected; endorsements and recognition are not inherited.')

    def build_context(self):
        p=self.pages['context'];self.notice(p,'Reader-owned roots, policy, authority roster, evidence, and clock. Applying edited data is a local choice, not authentication of its source.')
        bar=self.toolbar(p);self.button(bar,'Import reader context…',self.open_context)
        self.button(bar,'Apply displayed as reader context',self.apply_context)
        self.button(bar,'Use document context — DEMO ONLY',self.use_demo_context)
        self.button(bar,'Assess',self.evaluate)
        self.context_label=ttk.Label(p,text='Context: NOT_SELECTED',foreground=WARN);self.context_label.pack(anchor='w')
        self.context_editor=self.textbox(p,editable=True,height=10)
        self.checks_tree=ttk.Treeview(p,columns=('predicate','outcome'),show='headings',height=6)
        self.checks_tree.heading('predicate',text='Checked predicate');self.checks_tree.column('predicate',width=690)
        self.checks_tree.heading('outcome',text='Outcome');self.checks_tree.column('outcome',width=200);self.checks_tree.pack(fill='x',pady=5)
        self.matrix_text=self.textbox(p,height=8)

    def open_context(self):
        path=filedialog.askopenfilename(title='Select reader-owned context (not an implicit trust decision)',filetypes=[('JSON','*.json')])
        if path:
            v=decode(read_local(path));self.settext(self.context_editor,v,editable=True)
            self.info('Context displayed only. Apply it explicitly to use it.')

    def apply_context(self):
        self.cancel();self.model.set_reader_context(self.json_editor(self.context_editor));self.context_label.configure(text='Context: READER_SELECTED (source authentication external)')
        self.info('Reader context selected; no artifact authorized to act.')

    def use_demo_context(self):
        self.cancel();self.model.use_demo_context();self.settext(self.context_editor,self.model.context(),editable=True)
        self.context_label.configure(text='Context: DOCUMENT_DEMO_UNTRUSTED');self.info('Demo uses self-supplied pins and PUBLIC fixture keys. Not publisher recognition.')

    def build_graph(self):
        p=self.pages['graph'];self.notice(p,'Local references only. No remote fetch. Shared spelling or matching digest under another scheme does not establish the same identity.')
        bar=self.toolbar(p);self.left_choice=tk.StringVar();self.right_choice=tk.StringVar()
        self.left_combo=ttk.Combobox(bar,textvariable=self.left_choice,state='readonly',width=35);self.left_combo.pack(side='left',padx=(0,6))
        self.right_combo=ttk.Combobox(bar,textvariable=self.right_choice,state='readonly',width=35);self.right_combo.pack(side='left',padx=(0,6))
        self.button(bar,'Compare exact bindings',self.compare_selected)
        bar=self.toolbar(p);self.graph_filter=tk.StringVar(value='all')
        ttk.Combobox(bar,textvariable=self.graph_filter,values=['all','outgoing selected','incoming selected'],state='readonly',width=25).pack(side='left',padx=(0,8))
        self.button(bar,'Inspect local graph',self.refresh_graph);self.button(bar,'Follow selected target',self.follow_target)
        self.graph_tree=ttk.Treeview(p,columns=('predicate','target','state'),show='headings',height=7)
        for k,w in [('predicate',200),('target',510),('state',180)]:self.graph_tree.heading(k,text=k.title());self.graph_tree.column(k,width=w)
        self.graph_tree.pack(fill='x');self.graph_tree.bind('<Double-1>',lambda e:self.safe(self.follow_target));self.graph_edges={}
        self.graph_text=self.textbox(p)

    def refresh_document_choices(self):
        if not hasattr(self,'left_combo'):return
        self.choice_ids={r['label']+' ['+r['document_id'][:12]+']':r['document_id'] for r in self.model.documents()}
        values=list(self.choice_ids);self.left_combo.configure(values=values);self.right_combo.configure(values=values)
        if values:
            if self.left_choice.get() not in values:self.left_choice.set(values[0])
            if self.right_choice.get() not in values:self.right_choice.set(values[-1])

    def compare_selected(self):
        require(self.left_choice.get() in self.choice_ids and self.right_choice.get() in self.choice_ids,'CMBA_K_DOCUMENT_MISSING')
        self.settext(self.graph_text,self.model.compare_documents(self.choice_ids[self.left_choice.get()],self.choice_ids[self.right_choice.get()]))

    def refresh_graph(self):
        report=self.model.navigate();self.graph_edges={}
        for i in self.graph_tree.get_children():self.graph_tree.delete(i)
        selection=self.model.selected()['binding']['binding_root'] if self.model._selected else None
        for i,edge in enumerate(report['edges']):
            target=edge['relation']['target'];f=self.graph_filter.get()
            if f=='outgoing selected' and edge['source']!=selection:continue
            if f=='incoming selected' and not (target['scheme']=='cmba.binding' and target['algorithm']=='SHA-256' and target['digest_hex']==selection):continue
            self.graph_edges[str(i)]=edge
            self.graph_tree.insert('','end',iid=str(i),values=(edge['relation']['predicate'],target['digest_hex'],edge['target_status']))
        self.settext(self.graph_text,report)

    def follow_target(self):
        ids=self.graph_tree.selection();require(bool(ids),'CMBA_K_RELATION_SELECTION')
        edge=self.graph_edges[ids[0]];require(edge['target_status']=='PRESENT_LOCALLY','CMBA_K_TARGET_UNRESOLVED')
        candidates=[r for r in self.model.documents() if r['root']==edge['relation']['target']['digest_hex']]
        if len(candidates)!=1:
            self.settext(self.graph_text,{'status':'MULTIPLE_LOCAL_DOCUMENT_VIEWS_SELECT_EXPLICITLY','candidates':candidates});return
        self.cancel();self.model.select(candidates[0]['document_id']);self.refresh_documents();self.refresh_selection();self.show('inspect')

    def build_history(self):
        p=self.pages['history'];self.notice(p,'Historical result text is not current evidence. Imported entries stay NOT_REPLAYED until recomputed with their exact material and context.')
        bar=self.toolbar(p);self.button(bar,'Replay selected',self.replay_selected);self.button(bar,'Explain difference (2 selected)',self.compare_history);self.button(bar,'Refresh',self.refresh_history)
        self.history_tree=ttk.Treeview(p,columns=('time','status','verified','context'),show='headings',height=8)
        for k,w in [('time',90),('status',280),('verified',280),('context',250)]:self.history_tree.heading(k,text=k.title());self.history_tree.column(k,width=w)
        self.history_tree.pack(fill='both',expand=True);self.history_tree.bind('<<TreeviewSelect>>',lambda e:self.show_history())
        self.history_text=self.textbox(p,height=13)

    def refresh_history(self):
        for i in self.history_tree.get_children():self.history_tree.delete(i)
        for row in self.model.history():
            self.history_tree.insert('','end',iid=str(row['index']),values=(row['assessment_time']['epoch'],row['status'],row['verification'],row['context_source']))

    def show_history(self):
        s=self.history_tree.selection()
        if s:self.settext(self.history_text,self.model.receipt_packet(int(s[0])))

    def replay_selected(self):
        s=self.history_tree.selection();require(bool(s),'CMBA_NO_RECEIPT');index=int(s[0]);packet=self.model.receipt_packet(index)
        def run():
            b=packet['bundle'];return engine(b).replay(packet['receipt'],b['binding'],b['values'],packet['context'])
        def done(result):
            require(self.model.receipt_packet(index)['receipt']['receipt_hash']==packet['receipt']['receipt_hash'],'CMBA_K_STALE_RESULT')
            self.model._replayed.add(index);self.refresh_history();self.settext(self.history_text,result);self.info('Exact receipt replay matched. No recognition or execution approval.')
        self.start_job(run,done)

    def compare_history(self):
        rows=self.history_tree.selection();require(len(rows)==2,'CMBA_K_TWO_RECEIPTS_REQUIRED')
        a,b=[self.model.receipt_packet(int(x)) for x in rows]
        self.start_job(lambda:views.compare_receipts(a,b),lambda result:self.settext(self.history_text,result))

    def build_disclosure(self):
        p=self.pages['disclosure'];self.notice(p,'Create a salted commitment or load an existing opening set. Only selected openings enter the export preview. Inclusion is not encryption or unlinkability.')
        bar=self.toolbar(p);self.button(bar,'From selected disclosure',self.disclosure_from_selected)
        self.button(bar,'Create tree from entries',self.disclosure_create);self.button(bar,'Preview selected openings',self.disclosure_select)
        self.disclosure_editor=self.textbox(p,editable=True,height=7)
        self.settext(self.disclosure_editor,[{'label':'public-title','schema_id':'example.text','value':'Example'},
                                           {'label':'private-note','schema_id':'example.text','value':'Do not disclose this value.'}],editable=True)
        line=self.toolbar(p);ttk.Label(line,text='Expected root').pack(side='left');self.disclosure_root=tk.StringVar()
        ttk.Entry(line,textvariable=self.disclosure_root,width=80).pack(side='left',padx=8)
        self.disclosure_labels=tk.Listbox(p,selectmode='extended',height=5,background=SURFACE,foreground=TEXT,
           selectbackground=BORDER,selectforeground=TEXT,exportselection=False,highlightthickness=0);self.disclosure_labels.pack(fill='x')
        self.disclosure_text=self.textbox(p,height=10)

    def disclosure_from_selected(self):
        b=self.model.selected();require(b['binding']['body']['profile']['profile_id']=='cmba.disclosure','CMBA_K_DISCLOSURE_SELECTION')
        self.private_disclosure=clone(b['values']['record']);self.set_disclosure_labels()

    def set_disclosure_labels(self):
        self.invalidate_effect();self.disclosure_preview=None;self.disclosure_labels.delete(0,'end')
        for o in self.private_disclosure['openings']:self.disclosure_labels.insert('end',o['leaf']['label'])
        self.disclosure_root.set(self.private_disclosure['header']['disclosure_root'])
        self.settext(self.disclosure_text,'Nothing selected for disclosure. The displayed root is a supplied/self-authored value, not independent authentication.')

    def disclosure_create(self):
        self.private_disclosure=disclosure.make(self.json_editor(self.disclosure_editor));self.set_disclosure_labels()
        self.info('Fresh salts generated explicitly in memory. Private openings have NOT been saved or exported.')

    def disclosure_select(self):
        require(self.private_disclosure is not None,'CMBA_K_DISCLOSURE_SELECTION')
        labels=[self.disclosure_labels.get(i) for i in self.disclosure_labels.curselection()]
        require(bool(labels),'CMBA_K_DISCLOSURE_SELECTION');self.invalidate_effect()
        self.disclosure_preview=views.preview_disclosure(self.private_disclosure,labels,expected_root=self.disclosure_root.get())
        self.settext(self.disclosure_text,self.disclosure_preview)
        self.info('Preview verified; export includes only the selected view, never the private opening set.')

    def build_design(self):
        p=self.pages['design'];self.notice(p,'Explore a finite supported design space. Supported components are not a security score or deployment qualification. No custom code is registered.')
        grid=ttk.Frame(p);grid.pack(fill='x');self.design_vars={}
        for i,(k,choices) in enumerate(views.DESIGN_FIELDS.items()):
            ttk.Label(grid,text=k.title()).grid(row=i//3*2,column=i%3,sticky='w',padx=8)
            v=tk.StringVar(value=choices[0]);self.design_vars[k]=v
            ttk.Combobox(grid,textvariable=v,values=choices,state='readonly',width=29).grid(row=i//3*2+1,column=i%3,sticky='ew',padx=8,pady=(2,8))
        bar=self.toolbar(p);self.button(bar,'Assess design',self.design_assess);self.button(bar,'Installed model / corpus references',lambda:self.settext(self.design_text,views.installed_qualification()))
        self.design_text=self.textbox(p,height=8)
        ttk.Label(p,text='Replacement declarations: compare contracts and realizations; never infer approval from submitted results.').pack(anchor='w',pady=(12,0))
        self.qualification_editor=self.textbox(p,editable=True,height=6)
        proto={'semantic_commitment':'0'*64,'realization_sha256':'1'*64,'corpus_sha256':'2'*64,'claimed_results':{'status':'NOT_RUN'}}
        self.settext(self.qualification_editor,{'left':proto,'right':{**proto,'realization_sha256':'3'*64}},editable=True)
        bar=self.toolbar(p);self.button(bar,'Compare declarations',self.qualify)

    def design_assess(self):
        self.invalidate_effect();self.design_preview=views.design({k:v.get() for k,v in self.design_vars.items()})
        self.settext(self.design_text,self.design_preview)

    def qualify(self):
        from cmba_core.bindings import exact
        pair=self.json_editor(self.qualification_editor);exact(pair,{'left','right'})
        self.settext(self.design_text,views.qualification(**pair))

    def build_native(self):
        p=self.pages['native'];self.notice(p,'Read a host-selected native DKN index or vault. No file path from a loaded binding is used. Read results retain native uncertainty; this interface never creates or advances a vault.')
        line=self.toolbar(p);self.native_kind=tk.StringVar(value='index');self.native_path=tk.StringVar();self.native_op=tk.StringVar(value='discover')
        ttk.Combobox(line,textvariable=self.native_kind,values=['index','vault'],state='readonly',width=8).pack(side='left')
        ttk.Entry(line,textvariable=self.native_path,width=62).pack(side='left',padx=7)
        self.button(line,'Select path…',self.native_choose)
        line=self.toolbar(p);ttk.Combobox(line,textvariable=self.native_op,values=['discover','resolve_exact','traverse','compare_namespace','read_namespace'],state='readonly',width=25).pack(side='left')
        self.button(line,'Read native collection',self.native_read)
        self.native_args=self.textbox(p,height=7,editable=True);self.settext(self.native_args,{},editable=True)
        self.native_text=self.textbox(p,height=18)

    def native_choose(self):
        path=filedialog.askdirectory(title='Select existing native DKN index') if self.native_kind.get()=='index' else filedialog.askopenfilename(title='Select existing native DKN vault')
        if path:self.native_path.set(path)

    def native_read(self):
        path=self.native_path.get();require(bool(path),'CMBA_K_NATIVE_PATH_REQUIRED')
        kind=self.native_kind.get();op=self.native_op.get();args=self.json_editor(self.native_args)
        from cmba_core.j1.native import read_collection
        self.start_job(lambda:read_collection(path,op,args,kind=kind),lambda r:self.settext(self.native_text,r))

    def build_files(self):
        p=self.pages['files'];self.notice(p,'Create-only local files. Preparing a preview writes nothing. Approval binds the exact output, selected input/context, destination and expiry. Existing files are never overwritten.')
        line=self.toolbar(p);self.workspace_path=tk.StringVar();ttk.Entry(line,textvariable=self.workspace_path,width=80,state='readonly').pack(side='left',padx=(0,8))
        self.button(line,'Select output directory…',self.choose_workspace)
        line=self.toolbar(p);self.export_kind=tk.StringVar(value='bundle');self.export_name=tk.StringVar(value='binding.json');self.handoff_target=tk.StringVar(value='courthouse')
        ttk.Combobox(line,textvariable=self.export_kind,values=['bundle','receipt','workspace','disclosure','handoff','design'],state='readonly',width=13).pack(side='left')
        ttk.Entry(line,textvariable=self.export_name,width=35).pack(side='left',padx=8)
        ttk.Combobox(line,textvariable=self.handoff_target,values=['dkn','ccp','ucm','pippi','courthouse'],state='readonly',width=15).pack(side='left')
        self.button(line,'Prepare preview',self.prepare_export)
        line=self.toolbar(p);self.approve_button=self.button(line,'Review, approve & create file…',self.approve_export)
        self.button(line,'Cancel plan',self.invalidate_effect)
        self.notice(p,'Bundles, receipts and workspaces may contain private material. No secret scrubber or encryption is provided. Disclosure exports contain selected openings only. Handoffs contain references only and are not submitted anywhere.')
        self.effect_text=self.textbox(p,height=24)
        for var in (self.export_kind,self.export_name,self.handoff_target):var.trace_add('write',lambda *_:self.invalidate_effect())
        self.approve_button.configure(state='disabled')

    def choose_workspace(self):
        path=filedialog.askdirectory(title='Select an existing operator-owned local output directory')
        if path:self.set_workspace(path)

    def set_workspace(self,path):
        self.invalidate_effect()
        if self.host:self.host.close()
        self.host=LocalEffects(path,current_state=self.effect_state);self.workspace_path.set(str(self.host.path))
        self.info('Local output directory selected. No file created.')

    def effect_state(self):
        return hash_value('workspace',{'model':self.model.state_binding(),'kind':self.export_kind.get(),'name':self.export_name.get(),
          'handoff_target':self.handoff_target.get(),'disclosure_preview':self.disclosure_preview,'design_preview':self.design_preview})

    def export_value(self):
        kind=self.export_kind.get()
        if kind=='bundle':return self.model.selected()
        if kind=='workspace':return self.model.snapshot()
        if kind=='receipt':
            selected=self.history_tree.selection();return self.model.receipt_packet(int(selected[0]) if selected else None)
        if kind=='disclosure':
            require(self.disclosure_preview is not None,'CMBA_K_DISCLOSURE_SELECTION');return clone(self.disclosure_preview['view'])
        if kind=='design':
            require(self.design_preview is not None,'CMBA_K_DESIGN_SELECTION');return clone(self.design_preview)
        if kind=='handoff':return views.handoff(self.handoff_target.get(),self.model.selected())
        raise Refusal('CMBA_K_EFFECT_KIND')

    def prepare_export(self):
        require(not self.jobs.busy,'CMBA_K_JOB_BUSY');require(self.host is not None,'CMBA_K_WORKSPACE_NOT_SELECTED')
        value=self.export_value();self.plan=self.host.prepare(self.export_kind.get(),value,name=self.export_name.get())
        self._effect_input=hashlib.sha256(canonical(value)).hexdigest()
        self.settext(self.effect_text,{'plan':self.plan,'exact_output_preview':value,'notice':'No file has been written. Preview clipping, if shown, affects display only.'})
        self.approve_button.configure(state='normal');self.info('Plan prepared. Separate host confirmation is required; it expires after 120 seconds.')
        return clone(self.plan)

    def approve_export(self):
        require(self.host is not None and self.plan is not None,'CMBA_K_NO_PENDING_EFFECT')
        require(hashlib.sha256(canonical(self.export_value())).hexdigest()==self._effect_input,'CMBA_K_INPUT_CHANGED')
        b=self.plan['body'];prompt=(f"Create {b['target_name']}\nIn {b['workspace']}\n\n{b['output_bytes']} exact bytes\nSHA-256: {b['output_sha256']}\n\nNo overwrite. No encryption or secret scrubbing.\nNo external publication or authority grant.\n\nApprove this one local write?")
        if not messagebox.askyesno('Explicit local effect approval',prompt,parent=self.root):self.invalidate_effect();self.info('Export cancelled; no file written.');return
        self.commit_export()

    def commit_export(self):
        # Host action used by GUI/tests, not exposed through any serialized interface.
        require(self.host is not None and self.plan is not None,'CMBA_K_NO_PENDING_EFFECT')
        require(hashlib.sha256(canonical(self.export_value())).hexdigest()==self._effect_input,'CMBA_K_INPUT_CHANGED')
        self.last_effect=self.host.commit(self.host.approve(self.plan['plan_hash']))
        self.invalidate_effect();self.settext(self.effect_text,self.last_effect);self.info(self.last_effect['status']+' — one explicitly approved local file effect.')
        return clone(self.last_effect)

    def invalidate_effect(self):
        if self.host:self.host.cancel()
        self.plan=None;self._effect_input=None
        if hasattr(self,'approve_button'):self.approve_button.configure(state='disabled')

    def load_bundle(self,bundle, *, name='Imported binding'):
        self.cancel()
        try:self.model.load(bundle,name=name)
        finally:self.refresh_documents();self.refresh_selection()
        self.info('Binding admitted in memory. Reader context NOT_SELECTED; no file written.')

    def load_fixture(self):
        b=authoring.example(self.sample_var.get());self.load_bundle(b,name='PUBLIC fixture — '+self.sample_var.get());self.show('inspect')

    def open_file(self):
        path=filedialog.askopenfilename(title='Open canonical bundle, receipt packet or workspace (data only)',filetypes=[('Canonical JSON','*.json')])
        if not path:return
        self.cancel()
        try:
            value=decode(read_local(path));schema=value.get('schema') if type(value) is dict else None
            if schema=='cmba.workspace.k1':
                if not messagebox.askyesno('Replace in-memory workspace?','This replaces the unsaved in-memory collection. Imported context is NOT selected; imported receipt results need replay.',parent=self.root):return
                self.model.restore(value)
            elif schema=='cmba.receipt-packet.k1':self.model.import_receipt(value)
            else:self.model.load(value,name=Path(path).name[:128])
        except Exception:
            self.model._clear();raise
        finally:self.refresh_documents();self.refresh_selection();self.refresh_history()
        self.info('Data imported. No trust settings adopted; no files written.')

    def refresh_selection(self):
        self.invalidate_effect();self.disclosure_preview=None;self.private_disclosure=None
        for item in self.dims.get_children():self.dims.delete(item)
        for item in self.checks_tree.get_children():self.checks_tree.delete(item)
        self.context_label.configure(text='Context: NOT_SELECTED')
        if self.model._selected is None:
            self.selection_label.configure(text='No admitted selection');self.settext(self.inspect_text,'No selection.')
            self.settext(self.context_editor,{},editable=True);self.settext(self.matrix_text,'No current assessment.');return
        b=self.model.selected();report=self.model.inspection()
        self.selection_label.configure(text=b['binding']['body']['profile']['profile_id']+'\n'+b['binding']['binding_root'])
        for d in report['dimensions']:self.dims.insert('','end',values=(d['dimension_id'],d['role'],d['schema_id'],d['commitment']))
        self.settext(self.inspect_text,{'inspection':report,'supplied_values':b['values'],'document_context':'NOT_SELECTED'})
        self.settext(self.context_editor,b['context'],editable=True);self.settext(self.matrix_text,'No assessment under selected reader context.')

    def start_job(self,fn,handler):
        require(not self.jobs.busy,'CMBA_K_JOB_BUSY');self.invalidate_effect();self.job_handler=handler
        self.jobs.start(fn);self.info('Computing a bounded read-only task; cancellation discards its result.')

    def evaluate(self):
        require(not self.jobs.busy,'CMBA_K_JOB_BUSY');task=self.model.prepare_evaluation()
        self.start_job(lambda:execute_verified_task(task),self.finish_evaluation)

    def finish_evaluation(self,value):
        receipt=self.model.accept_verified(value);m=views.matrix(receipt)
        for i in self.checks_tree.get_children():self.checks_tree.delete(i)
        for row in m['rows']:self.checks_tree.insert('','end',values=(row['predicate'],row['outcome']))
        self.settext(self.matrix_text,m);self.refresh_history();self.settext(self.history_text,self.model.receipt_packet())
        self.show('context');self.info(m['status']+' — scoped assessment only; operational authorization remains external.')

    def poll_jobs(self):
        if self._closing:return
        result=self.jobs.poll()
        if result:
            if result['status']=='RESULT':
                handler=self.job_handler;self.job_handler=None
                if handler:self.safe(lambda:handler(result['value']))
            elif result['status']=='REFUSED':self.job_handler=None;self.error(result['code'])
            else:
                self.job_handler=None;self.info(result['status']+' — '+result['worker'])
        self._timer=self.root.after(60,self.poll_jobs)

    def cancel(self):
        self.jobs.cancel();self.job_handler=None;self.model.cancel();self.invalidate_effect()
        if hasattr(self,'checks_tree'):
            for i in self.checks_tree.get_children():self.checks_tree.delete(i)
        if hasattr(self,'matrix_text'):self.settext(self.matrix_text,'No current assessment. Cancelled or prior results are not current evidence.')

    def close(self):
        self._closing=True;self.cancel()
        if self.host:self.host.close()
        if hasattr(self,'_timer'):
            try:self.root.after_cancel(self._timer)
            except tk.TclError:pass
        self.root.destroy()


def main():
    try:root=tk.Tk()
    except tk.TclError:
        print('CMBA_GUI_UNAVAILABLE: Tk and a graphical session are required.',file=sys.stderr);return 2
    Application(root);root.mainloop();return 0
if __name__=='__main__':raise SystemExit(main())
