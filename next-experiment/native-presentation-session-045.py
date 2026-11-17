"""Explicit user-approved connection/timer policy; no operational side effects."""
import ast
import re

SSH_BASE = ['ssh', '-o', 'HostName=10.126.126.14', '-o', 'HostKeyAlias=192.168.10.128',
            '-o', 'StrictHostKeyChecking=yes', '-o', 'BatchMode=yes']


def connection_source(text):
    assert 'SSH_BASE =' not in text
    lines = text.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))
    changes = []
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.List) and node.elts and isinstance(node.elts[0], ast.Constant) and node.elts[0].value == 'ssh':
            first = node.elts[0]
            begin = starts[first.lineno - 1] + len(lines[first.lineno - 1].encode()[:first.col_offset].decode())
            end = starts[first.end_lineno - 1] + len(lines[first.end_lineno - 1].encode()[:first.end_col_offset].decode())
            changes.append((begin, end))
    assert changes, 'no client SSH command found'
    for begin, end in sorted(changes, reverse=True):
        text = text[:begin] + '*SSH_BASE' + text[end:]
    prefix = ("from pathlib import Path\nimport runpy\n"
              "_SESSION = runpy.run_path(str(Path(__file__).with_name('native-presentation-session-045.py')))\n"
              'SSH_BASE = ' + repr(SSH_BASE) + '\n')
    compile(prefix + text, 'session045-connection', 'exec')
    return prefix + text


def timer_guard(text):
    pattern = r"assert cmd\(\['systemctl','is-(active|enabled)','harmony-lab-screen-off-001.timer'\]\)\.strip\(\)==\s*'(active|enabled)'"
    def replace(m):
        assert m[1] == m[2]
        return ("assert guard_user_timer_045('is-active','inactive',3)" if m[1] == 'active'
                else "assert guard_user_timer_045('is-enabled','disabled',1)")
    text, count = re.subn(pattern, replace, text)
    assert count, 'no original timer guard found'
    text = text.replace('screenoff_timer_active_enabled=True',
                        'screenoff_timer_active_enabled=False,screenoff_timer_inactive_disabled_preserved=True')
    helper = '''def guard_user_timer_045(operation, expected, code):
 import subprocess
 r=subprocess.run(['systemctl',operation,'harmony-lab-screen-off-001.timer'],text=True,capture_output=True,timeout=20)
 assert r.returncode==code and r.stdout.strip()==expected,(r.returncode,r.stdout,r.stderr)
 return True
'''
    return helper + text
