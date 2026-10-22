"""Dependency-free, consent-gated installer UI. tkinter ships with Windows Python.

Workers never access Tk. A queue carries results to the UI thread. Once approved,
closing is deferred until native/package/file operations finish safely.
"""
from __future__ import annotations
import contextlib
import io
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk,filedialog

BG='#071121'; PANEL='#0d1c30'; BORDER='#29405e'; TEXT='#eff7ff'; MUTED='#b4c6da'; ACCENT='#88d9ff'; PURPLE='#aa9aff'

class StageProgress:
    """Equal completed-work stages, not bytes or estimated elapsed time.

    Reserve the final stage for execute_plan's successful return so no intermediate
    event, duplicate or partial failure can make the bar falsely show 100%.
    """
    def __init__(self,plan):
        self.stages=['files']
        if plan.get('dependencies'): self.stages.append('runtime')
        if plan.get('compiler'): self.stages.append('native')
        if plan.get('shortcut',{}).get('action','skip')!='skip': self.stages.append('shortcut')
        self.stages.append('finalize'); self.completed=set(); self.value=0
    def complete(self,stage):
        if stage in self.stages and stage!='finalize': self.completed.add(stage)
        self.value=100*len(self.completed)//len(self.stages)
        return self.value
    def finish(self,success):
        if success: self.completed=set(self.stages); self.value=100
        return self.value

class Controller:
    """Small independently testable state machine; no mutation before approve."""
    def __init__(self, api, args, target):
        self.api=api; self.args=args; self.target=target
        self.events=queue.Queue(); self.state='checking'; self.plan=None; self.code=1; self.progress=None; self.receipt=None
    def preflight(self):
        try:
            plan=self.api.make_plan(self.target,desktop=os.name=='nt' and not self.args.no_desktop,
                native=not self.args.no_native,shortcut=not self.args.no_shortcut,rebuild_native=self.args.rebuild_native,
                fresh=getattr(self.args,'fresh',False))
            plan['autolaunch']=not getattr(self.args,'no_launch',False)
            stream=io.StringIO()
            with contextlib.redirect_stdout(stream): self.api.show_plan(plan)
            self.plan=plan; self.progress=StageProgress(plan)
            self.events.put(('ready',stream.getvalue()))
        except BaseException as exc: self.events.put(('error',str(exc)))
    def set_startup_model(self,path=None,clear=False):
        if self.state!='ready':return False
        self.plan['startup_model']={'action':'clear'} if clear else self.api.select_startup_model(path)
        return True
    def toggle_fresh(self):
        if self.state!='ready' or not self.plan.get('update'):return False
        self.plan['fresh']=not self.plan.get('fresh',False)
        return True
    def plan_text(self):
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):self.api.show_plan(self.plan)
        return stream.getvalue()
    def accept_ready(self):
        if self.state=='checking': self.state='ready'
    def approve(self):
        if self.state!='ready' or self.plan is None: return False
        self.state='installing'
        threading.Thread(target=self._execute,daemon=False,name='Nexus installer').start()
        return True
    def report(self,stage,text):
        if stage=='completed':
            self.events.put(('progress',self.progress.complete(text)))
        else: self.events.put(('stage',(stage,text)))
    def _execute(self):
        try:
            self.code=self.api.execute_plan(self.args.package_dir,self.plan,report=self.report)
            self.events.put(('progress',self.progress.finish(self.code==0)))
            if self.code!=0:
                self.events.put(('finished',self.code)); return
            self.events.put(('installed',None))
            if self.plan.get('autolaunch'):
                try:
                    self.receipt=self.api.launch_app(self.target)
                except BaseException as exc:
                    self.code=3; self.events.put(('launch_error',str(exc))); return
                self.events.put(('launched',self.receipt))
            self.events.put(('finished',0))
        except BaseException as exc:
            self.code=2; self.events.put(('error',str(exc)))
    def cancel(self):
        if self.state=='installing': return False
        self.state='closed'; return True


def prepare_process(icon):
    """Only this process: DPI awareness and taskbar identity, never OS settings."""
    if os.name!='nt': return
    import ctypes
    try: ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except (AttributeError,OSError):
        try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError,OSError): pass
    try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('NexusAI.Installer')
    except (AttributeError,OSError): pass

class InstallerWindow:
    def __init__(self,root,controller,art,icon):
        self.root=root; self.controller=controller
        root.title('Nexus AI'); root.configure(bg=BG)
        scale=max(1.0,float(root.winfo_fpixels('1i'))/96)
        # Logical geometry scales with the monitor, bounded by the available desktop.
        width=min(round(1040*scale),root.winfo_screenwidth()-40)
        height=min(round(880*scale),root.winfo_screenheight()-70)
        root.geometry(f'{width}x{height}'); root.minsize(min(round(720*scale),width),min(round(620*scale),height))
        if os.name=='nt' and icon.is_file(): root.iconbitmap(str(icon))
        self.logo=tk.PhotoImage(file=str(art))
        root.iconphoto(True,self.logo)
        self.brand_image=self.logo.subsample(max(1,round(256/(64*scale))))
        style=ttk.Style(root); style.theme_use('clam')
        style.configure('Nexus.Horizontal.TProgressbar',troughcolor=PANEL,background=ACCENT,bordercolor=BORDER,lightcolor=ACCENT,darkcolor=ACCENT)
        style.configure('Vertical.TScrollbar',background=BORDER,troughcolor=PANEL,bordercolor=PANEL,arrowcolor=TEXT)
        compact=height/scale<740
        margin=round((14 if compact else 26)*scale)
        outer=tk.Frame(root,bg=BG,padx=margin,pady=margin); outer.pack(fill='both',expand=True)
        # Allocate the footer FIRST, from the bottom. The plan can shrink, never
        # steal the action buttons' requested height at high DPI or low height.
        self.footer=tk.Frame(outer,bg=BG)
        self.footer.pack(side='bottom',fill='x')
        self.footer.columnconfigure(0,weight=1)
        self.footer.rowconfigure(4,minsize=round(48*scale))
        self.content=tk.Frame(outer,bg=BG)
        self.content.pack(side='top',fill='both',expand=True)
        self.content.columnconfigure(0,weight=1)
        self.content.rowconfigure(4,weight=1,minsize=0)
        header=tk.Frame(self.content,bg=BG); header.grid(row=0,column=0,sticky='ew')
        tk.Label(header,image=self.brand_image,bg=BG).pack(side='left',padx=(0,18))
        brand=tk.Frame(header,bg=BG); brand.pack(side='left')
        self.label(brand,'Nexus AI',20 if compact else 26,bold=True).pack(anchor='w')
        self.label(brand,'YOUR SPACE. YOUR INTELLIGENCE.',9,color=ACCENT).pack(anchor='w',pady=(2,0))
        self.label(header,'DESKTOP SETUP',10,color=PURPLE).pack(side='right')
        tk.Frame(self.content,bg=BORDER,height=1).grid(row=1,column=0,sticky='ew',pady=(10,10) if compact else (22,20))
        self.heading=self.label(self.content,'One plan. One install.',18 if compact else 23,bold=True); self.heading.grid(row=2,column=0,sticky='w')
        self.subtitle=self.label(self.content,'Review everything below. Nothing changes until you choose Install.',11,color=MUTED)
        self.subtitle.grid(row=3,column=0,sticky='ew',pady=(4,8) if compact else (6,18))
        card=tk.Frame(self.content,bg=PANEL,highlightbackground=BORDER,highlightthickness=1,padx=18,pady=15)
        card.grid(row=4,column=0,sticky='nsew')
        card.columnconfigure(0,weight=1); card.rowconfigure(1,weight=1,minsize=0)
        line=tk.Frame(card,bg=PANEL); line.grid(row=0,column=0,columnspan=2,sticky='ew',pady=(0,8))
        self.label(line,'INSTALLATION PLAN',10,color=ACCENT,bg=PANEL,bold=True).pack(side='left')
        self.mode_button=tk.Button(line,text='Checking install mode…',command=self.toggle_fresh,bg=PANEL,fg=TEXT,relief='flat',state='disabled')
        self.mode_button.pack(side='left',padx=(12,0))
        self.badge=self.label(line,'CHECKING',9,color=PURPLE,bg=PANEL); self.badge.pack(side='right')
        self.body=tk.Text(card,bg=PANEL,fg=TEXT,insertbackground=TEXT,relief='flat',borderwidth=0,
            wrap='word',font=('Segoe UI',11),padx=2,pady=4,spacing1=4,spacing3=8,height=1,width=1,
            selectbackground='#315776',selectforeground=TEXT,takefocus=True)
        scroll=ttk.Scrollbar(card,orient='vertical',command=self.body.yview)
        self.body.configure(yscrollcommand=scroll.set)
        scroll.grid(row=1,column=1,sticky='ns'); self.body.grid(row=1,column=0,sticky='nsew')
        self.set_text('Checking existing runtimes, packages, native engine and desktop shortcut…\n\nThis is read-only. No packages or GUI dependencies are installed during this check.')
        model=tk.Frame(self.content,bg=BG);model.grid(row=5,column=0,sticky='ew',pady=(8,0));model.columnconfigure(0,weight=1)
        self.model_label=self.label(model,'Optional: choose an existing GGUF as the default startup model (WebGPU).',10,color=MUTED)
        self.model_label.grid(row=0,column=0,columnspan=3,sticky='ew',pady=(0,5))
        self.model_choice=self.label(model,'Keep current default / no new selection',10,color=TEXT)
        self.model_choice.grid(row=1,column=0,sticky='ew',padx=(0,8))
        self.model_browse=tk.Button(model,text='Browse GGUF…',command=self.choose_model,bg=PANEL,fg=TEXT,relief='flat',padx=12,pady=6,state='disabled')
        self.model_browse.grid(row=1,column=1,padx=(0,6))
        self.model_clear=tk.Button(model,text='Clear default',command=self.clear_model,bg=PANEL,fg=TEXT,relief='flat',padx=12,pady=6,state='disabled')
        self.model_clear.grid(row=1,column=2)
        self.status=self.label(self.footer,'Preparing your complete plan…',11,color=MUTED); self.status.grid(row=0,column=0,sticky='ew',pady=(10,5))
        self.progress_label=self.label(self.footer,'Installation stages: 0%',10,color=MUTED); self.progress_label.grid(row=1,column=0,sticky='ew',pady=(0,5))
        self.progress=ttk.Progressbar(self.footer,mode='determinate',maximum=100,value=0,style='Nexus.Horizontal.TProgressbar'); self.progress.grid(row=2,column=0,sticky='ew')
        self.safety=self.label(self.footer,'App-local setup • Existing packages preserved • No drivers or system settings changed',10,color=MUTED)
        self.safety.grid(row=3,column=0,sticky='ew',pady=(8,8))
        actions=tk.Frame(self.footer,bg=BG); actions.grid(row=4,column=0,sticky='ew'); actions.columnconfigure(1,weight=1)
        self.cancel_button=tk.Button(actions,text='Cancel',command=self.close,bg=PANEL,fg=TEXT,activebackground=BORDER,activeforeground=TEXT,
            relief='flat',font=('Segoe UI',11),padx=25,pady=11,cursor='hand2')
        self.cancel_button.grid(row=0,column=0,sticky='w')
        self.install_button=tk.Button(actions,text='Install',command=self.approve,bg=ACCENT,fg='#05223a',activebackground='#b8eaff',activeforeground='#05223a',
            disabledforeground='#4f6a80',relief='flat',font=('Segoe UI',12,'bold'),padx=40,pady=10,cursor='hand2',state='disabled')
        self.install_button.grid(row=0,column=2,sticky='e')
        def reflow(event):
            if event.widget is root:
                available=max(120,event.width-2*margin)
                for label in (self.heading,self.subtitle,self.status,self.safety,self.model_label): label.configure(wraplength=available)
                self.model_choice.configure(wraplength=max(120,available-280))
        for label in (self.heading,self.subtitle,self.status,self.safety): label.configure(wraplength=max(120,width-2*margin))
        self.model_label.configure(wraplength=max(120,width-2*margin));self.model_choice.configure(wraplength=max(120,width-2*margin-280))
        root.bind('<Configure>',reflow)
        root.protocol('WM_DELETE_WINDOW',self.close)
        root.after(80,self.poll)
    def label(self,parent,text,size,color=TEXT,bg=BG,bold=False):
        return tk.Label(parent,text=text,font=('Segoe UI',size,'bold' if bold else 'normal'),bg=bg,fg=color,anchor='w',justify='left')
    def set_text(self,text):
        self.body.configure(state='normal'); self.body.delete('1.0','end'); self.body.insert('end',text); self.body.configure(state='disabled')
    def append(self,text):
        self.body.configure(state='normal'); self.body.insert('end','\n'+text+'\n'); self.body.configure(state='disabled'); self.body.see('end')
    def choose_model(self):
        if self.controller.state!='ready':return
        path=filedialog.askopenfilename(parent=self.root,title='Choose default startup GGUF',filetypes=[('GGUF models','*.gguf'),('All files','*.*')])
        if not path:return
        try:
            if self.controller.set_startup_model(path):
                self.model_choice.configure(text=path);self.set_text(self.controller.plan_text())
                self.status.configure(text='Default model added to the plan. Choose Install to approve.')
        except (OSError,ValueError) as error:self.status.configure(text='Model was not selected: '+str(error))
    def refresh_mode(self):
        fresh=self.controller.plan.get('fresh',False)
        self.mode_button.configure(text='Fresh install — no saved data' if fresh else 'Update — keep saved data',state='normal' if self.controller.plan.get('update') else 'disabled')
        if not self.controller.plan.get('startup_model'):
            self.model_choice.configure(text='No default model' if fresh else 'Keep current default / no new selection')
    def toggle_fresh(self):
        if self.controller.toggle_fresh():
            self.refresh_mode();self.set_text(self.controller.plan_text())
            self.status.configure(text='Install mode changed. The plan above shows which data will be kept.')
    def clear_model(self):
        if self.controller.set_startup_model(clear=True):
            self.model_choice.configure(text='Clear default on install; keep all model files')
            self.set_text(self.controller.plan_text())
    def approve(self):
        if not self.controller.approve(): return
        self.install_button.configure(state='disabled'); self.cancel_button.configure(state='disabled')
        self.model_browse.configure(state='disabled');self.model_clear.configure(state='disabled')
        self.mode_button.configure(state='disabled')
        self.heading.configure(text='Making it yours.'); self.subtitle.configure(text='Installing only the plan you approved. You can keep this window open while setup runs.')
        self.badge.configure(text='INSTALLING',fg=ACCENT)
        self.append('── Installation activity ──')
        self.safety.configure(text='For a safe install, closing is available again when the current operations finish.')
    def close(self):
        if not self.controller.cancel():
            self.status.configure(text='Installation is still running. Close is available when operations finish safely.'); return
        self.root.destroy()
    def poll(self):
        try:
            while True:
                kind,value=self.controller.events.get_nowait()
                if self.controller.state=='closed': return
                if kind=='ready':
                    self.controller.accept_ready(); self.set_text(value)
                    self.refresh_mode()
                    self.badge.configure(text='READY TO REVIEW',fg='#79e0be'); self.status.configure(text='Ready. Install approves every change shown above.')
                    self.install_button.configure(state='normal'); self.install_button.focus_set()
                    self.model_browse.configure(state='normal');self.model_clear.configure(state='normal')
                elif kind=='progress':
                    self.progress.configure(value=value)
                    self.progress_label.configure(text=f'Installation stages: {value}%')
                elif kind=='installed':
                    self.heading.configure(text='Installed. Opening Nexus AI…' if self.controller.plan.get('autolaunch') else 'Installation complete.')
                    self.status.configure(text='100% installed. Waiting for the app to confirm startup…' if self.controller.plan.get('autolaunch') else 'Installation complete.')
                    self.append('Installation completed successfully. All installation stages: 100%.')
                elif kind=='launched':
                    status=value.get('status','')
                    message={'desktop_shown':'Nexus AI confirmed its desktop window is shown.', 'desktop_restored':'Nexus AI confirmed its existing desktop window was restored.', 'browser_started':'The OS accepted the Nexus AI browser launch. Browser rendering is not verified.'}.get(status,'Launch confirmation received.')
                    self.append(message)
                elif kind=='stage':
                    stage,text=value; self.status.configure(text={'files':'Installing verified app files…','runtime':'Preparing desktop runtime…','native':'Building native engine…','shortcut':'Setting up desktop shortcut…'}.get(stage,'Finishing approved setup…')); self.append(text)
                elif kind in ('finished','error','launch_error'):
                    self.controller.state='finished'; self.cancel_button.configure(state='normal',text='Close')
                    success=kind=='finished' and value==0
                    launch_failed=kind=='launch_error'
                    self.controller.code=0 if success else (3 if launch_failed else 2)
                    self.heading.configure(text='You’re ready.' if success else ('Installed. Launch needs attention.' if launch_failed else 'Setup needs attention.'))
                    self.badge.configure(text='COMPLETE' if success else 'REVIEW DETAILS',fg='#79e0be' if success else '#ffb3b3')
                    self.subtitle.configure(text='Nexus AI is installed. Review the confirmed launch details below.' if success else ('Installation is complete, but app startup was not confirmed. See the error and app log below.' if launch_failed else 'Some installation stages did not complete. The app was not launched.'))
                    self.status.configure(text=(('Installation complete. Browser handoff accepted.' if self.controller.receipt.get('status')=='browser_started' else 'Installation complete. App window confirmed.') if self.controller.receipt else 'Installation complete.') if success else ('Installation complete. App launch was not confirmed.' if launch_failed else 'Some steps did not complete. See the activity details.'))
                    self.safety.configure(text='You can now safely close this installer.')
                    if kind=='error': self.append('Installation stopped: '+value)
                    if launch_failed:self.append('Installed, but launch was not confirmed: '+value)
                    self.install_button.configure(state='disabled'); self.cancel_button.focus_set()
                    # Close only after a matching desktop receipt, never on an
                    # intermediate 100% event or an unverified browser handoff.
                    if success and self.controller.receipt and self.controller.receipt.get('status') in ('desktop_shown','desktop_restored'):
                        self.status.configure(text='Nexus AI is open. Closing installer…')
                        self.root.after(250,self.close)
                        return
        except queue.Empty: pass
        self.root.after(80,self.poll)

def run(api,args,target,art,icon):
    prepare_process(icon)
    root=tk.Tk(); controller=Controller(api,args,target)
    window=InstallerWindow(root,controller,art,icon)
    threading.Thread(target=controller.preflight,daemon=True,name='Nexus preflight').start()
    root.mainloop()
    return controller.code
