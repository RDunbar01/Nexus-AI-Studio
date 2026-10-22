"""Reuse verified Python dependencies without changing global installations.

Only the installer interpreter's regular base and this app's recorded runtime are
examined. No other applications' environments, registry or disk trees are scanned.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import time

RUNTIME_FILE = '.nexus-python.json'
REQUIREMENTS = {'pywebview': 'pywebview>=5,<7', 'Jinja2': 'Jinja2>=3.1.6,<4',
                'regex': 'regex>=2024.11.6'}
# Deliberately conservative: prereleases/dev/vendor versions are not auto-reused.
PROBE = r'''
import importlib.metadata as m, json, re, sys
result = {'prefix': sys.prefix, 'base_prefix': sys.base_prefix, 'packages': {}}
bounds = {'pywebview': ((5,), (7,)), 'Jinja2': ((3,1,6), (4,)), 'regex': ((2024,11,6), None)}
for name, (lo, hi) in bounds.items():
    item = {'status': 'missing'}
    try:
        version = m.version(name)
        item['version'] = version
        if not re.fullmatch(r'\d+(?:\.\d+)*', version):
            raise ValueError('non-final or unrecognized version')
        parts = tuple(int(x) for x in version.split('.'))
        pad = lambda v: v + (0,) * (8-len(v))
        if pad(parts) < pad(lo) or hi and pad(parts) >= pad(hi):
            raise ValueError('outside supported version range')
        if name == 'pywebview':
            import webview
            assert callable(webview.create_window) and callable(webview.start)
        elif name == 'Jinja2':
            import jinja2
            assert jinja2.Template('{{ value }}').render(value='ok') == 'ok'
        else:
            import regex
            assert regex.fullmatch(r'\p{L}+', 'hello') is not None
        item['status'] = 'compatible'
    except m.PackageNotFoundError:
        pass
    except Exception as exc:
        item['status'] = 'incompatible'
        item['reason'] = str(exc)
    result['packages'][name] = item
result['installed'] = {d.metadata['Name']: d.version for d in m.distributions() if d.metadata['Name']}
print(json.dumps(result))
'''


def python_in(folder):
    return Path(folder) / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def probe(python):
    """Do not write bytecode, load user site packages, or inherit PYTHONPATH."""
    try:
        result = subprocess.run([str(python), '-I', '-B', '-c', PROBE],
                                capture_output=True, text=True, check=True, timeout=60)
        data = json.loads(result.stdout.strip().splitlines()[-1])
        if set(data['packages']) != set(REQUIREMENTS):
            raise ValueError('Incomplete dependency probe')
        return data
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, IndexError) as exc:
        raise RuntimeError('Cannot check Python runtime %s: %s' % (python, exc)) from exc


def recorded_python(target):
    """Only accept a runtime inside this app; config never executes arbitrary paths."""
    target = Path(target).resolve()
    try:
        record = json.loads((target / RUNTIME_FILE).read_text(encoding='utf-8'))
        candidate = Path(record['executable'])
        if record.get('schema') == 1 and candidate.is_absolute() and target in candidate.absolute().parents and candidate.is_file():
            # Resolve the directory, not POSIX venv Python symlinks to the base executable.
            if target in candidate.parent.resolve().parents:
                return candidate
    except (OSError, ValueError, KeyError, TypeError):
        pass
    candidate = python_in(target / '.venv')
    return candidate if candidate.is_file() else None


def _complete(report):
    return all(p['status'] == 'compatible' for p in report['packages'].values())


def _save(target, python):
    path = target / RUNTIME_FILE
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps({'schema': 1, 'executable': str(python)}), encoding='utf-8')
    os.replace(temp, path)


def dependency_plan(target):
    """Read-only preflight. Return the exact application-local change plan."""
    target = Path(target).resolve()
    existing = recorded_python(target)
    if existing:
        try:
            report = probe(existing)
            if all(p['status'] != 'incompatible' for p in report['packages'].values()) and Path(report['prefix']).resolve() == existing.parent.parent.resolve() and report['prefix'] != report['base_prefix']:
                return {'target': str(target), 'python': str(existing), 'reuse': True,
                        'requirements': [REQUIREMENTS[n] for n,p in report['packages'].items() if p['status'] != 'compatible'],
                        'reused': {n:p for n,p in report['packages'].items() if p['status']=='compatible'}, 'notes': []}
        except RuntimeError:
            pass
    base = Path(getattr(sys, '_base_executable', sys.executable))
    report = probe(base)
    if report['prefix'] != report['base_prefix']:
        raise RuntimeError('Run the installer with a regular Python installation, not another app runtime.')
    incompatible = [name for name, item in report['packages'].items() if item['status'] == 'incompatible']
    share = not incompatible
    env = target / '.venv'
    if env.exists():
        env = target / '.runtimes' / ('python-' + str(time.time_ns()))
    needed = [REQUIREMENTS[name] for name, item in report['packages'].items()
              if not share or item['status'] != 'compatible']
    return {'target': str(target), 'python': str(python_in(env)), 'env': str(env),
            'base': str(base), 'reuse': False, 'share': share, 'requirements': needed,
            'reused': {n: p for n, p in report['packages'].items() if share and p['status'] == 'compatible'},
            'notes': (['Existing incompatible packages left unchanged: ' + ', '.join(incompatible) +
                       '. All required packages will be installed in a separate isolated runtime.'] if incompatible else [])}


def setup_dependencies(target, emit=print, plan=None):
    """Execute the approved preflight, failing closed if its assumptions changed."""
    target = Path(target).resolve()
    plan = dependency_plan(target) if plan is None else plan
    if plan['target'] != str(target):
        raise RuntimeError('Dependency plan target changed; rerun preflight.')
    python = Path(plan['python'])
    if plan['reuse']:
        env = python.parent.parent
    else:
        env = Path(plan['env'])
        if env.exists():
            raise RuntimeError('Planned new runtime folder already exists; rerun preflight. Nothing overwritten.')
        env.parent.mkdir(parents=True, exist_ok=True)
    command = [plan.get('base', str(python)), '-I', '-m', 'venv']
    if plan.get('share'):
        command.append('--system-site-packages')
    command.append(str(env))
    try:
        if not plan['reuse']:
            subprocess.run(command, check=True, timeout=180)
        report = probe(python)
        if Path(report['prefix']).resolve() != env.resolve() or report['prefix'] == report['base_prefix']:
            raise RuntimeError('Refusing pip: Python is not the new app-owned virtual environment.')
        needed = [REQUIREMENTS[name] for name, item in report['packages'].items() if item['status'] != 'compatible']
        if needed != plan['requirements']:
            raise RuntimeError('Dependency requirements changed after preflight; rerun installer to review a new plan.')
        if needed:
            emit('Installing approved app-local requirements from official PyPI: ' + ', '.join(needed))
            # Pin every installed distribution so pip cannot replace or upgrade it.
            # A conflict fails this step instead of changing existing versions.
            import re
            pins = []
            for name, version in report.get('installed', {}).items():
                if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', name) or not re.fullmatch(r'[A-Za-z0-9.!+_-]+', version):
                    raise RuntimeError('Cannot safely pin existing package metadata; no packages changed.')
                pins.append(name + '==' + version)
            constraints = env / '.nexus-existing-constraints.txt'
            constraints.write_text('\n'.join(sorted(pins)) + '\n', encoding='utf-8')
            subprocess.run([str(python), '-I', '-m', 'pip', '--isolated', 'install',
                            '--index-url', 'https://pypi.org/simple', '--only-binary=:all:',
                            # pywebview requires this small pure-Python, sdist-only
                            # package. Keep compiled dependencies wheel-only.
                            '--no-binary=proxy-tools',
                            '--disable-pip-version-check', '--no-input', '--constraint', str(constraints), *needed],
                           check=True, timeout=600)
        if not _complete(probe(python)):
            raise RuntimeError('Installed dependencies failed version/import checks.')
        _save(target, python)
        emit('Runtime verified. Existing packages, compilers and drivers were not changed.')
        return python
    except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
        raise RuntimeError('Desktop dependency setup did not complete; no existing package versions were intentionally replaced. App data and previous runtime selection are unchanged. '
                           'Check network/PyPI access and supported Python, then rerun the installer. '
                           'Browser mode remains available. Detail: ' + str(exc)) from exc
