"""Native Tk read-only workbench. No server, subprocess, plugin loader or publication.

Only explicit file selection reads external data. The demonstration evaluation
context is visibly self-supplied and never promoted to recognized authority.
"""
from __future__ import annotations
import json
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from cmba_core import decode, Refusal
from cmba_core.cli import read_local
from cmba_core.demo import chc, session
from .model import Workbench

BG='#121820';PANEL='#1c2530';TEXT='#e5eaf0';MUTED='#a5b2c2';ACCENT='#8ccdc2'


class Application:
    def __init__(self, root: tk.Tk):
        self.root=root;self.model=Workbench();self.last_error=None
        root.title('CMBA | Binding Workbench — Batch I');root.geometry('1220x820');root.minsize(980,700)
        root.configure(background=BG)
        style=ttk.Style(root);style.theme_use('clam')
        style.configure('.',background=BG,foreground=TEXT,font=('TkDefaultFont',11))
        style.configure('TFrame',background=BG);style.configure('TLabel',background=BG,foreground=TEXT)
        style.configure('TButton',background=PANEL,foreground=TEXT,padding=(10,7))
        style.map('TButton',background=[('active','#314454')])
        style.configure('TNotebook',background=BG,borderwidth=0)
        style.configure('TNotebook.Tab',background=PANEL,foreground=TEXT,padding=(15,9))
        style.map('TNotebook.Tab',background=[('selected','#314454')])
        style.configure('Treeview',background=PANEL,fieldbackground=PANEL,foreground=TEXT,rowheight=29)
        style.configure('Treeview.Heading',background='#293544',foreground=TEXT)
        style.map('Treeview',background=[('selected','#365361')])
        outer=ttk.Frame(root,padding=20);outer.pack(fill='both',expand=True)
        ttk.Label(outer,text='CMBA  /  BINDING WORKBENCH',font=('TkDefaultFont',19,'bold')).pack(anchor='w')
        ttk.Label(outer,text='Open-ended descriptions. Finite checks. Explicit authority boundaries.',foreground=MUTED).pack(anchor='w',pady=(5,13))
        self.banner=ttk.Label(outer,text='Batch I engineering candidate  •  Local only  •  Unsigned receipts  •  Authority effect: NONE',foreground=ACCENT)
        self.banner.pack(anchor='w',pady=(0,13))
        self.tabs=ttk.Notebook(outer);self.tabs.pack(fill='both',expand=True)
        binding=ttk.Frame(self.tabs,padding=12);applications=ttk.Frame(self.tabs,padding=12)
        self.receipts_tab=ttk.Frame(self.tabs,padding=12);program=ttk.Frame(self.tabs,padding=12)
        for widget,name in [(binding,'Binding inspector'),(applications,'Application catalogue'),(self.receipts_tab,'Evaluation receipt'),(program,'Program & boundaries')]:self.tabs.add(widget,text=name)
        toolbar=ttk.Frame(binding);toolbar.pack(fill='x')
        for label,fn in [('Open bundle…',self.open_file),('CHC example',lambda:self.load(chc())),
                         ('Wrong output',lambda:self.load(chc(wrong_output=True))),('Session example',lambda:self.load(session()))]:
            ttk.Button(toolbar,text=label,command=fn).pack(side='left',padx=(0,8))
        self.root_label=ttk.Label(binding,text='',foreground=MUTED,font=('TkFixedFont',10));self.root_label.pack(anchor='w',pady=(15,8))
        self.dims=ttk.Treeview(binding,columns=('dimension','role','schema','commitment'),show='headings',height=5)
        for k,width in [('dimension',140),('role',180),('schema',390),('commitment',150)]:
            self.dims.heading(k,text=k.replace('_',' ').title());self.dims.column(k,width=width,minwidth=90)
        self.dims.pack(fill='x')
        bar=ttk.Frame(binding);bar.pack(fill='x',pady=(10,6))
        self.consent=tk.BooleanVar(value=False)
        ttk.Checkbutton(bar,text='Use displayed document context for DEMONSTRATION only (not a trusted pin)',variable=self.consent).pack(side='left')
        ttk.Button(bar,text='Evaluate selected profile',command=self.evaluate).pack(side='right')
        self.details=self.textbox(binding);self.details.pack(fill='both',expand=True)
        self.catalogue_tree=ttk.Treeview(applications,columns=('name','kind','state'),show='headings',height=12)
        for k,width in [('name',340),('kind',220),('state',430)]:
            self.catalogue_tree.heading(k,text=k.title());self.catalogue_tree.column(k,width=width)
        self.catalogue_tree.pack(fill='both',expand=True)
        self.entries={}
        for i,e in enumerate(self.model.applications()['entries']):
            row=str(i);self.entries[row]=e;self.catalogue_tree.insert('', 'end',iid=row,values=(e['label'],e['kind'],e['implementation']))
        self.catalogue_details=self.textbox(applications,height=8);self.catalogue_details.pack(fill='both',expand=True,pady=(10,0))
        self.catalogue_tree.bind('<<TreeviewSelect>>',self.show_application)
        ttk.Label(self.receipts_tab,text='Replay recomputes the evaluation; a self-consistent hash alone is insufficient.',foreground=MUTED).pack(anchor='w',pady=(0,8))
        ttk.Button(self.receipts_tab,text='Replay last receipt',command=self.replay).pack(anchor='w',pady=(0,10))
        self.receipt_text=self.textbox(self.receipts_tab);self.receipt_text.pack(fill='both',expand=True)
        p=self.textbox(program);p.pack(fill='both',expand=True)
        self.settext(p, 'BATCH I — FOUNDATION\n\nImplemented: typed binding kernel; pinned built-in profiles; DKN manifest/archive adapter; bounded CHC JSON transform; GenDev source-span checker; exact evaluation receipts; local inspector.\n\n52 historical domain rows + 19 application-family records are catalogued. Catalogue entries are not deployed systems.\n\nBATCH J — APPLICATION EVALUATORS\nJurisdiction, consent, disclosure, observation, coordination and reconciliation with finite predicates. Domain templates remain explicit about missing validation.\n\nBATCH K — INTEGRATED WORKBENCH\nAuthoring, comparison, navigation, policy/evidence views and selected local effects behind host-owned controls.\n\nBATCH L — QUALIFICATION\nConformance, cross-language checks, adversarial review, packaging and target-machine handoff.\n\nNOT CLAIMED\nIndependent approval, domain truth, medical/election/weapon-control systems, global freshness, live P2P, automatic trust, arbitrary code safety or complete semantic equivalence.\n\nThis workbench cannot install plugins, execute payloads, publish, sign or fetch remote data. Opening a description never authorizes its effects.')
        self.status=ttk.Label(outer,text='Ready — no file selected',foreground=MUTED);self.status.pack(side='bottom',fill='x',before=self.tabs,pady=(9,0))
        self.load(chc())

    @staticmethod
    def textbox(parent,height=10):
        box=tk.Text(parent,height=height,wrap='word',background=PANEL,foreground=TEXT,
                    insertbackground=TEXT,relief='flat',padx=14,pady=12,font=('TkFixedFont',10))
        box.configure(state='disabled');return box

    @staticmethod
    def settext(box,value):
        text=value if isinstance(value,str) else json.dumps(value,indent=2,ensure_ascii=False,sort_keys=True)
        box.configure(state='normal');box.delete('1.0','end');box.insert('end',text);box.configure(state='disabled')

    def error(self,e):
        self.last_error=e.code;self.status.configure(text='REFUSED: '+e.code)

    def load(self,value):
        try:
            report=self.model.load(value);self.last_error=None;self.consent.set(False)
            self.root_label.configure(text='Binding root: '+value['binding']['binding_root'])
            for iid in self.dims.get_children():self.dims.delete(iid)
            for d in report['dimensions']:self.dims.insert('', 'end',values=(d['dimension_id'],d['role'],d['schema_id'],d['commitment']))
            self.settext(self.details,{'inspection':report,'supplied_context_not_a_trust_anchor':value['context'],'values':value['values']})
            self.settext(self.receipt_text,'No evaluation for this selection.');self.status.configure(text='Structure and supplied commitments checked. Profile semantics not yet evaluated.')
        except Refusal as e:
            self.root_label.configure(text='No admitted binding')
            for iid in self.dims.get_children():self.dims.delete(iid)
            self.settext(self.details, {'status':'REFUSED','code':e.code})
            self.settext(self.receipt_text, 'No current receipt.');self.error(e)

    def open_file(self):
        path=filedialog.askopenfilename(title='Open a canonical CMBA bundle',filetypes=[('Canonical JSON','*.json'),('All files','*')])
        if path:
            try:self.load(decode(read_local(path)))
            except Refusal as e:self.error(e)

    def evaluate(self):
        try:
            receipt=self.model.evaluate(accept_document_context=self.consent.get());self.last_error=None
            self.settext(self.receipt_text,receipt);self.tabs.select(self.receipts_tab)
            self.status.configure(text=receipt['body']['result']['status']+' — no authorization or execution effect')
        except Refusal as e:self.error(e)

    def replay(self):
        try:self.status.configure(text=self.model.replay()['status']+' — unsigned engineering evidence')
        except Refusal as e:self.error(e)

    def show_application(self,_=None):
        selection=self.catalogue_tree.selection()
        if selection:self.settext(self.catalogue_details,self.entries[selection[0]])


def main():
    try:root=tk.Tk()
    except tk.TclError:
        print('CMBA_GUI_UNAVAILABLE: Tk and a graphical session are required.',file=sys.stderr);return 2
    Application(root);root.mainloop();return 0
if __name__=='__main__':raise SystemExit(main())
