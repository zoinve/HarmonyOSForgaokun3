"""Retain audited workflow guards; use the existing Windows SSH key per command."""
from pathlib import Path
import runpy
import subprocess


def source043(name):
    text = runpy.run_path(str(Path(__file__).with_name(name + '-042.py')))['source']
    for old, new in [('commercial61-native-042', 'commercial61-native-043'),
                     ('commercial-return-audit-042', 'commercial-return-audit-043'),
                     ('COMMERCIAL042', 'COMMERCIAL043'),
                     ('ordered_chain_equals_full_042', 'ordered_chain_equals_full_043'),
                     ('libcommercial_rs_observer042.so', 'libcommercial_rs_observer043.so'),
                     ('Original transaction mode and state 042', 'Actual original Binder delivery 043')]:
        text = text.replace(old, new)
    return text


def configure_local_transport():
    if getattr(subprocess.run, '_commercial043', False):
        return
    original = subprocess.run

    def run(args, *a, **kwargs):
        if isinstance(args, list) and args:
            if args[0] == 'ssh':
                args = ['/mnt/c/Windows/System32/OpenSSH/ssh.exe', '-i',
                        'C:/Users/39255/.ssh/id_ed25519_opencode_matebook'] + args[1:]
            elif args[:4] == ['wsl', '-d', 'Debian', '--']:
                assert args[4] == 'cat', 'Only existing local artifact reads are remapped'
                args = args[4:]
        return original(args, *a, **kwargs)

    run._commercial043 = True
    subprocess.run = run
