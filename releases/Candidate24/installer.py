"""Nexus AI independent installer. Import is inert; every mutation requires consent."""
from __future__ import annotations
import threading,contextlib,re,argparse,hashlib,json,os,pathlib,shutil,stat,subprocess,sys,tempfile,time,uuid,zipfile
HELPER_SHA256 = '0b721dc4533605f42ca1502e5b6595526edf454eb49a6526765e532b77c196e5'  # Packaging fills this with the companion file digest.
GUI_FILES = {'Nexus_AI_Installer_GUI.py': 'e134a6d2078633cd61a815fc5530b51b8a53e83dfa56ff674c053034fa74b839', 'Nexus_AI_Installer.png': 'a3f1c6abcc9b577527774179e13c2ad380e991d30163f45d252285bff91dcb0f', 'Nexus_AI_Installer.ico': '69f427721b34600252ff5685ccbb3650f0e6115ba3ea479d0a4f080da2a49c99'}  # Packaging fills this with GUI companion SHA-256 digests.
def _dependency_helper():
 import importlib.util
 folder=pathlib.Path(__file__).resolve().parent
 helper=folder/('Nexus_AI_Dependencies.py' if HELPER_SHA256 else 'dependencies.py')
 if not helper.is_file():raise SystemExit('Installation stopped: dependency helper is missing. Keep all installer files together and extract the complete package.')
 if HELPER_SHA256 and hashlib.sha256(helper.read_bytes()).hexdigest()!=HELPER_SHA256:raise SystemExit('Installation stopped: dependency helper integrity check failed. Extract a fresh complete package.')
 spec=importlib.util.spec_from_file_location('nexus_installer_dependencies',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module
dependencies=_dependency_helper()
dependency_plan=dependencies.dependency_plan;setup_dependencies=dependencies.setup_dependencies;recorded_python=dependencies.recorded_python
LIMIT=20_000_000
MARKER='.nexus-ai-independent.json'
_publication_local=threading.local()
@contextlib.contextmanager
def publication_lock(target,timeout=30):
 """Serialize only this installation's publication and launcher admission."""
 target=pathlib.Path(target).resolve()
 held=getattr(_publication_local,'held',set())
 if target in held:
  yield;return
 target.parent.mkdir(parents=True,exist_ok=True)
 lock=target.parent/('.'+target.name+'.publication.lock')
 if lock.is_symlink():raise ValueError('Installation lock must not be a symlink')
 with lock.open('a+b') as stream:
  stream.seek(0)
  if not stream.read(1):stream.write(b'0');stream.flush()
  end=time.monotonic()+timeout
  while True:
   stream.seek(0)
   try:
    if os.name=='nt':
     import msvcrt
     msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
    else:
     import fcntl
     fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    break
   except OSError:
    if time.monotonic()>=end:raise ValueError('Another installation or startup is in progress; retry after it finishes')
    time.sleep(.05)
  _publication_local.held=held|{target}
  try:yield
  finally:
   _publication_local.held=held
   if os.name=='nt':
    stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
   else:fcntl.flock(stream.fileno(),fcntl.LOCK_UN)

def safe_path(root,name):
 if not isinstance(name,str) or not name or any(c in name for c in '\\:< >"|?*'.replace(' ','')) or any(ord(c)<32 for c in name):raise ValueError('Unsafe package path')
 parts=name.split('/')
 if any(not x or x in ('.','..') or x.endswith((' ','.')) or x.split('.')[0].rstrip(' ').upper() in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))} for x in parts):raise ValueError('Unsafe package path')
 target=pathlib.Path(root).joinpath(*parts)
 if pathlib.Path(root).resolve() not in target.resolve().parents:raise ValueError('Path escapes target')
 return target

def _records(records,key,root):
 if not isinstance(records,list) or not records or len(records)>20000:raise ValueError('Invalid manifest records')
 seen=set()
 for r in records:
  if not isinstance(r,dict):raise ValueError('Invalid manifest record')
  name=r.get(key);safe_path(root,name)
  if name.casefold() in seen:raise ValueError('Duplicate package path')
  folded=name.casefold()
  if any(folded.startswith(x+'/') or x.startswith(folded+'/') for x in seen):raise ValueError('Conflicting package paths')
  seen.add(folded)
  if type(r.get('size')) is not int or not 0<=r['size']<LIMIT:raise ValueError('Invalid component size')
  if not isinstance(r.get('sha256'),str) or not re.fullmatch('[0-9a-f]{64}',r['sha256']):raise ValueError('Invalid component digest')
 return records

def verify_package(folder,staging):
 folder=pathlib.Path(folder);staging=pathlib.Path(staging)
 m=json.loads((folder/'Nexus_AI_Manifest.json').read_text(encoding='utf-8'))
 if not isinstance(m,dict) or m.get('schema')!=1 or m.get('product')!='Nexus AI Independent':raise ValueError('Wrong package identity')
 _records(m.get('parts'),'name',folder);_records(m.get('files'),'path',staging)
 if not isinstance(m.get('archive_sha256'),str) or not re.fullmatch('[0-9a-f]{64}',m['archive_sha256']):raise ValueError('Invalid archive digest')
 archive=staging.parent/('payload-'+str(time.time_ns())+'.zip')
 try:
  digest=hashlib.sha256()
  with archive.open('wb') as out:
   for record in m['parts']:
    p=safe_path(folder,record['name']);size=record['size']
    if type(size)!=int or not 0<size<LIMIT or p.stat().st_size!=size:raise ValueError('Invalid data-part size')
    data=p.read_bytes()
    if hashlib.sha256(data).hexdigest()!=record['sha256']:raise ValueError('Data-part integrity failure')
    digest.update(data);out.write(data)
  if digest.hexdigest()!=m['archive_sha256']:raise ValueError('Package integrity failure')
  expected={r['path']:r for r in m['files']}
  if len(expected)!=len(m['files']):raise ValueError('Duplicate manifest path')
  with zipfile.ZipFile(archive) as z:
   names=[i.filename for i in z.infolist()]
   if len(set(names))!=len(names) or set(names)!=set(expected):raise ValueError('Archive/manifest file mismatch')
   for info in z.infolist():
    r=expected[info.filename];target=safe_path(staging,info.filename)
    if stat.S_ISLNK(info.external_attr>>16) or info.is_dir():raise ValueError('Unexpected link/directory')
    if info.file_size!=r['size'] or not 0<=info.file_size<LIMIT:raise ValueError('Component exceeds 20 MB or wrong size')
    data=z.read(info)
    if hashlib.sha256(data).hexdigest()!=r['sha256']:raise ValueError('Component integrity failure')
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  if not (staging/'server.py').is_file():raise ValueError('Missing server entry point')
  (staging/MARKER).write_text(json.dumps({'product':m['product'],'installed_at':time.time(),'manifest_sha256':hashlib.sha256((folder/'Nexus_AI_Manifest.json').read_bytes()).hexdigest()}))
  return m
 finally:archive.unlink(missing_ok=True)

def install(folder,target,*,fresh=False):
 target=pathlib.Path(target).expanduser()
 if target.is_symlink():raise ValueError('Refusing linked installation directory')
 with publication_lock(target):return _install_locked(folder,target,fresh=fresh)

def _install_locked(folder,target,*,fresh=False):
 """Call only after caller obtains consent. All package checks precede replacement."""
 target=pathlib.Path(target).expanduser().resolve()
 if target.exists():
  try:
   marker=target/MARKER
   valid=not marker.is_symlink() and json.loads(marker.read_text(encoding='utf-8')).get('product')=='Nexus AI Independent'
  except (OSError,ValueError,AttributeError):valid=False
  if not valid:raise ValueError('Refusing to overwrite a folder not owned by this independent app')
 require_closed_app(target)
 target.parent.mkdir(parents=True,exist_ok=True)
 stage=pathlib.Path(tempfile.mkdtemp(prefix='.nexus-ai-stage-',dir=target.parent));backup=None
 try:
  verify_package(folder,stage)
  # Release payloads must never seed user data, even if built from a used checkout.
  for name in ('state','models','.venv','.runtimes','.nexus-python.json'):
   if (stage/name).exists():raise ValueError('Package contains saved app state or a runtime: '+name)
  if fresh or not target.exists():
   (stage/'state').mkdir()
   (stage/'state'/'workspace-id.json').write_text(json.dumps({'schema':1,'id':uuid.uuid4().hex}),encoding='utf-8')
  if target.exists():
   # Preserve only app-owned data; do not follow symlinks into other installations.
   for name in (('.venv','.runtimes') if fresh else ('state','models','.venv','.runtimes')):
    old=target/name
    if old.exists():
     if old.is_symlink():raise ValueError('Refusing linked user-data directory')
     shutil.copytree(old,stage/name,symlinks=True)
   old_build=target/'native'/'Nexus.cpp'/'build'
   if old_build.exists():
    if old_build.is_symlink():raise ValueError('Refusing linked native build directory')
    shutil.copytree(old_build,stage/'native'/'Nexus.cpp'/'build',symlinks=True,dirs_exist_ok=True)
   runtime_config=target/'.nexus-python.json'
   if runtime_config.is_file() and not runtime_config.is_symlink():shutil.copy2(runtime_config,stage/runtime_config.name)
   require_closed_app(target)
   backup=target.with_name(target.name+'.backup-'+str(time.time_ns()));target.rename(backup)
  try:stage.rename(target)
  except BaseException:
   if backup and not target.exists():backup.rename(target)
   raise
  return backup
 finally:
  if stage.exists():shutil.rmtree(stage)

def require_closed_app(target):
 """Default and custom-state launchers must both stop before replacement."""
 for name in ('launcher.lock','installation-running.lock'):
  lock=pathlib.Path(target)/'state'/name
  if not lock.exists():continue
  if lock.is_symlink():raise ValueError('App lock must not be a symlink')
  with lock.open('r+b') as stream:
   try:
    if os.name=='nt':
     import msvcrt
     msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
    else:
     import fcntl
     fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
   except OSError as exc:
    raise ValueError('Close Nexus AI using Stop server and exit before installing or updating. Saved data has not been changed.') from exc

def _shortcut_details(path):
 q=lambda value: "'"+str(value).replace("'","''")+"'"
 script="$s=(New-Object -ComObject WScript.Shell).CreateShortcut("+q(path)+");@{target=$s.TargetPath;arguments=$s.Arguments;working=$s.WorkingDirectory}|ConvertTo-Json -Compress"
 result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],check=True,capture_output=True,text=True)
 return json.loads(result.stdout)

def desktop_directory():
 """Ask Windows for the actual (possibly redirected) Desktop without creating it."""
 script=("$ErrorActionPreference='Stop';[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false);"
         "[Environment]::GetFolderPath([Environment+SpecialFolder]::DesktopDirectory,"
         "[Environment+SpecialFolderOption]::DoNotVerify)|ConvertTo-Json -Compress")
 result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],
                       check=True,capture_output=True,text=True,encoding='utf-8',timeout=30)
 value=json.loads(result.stdout.lstrip('\ufeff').strip())
 if not isinstance(value,str) or not value.strip() or not pathlib.Path(value).is_absolute():
  raise ValueError('Windows did not return an absolute Desktop folder; no shortcut was written.')
 return pathlib.Path(value)

def shortcut_plan(target):
 if os.name!='nt':return {'action':'skip','reason':'Windows shortcut not applicable'}
 target=pathlib.Path(target).resolve()
 desktop=desktop_directory()
 new=desktop/'Nexus AI.lnk';old=desktop/'Nexus AI Independent.lnk'
 def own(path):
  try:
   details=_shortcut_details(path)
   executable=pathlib.Path(details['target'])
   expected='"'+str(target/'installer'/'launch.py')+'"'
   valid_python=executable.name.lower() in ('python.exe','pythonw.exe')
   return valid_python and details['arguments']==expected and pathlib.Path(details['working']).resolve()==target
  except (OSError,ValueError,KeyError,subprocess.SubprocessError):return False
 if new.exists():
  return {'action':'update' if own(new) else 'skip','path':str(new),'reason':'Update verified app shortcut' if own(new) else 'Existing Nexus AI shortcut is not verified as this app; leave unchanged'}
 if old.exists() and own(old):return {'action':'migrate','path':str(new),'old':str(old),'reason':'Rename verified app shortcut to Nexus AI and apply modern icon'}
 return {'action':'create','path':str(new),'reason':'Create Nexus AI desktop shortcut with modern icon'}

def make_shortcut(target,plan=None):
 """Execute only the approved shortcut change; preserve unrelated shortcuts."""
 target=pathlib.Path(target).resolve();current=shortcut_plan(target)
 if plan is not None and current!=plan:raise ValueError('Shortcut changed after preflight; left unchanged')
 plan=current
 if plan['action']=='skip':return None
 sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
 selected=recorded_python(target)
 python=selected.with_name('pythonw.exe') if selected else pathlib.Path(sys.executable)
 if not python.exists():python=selected or pathlib.Path(sys.executable)
 path=pathlib.Path(plan['path'])
 path.parent.mkdir(parents=True,exist_ok=True)
 q=lambda value:"'"+str(value).replace("'","''")+"'"
 script="$ErrorActionPreference='Stop';$s=(New-Object -ComObject WScript.Shell).CreateShortcut("+q(path)+");$s.TargetPath="+q(python)+";$s.Arguments="+q('"'+str(target/'installer'/'launch.py')+'"')+";$s.WorkingDirectory="+q(target)+";$s.IconLocation="+q(str(target/'assets'/'nexus_ai.ico')+',0')+";$s.Save()"
 subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],check=True,timeout=30)
 if plan['action']=='migrate':pathlib.Path(plan['old']).unlink()
 return path

def setup_desktop(target,plan=None,emit=print):
 sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
 return setup_dependencies(target,plan=plan,emit=emit)


def build_native(target,backend):
 """Build only with existing tools, after an explicit HIP/CPU choice."""
 if backend not in ('hip','cpu'):raise ValueError('Choose hip or cpu explicitly')
 target=pathlib.Path(target).resolve();script=target/'native'/'Nexus.cpp'/'scripts'/'build.py'
 if not script.is_file():raise ValueError('Native source build script is missing')
 folder=script.parents[1]/'build';folder.mkdir(parents=True,exist_ok=True)
 binary=folder/('nexus.exe' if os.name=='nt' else 'nexus')
 candidate=folder/(binary.name+'.candidate-'+str(time.time_ns()))
 # The existing build script locates hipcc/g++/clang++; it never installs them.
 try:
  subprocess.run([sys.executable,str(script),'--backend',backend,'--output',str(candidate)],check=True,cwd=target)
  if not candidate.is_file() or candidate.stat().st_size==0:raise ValueError('Compiler did not produce a native executable')
  if binary.exists():shutil.copy2(binary,binary.with_name(binary.name+'.backup-'+str(time.time_ns())))
  os.replace(candidate,binary)
  return binary
 finally:candidate.unlink(missing_ok=True)

def existing_hip_compiler():
 compiler=shutil.which('hipcc') or shutil.which('hipcc.bat')
 if not compiler and os.environ.get('HIP_PATH'):
  candidate=pathlib.Path(os.environ['HIP_PATH'])/'bin'/('hipcc.bat' if os.name=='nt' else 'hipcc')
  if candidate.is_file():compiler=str(candidate)
 return compiler

NATIVE_FEATURE_REVISION='nexus-integration-mistral3-v2'

def probe_native_build(target,binary):
 """Read-only, bounded probe of this app's own non-linked native executable."""
 target=pathlib.Path(target).resolve();binary=pathlib.Path(binary)
 try:
  marker=target/MARKER
  if marker.is_symlink() or json.loads(marker.read_text(encoding='utf-8')).get('product')!='Nexus AI Independent':return None
  if not binary.is_file() or binary.is_symlink() or binary.resolve()!=binary.absolute():return None
  if target not in binary.resolve().parents:return None
  result=subprocess.run([str(binary),'--build-info'],cwd=target,capture_output=True,text=True,check=True,timeout=3)
  info=json.loads(result.stdout)
  if not isinstance(info,dict):return None
  if (info.get('feature_revision')!=NATIVE_FEATURE_REVISION or
      not isinstance(info.get('architectures'),list) or 'mistral3' not in info['architectures'] or
      info.get('compiled_backend') not in ('cpu-only','hip-gfx1100') or
      info.get('hardware_qualified') is not False):return None
  return info
 except (OSError,ValueError,AttributeError,subprocess.SubprocessError):return None

def make_plan(target,desktop=True,native=True,shortcut=True,rebuild_native=False,fresh=False):
 target=pathlib.Path(target).expanduser().resolve()
 sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
 binary=target/'native'/'Nexus.cpp'/'build'/('nexus.exe' if os.name=='nt' else 'nexus')
 existing_native=binary.is_file() and (target/MARKER).is_file()
 build_info=probe_native_build(target,binary) if existing_native else None
 needs_build=rebuild_native or not build_info
 compiler=existing_hip_compiler() if native and needs_build else None
 if compiler:
  notice=('Rebuild app-local native engine with backup' if existing_native else 'Build app-local native engine')+' for Ministral 3 support using the listed existing HIP compiler. Build success is not model/GPU qualification.'
 elif build_info:
  notice='Reuse existing native Ministral 3 feature build unchanged ('+build_info['compiled_backend']+'). Features reported by --build-info; hardware and model execution are not qualified.'
  if rebuild_native:notice+=' Requested rebuild cannot run: '+('native builds disabled by --no-native.' if not native else 'no existing HIP compiler found.')
 else:
  notice=('Existing native engine preserved unchanged. ' if existing_native else 'No existing native engine. ')+'Native Ministral 3 is NOT READY: a compatible build is required; '+('native builds disabled by --no-native.' if not native else 'no existing HIP compiler found.')
 return {'target':str(target),'update':target.exists(),'fresh':bool(fresh or not target.exists()),'existing_native':str(binary) if existing_native else None,
         'native_build_info':build_info,'native_notice':notice,
         'dependencies':dependency_plan(target) if desktop else None,
         'compiler':compiler,
         'shortcut':shortcut_plan(target) if shortcut else {'action':'skip','reason':'Shortcut disabled'}}

def select_startup_model(path):
 """Read only a chosen GGUF header; never copy or execute a model."""
 model=pathlib.Path(path).expanduser().resolve(strict=True)
 if not model.is_file() or model.suffix.lower()!='.gguf':raise ValueError('Choose an existing .gguf model file.')
 with model.open('rb') as stream:
  if stream.read(4)!=b'GGUF':raise ValueError('This file does not have a GGUF header.')
 info=model.stat()
 return {'action':'set','schema':1,'path':str(model),'engine':'webgpu','enabled':True,'size':info.st_size,'mtime_ns':info.st_mtime_ns}

def save_startup_model(target,selection):
 if not selection:return  # Untouched picker preserves the existing default.
 if selection.get('action')=='set':
  current=select_startup_model(selection['path'])
  if any(current[key]!=selection[key] for key in ('path','size','mtime_ns')):
   raise ValueError('Selected model changed after approval. Select it again before saving a default.')
  record={key:current[key] for key in ('schema','path','engine','enabled')}
 elif selection.get('action')=='clear':record={'schema':1,'path':None,'engine':'webgpu','enabled':False}
 else:raise ValueError('Unknown default model action')
 state=pathlib.Path(target)/'state'
 if state.is_symlink():raise ValueError('App state must not be a symlink')
 state.mkdir(exist_ok=True)
 destination=state/'startup-model.json'
 if destination.is_symlink():raise ValueError('Default model configuration must not be a symlink')
 fd,name=tempfile.mkstemp(prefix='startup-model-',suffix='.tmp',dir=state)
 try:
  with os.fdopen(fd,'w',encoding='utf-8') as stream:json.dump(record,stream,indent=2)
  os.replace(name,destination)
 finally:
  if os.path.exists(name):os.unlink(name)

def show_plan(plan):
 print('Nexus AI installation plan')
 print(('Fresh install' if plan.get('fresh') else 'Update' if plan['update'] else 'Create')+' app files: '+plan['target'])
 print('Apply Nexus AI title and modern app/tray/taskbar/shortcut icon from assets/nexus_ai.ico.')
 print('Fresh install: no saved chats, memories, documents, adapters, settings, model registrations or default model. Use a new isolated browser workspace. The old installation is kept only in the reported backup; it is not loaded.' if plan.get('fresh') else 'Update: preserve saved app data and runtime; keep a backup. Previous chats are not automatically inserted into a new conversation.')
 dep=plan['dependencies']
 if dep:
  print(('Reuse runtime: ' if dep['reuse'] else 'Create app-local runtime: ')+dep['python'])
  for name,item in dep['reused'].items():print('Reuse '+name+' '+item['version']+' (version and import checked)')
  for note in dep['notes']:print(note)
  print('Add from official PyPI: '+(', '.join(dep['requirements'])+' and required dependencies' if dep['requirements'] else 'nothing'))
  print('Save runtime selection: '+str(pathlib.Path(plan['target'])/'.nexus-python.json'))
 if plan.get('native_notice'):print(plan['native_notice'])
 elif plan.get('existing_native'):print('Existing native engine kept: '+plan['existing_native']+'. Compatibility checked when loading.')
 print('Native HIP build: '+('use existing '+plan['compiler']+'; write app native/Nexus.cpp/build/nexus executable (backup existing)' if plan['compiler'] else 'unavailable/skipped; no compiler installation or CPU fallback'))
 selection=plan.get('startup_model')
 if selection:
  if selection.get('action')=='set':print('Default startup model (WebGPU): '+selection['path']+'. Reference the existing disk file without copying it; load automatically when the app starts. Architecture, memory and runtime compatibility are checked at load time. If no hardware profile is saved, choose your card on first launch before the model auto-loads.')
  else:print('Clear default startup model. The model file itself is not deleted.')
 else:print('Default startup model: none (fresh install).' if plan.get('fresh') else 'Default startup model: preserve current choice (no new model selected).')
 print('Shortcut: '+plan['shortcut']['reason']+(' at '+plan['shortcut']['path'] if 'path' in plan['shortcut'] else ''))
 if plan.get('autolaunch'):print('After successful installation, open this installed Nexus AI app full screen using its selected runtime; restore its existing window if already running. The installer closes after a confirmed desktop launch. Launch errors remain visible. Escape exits full screen; F11 toggles it.')
 print('No existing packages will be uninstalled, upgraded or downgraded. No drivers, shared runtimes, PATH, registry or security settings changed.')
 print('If an unexpected requirement or changed prerequisite appears, that step stops rather than expanding this plan.')

def launch_gui(args,target):
 import importlib.util
 folder=pathlib.Path(__file__).resolve().parent
 if GUI_FILES:
  for name,digest in GUI_FILES.items():
   path=folder/name
   if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
    raise ValueError('Installer GUI companion missing or modified: '+name+'. Extract a fresh complete package.')
  helper=folder/'Nexus_AI_Installer_GUI.py';art=folder/'Nexus_AI_Installer.png';icon=folder/'Nexus_AI_Installer.ico'
 else:
  helper=folder/'gui.py';art=folder.parent/'assets'/'nexus_ai_256.png';icon=folder.parent/'assets'/'nexus_ai.ico'
 try:
  spec=importlib.util.spec_from_file_location('nexus_installer_gui',helper)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  return module.run(sys.modules[__name__],args,target,art,icon)
 except (ImportError,module.tk.TclError if 'module' in locals() and hasattr(module,'tk') else ImportError) as exc:
  message='Graphical installer unavailable: '+str(exc)+'. No GUI dependency was installed. Run this installer with --cli for the same complete plan and one confirmation.'
  print(message,file=sys.stderr)
  if os.name=='nt':
   import ctypes
   ctypes.windll.user32.MessageBoxW(None,message,'Nexus AI',0x10)
  return 2

def main(argv=None):
 parser=argparse.ArgumentParser(description='Nexus AI installer: one plan, one INSTALL confirmation.')
 parser.add_argument('--cli',action='store_true',help='Use the terminal plan and INSTALL confirmation')
 parser.add_argument('--gui',action='store_true',help='Use the graphical installer (requires existing tkinter)')
 parser.add_argument('--no-launch',action='store_true',help='Install without automatically opening the installed app')
 parser.add_argument('--fresh',action='store_true',help='Start with zero saved user data; keep the old install only in the rollback backup')
 parser.add_argument('--target');parser.add_argument('--dry-run',action='store_true')
 parser.add_argument('--package-dir',default=str(pathlib.Path(__file__).resolve().parent))
 parser.add_argument('--rebuild-native',action='store_true',help='Explicitly rebuild the existing app native engine with backup, using an already installed HIP compiler')
 parser.add_argument('--no-desktop',action='store_true');parser.add_argument('--no-native',action='store_true');parser.add_argument('--no-shortcut',action='store_true')
 a=parser.parse_args(argv)
 base=pathlib.Path(os.environ.get('LOCALAPPDATA',str(pathlib.Path.home()/'.local/share')))
 target=pathlib.Path(a.target or base/'NexusAIIndependent').expanduser().resolve()
 if not a.dry_run and (a.gui or (os.name=='nt' and not a.cli)):
  return launch_gui(a,target)
 plan=make_plan(target,desktop=os.name=='nt' and not a.no_desktop,native=not a.no_native,shortcut=not a.no_shortcut,rebuild_native=a.rebuild_native,fresh=a.fresh)
 plan['autolaunch']=not a.no_launch
 show_plan(plan)
 if a.dry_run:return 0
 if input('Type INSTALL to approve this complete plan, or press Enter to cancel: ').strip()!='INSTALL':print('Cancelled. Nothing changed.');return 1
 code=execute_plan(a.package_dir,plan)
 if code==0 and plan['autolaunch']:
  try:
   receipt=launch_app(target);print('Installation complete. Launch confirmation:',receipt['status'])
  except (OSError,RuntimeError,ValueError) as exc:
   print('Installed, but launch was not confirmed:',exc,file=sys.stderr);return 3
 return code

def launch_app(target):
 """Use only this verified installed application's launch-confirmation helper."""
 import importlib.util
 target=pathlib.Path(target).resolve()
 helper=target/'installer'/'launch_after_install.py'
 if not (target/MARKER).is_file() or not helper.is_file():
  raise RuntimeError('Installation succeeded, but the app launch helper is missing. See '+str(target/'state'/'NexusAI.log'))
 spec=importlib.util.spec_from_file_location('nexus_installed_launch',helper)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module.launch_installed(target)

def execute_plan(folder,plan,report=None):
 with publication_lock(plan['target']):return _execute_plan_locked(folder,plan,report)

def _execute_plan_locked(folder,plan,report=None):
 """Execute the already reviewed plan; never asks additional questions."""
 target=pathlib.Path(plan['target']); failures=[]
 output=report or (lambda stage,message: print(message));activity=[]
 def emit(stage,message):
  activity.append((stage,message));output(stage,message)
 emit('files','Verifying package and installing app files…')
 backup=install(folder,target,fresh=True) if plan.get('fresh') else install(folder,target)
 emit('files', 'App installed. Backup: '+str(backup or 'not needed'))
 emit('completed','files')
 if plan.get('startup_model'):
  try:
   save_startup_model(target,plan['startup_model'])
   emit('model','Default startup model saved. Existing model file was not copied or modified.')
  except (OSError,ValueError,KeyError) as error:failures.append('Default startup model: '+str(error))
 if plan['dependencies']:
  emit('runtime', 'Preparing approved app-local desktop runtime; package output is also available in the launching console.')
  try:
   setup_desktop(target,plan=plan['dependencies'],emit=lambda message:emit('runtime',message))
   emit('completed','runtime')
  except (OSError,RuntimeError,subprocess.SubprocessError) as e:failures.append('Desktop runtime: '+str(e))
 if plan.get('native_notice'):emit('native',plan['native_notice'])
 if plan['compiler']:
  emit('native', 'Building with the approved existing HIP compiler. This may take several minutes.')
  try:
   if existing_hip_compiler()!=plan['compiler']:raise ValueError('HIP compiler changed after preflight; rerun installer')
   binary=build_native(target,'hip');emit('native','Native executable built: '+str(binary))
   emit('native','Build completion is not model/GPU qualification; run a model check and benchmark before trusting it.')
   emit('completed','native')
  except (OSError,ValueError,subprocess.SubprocessError) as e:failures.append('Native build: '+str(e))
 if plan['shortcut']['action']!='skip':
  emit('shortcut', 'Applying the approved Nexus AI shortcut and modern icon.')
  try:
   emit('shortcut','Shortcut: '+str(make_shortcut(target,plan=plan['shortcut'])))
   emit('completed','shortcut')
  except (OSError,ValueError,subprocess.SubprocessError) as e:failures.append('Shortcut: '+str(e))
 for failure in failures:emit('warning','Not completed: '+failure)
 if plan.get('native_notice') and not plan.get('compiler') and not plan.get('native_build_info'):
  emit('warning','App installation does not add native Ministral 3 support: '+plan['native_notice'])
 emit('launch','Start with: '+sys.executable+' '+str(target/'installer'/'launch.py'))
 emit('result','To undo an update, close this app and restore the reported backup folder. No global uninstall needed.')
 # Keep native NOT READY/build warnings accessible after the GUI closes.
 if target.is_dir():
  try:
   state=target/'state';state.mkdir(exist_ok=True)
   with (state/'NexusAI.log').open('a',encoding='utf-8') as log:
    log.write('\nINSTALLATION ACTIVITY\n')
    for stage,message in activity:log.write(stage+': '+str(message)+'\n')
  except OSError as error:
   output('warning','Could not save installation activity: '+str(error))
 return 2 if failures else 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except (ValueError,RuntimeError,OSError,zipfile.BadZipFile) as e:print('Installation stopped safely:',e,file=sys.stderr);raise SystemExit(2)
