"""Prepare the traced USB candidate with early disk and command-line admission."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-176'
WORKFLOW_REPORT = REPORT / 'workflow-admission-r1'
PREVIOUS = runpy.run_path(str(BASE / 'commercial-workflow-175.py'))
configure_local_transport = PREVIOUS['configure_local_transport']
OPERATIONS = PREVIOUS['OPERATIONS']

USB_PREFLIGHT = '''
def usb176_preflight():
 import json,subprocess
 from pathlib import Path
 candidates=[]
 for path in Path('/sys/class/block').iterdir():
  if (path/'partition').exists():continue
  parents=[path.resolve(),*path.resolve().parents]
  usb=next((p for p in parents if (p/'subsystem').resolve()==Path('/sys/bus/usb') and (p/'idVendor').is_file()),None)
  if usb is None:continue
  if (usb/'idVendor').read_text().strip()!='346d' or (usb/'idProduct').read_text().strip()!='5678':continue
  if (path/'removable').read_text().strip()!='1' or (path/'size').read_text().strip()!='61849600':continue
  candidates.append(path.name)
 assert len(candidates)==1,'expected unique USB disk absent or ambiguous; no target changes permitted'
 tree=json.loads(subprocess.check_output(['lsblk','--json','--bytes','-o','NAME,TYPE,SIZE,TRAN,MOUNTPOINTS'],text=True))
 disks=[p for p in tree['blockdevices'] if p.get('tran')=='usb']
 assert len(disks)==1 and disks[0]['name']==candidates[0] and disks[0]['size']==31666995200,'unexpected USB block topology'
 def mounted(node):
  return any(node.get('mountpoints') or []) or any(mounted(p) for p in node.get('children',[]))
 assert not mounted(disks[0]),'USB volumes mounted; do not force unmount or boot'
usb176_preflight()
'''


def source176(operation):
    source = PREVIOUS['source175'](operation)
    source = source.replace('commercial61-native-175-compile-fix-1', 'commercial61-native-176')
    source = source.replace('commercial61-native-175', 'commercial61-native-176')
    source = source.replace('commercial-return-audit-175', 'commercial-return-audit-176')
    source = source.replace('ordered_chain_equals_full_175', 'ordered_chain_equals_full_176')
    source = source.replace('estimated175', 'estimated176')
    source = source.replace('native protected USB storage visibility diagnostic 175',
                            'native traced protected USB storage diagnostic 176')
    if operation == 'install-commercial-native':
        split = "code='payload='"
        assert source.count(split) == 1
        local, remote = source.split(split, 1)
        # Preserve the admitted full-chain identity locally; only the ESP alias differs.
        remote = remote.replace("'commercial61-native-176/initrd.img'", "'usb176.img'")
        remote = remote.replace("'initrd /commercial61-native-176/initrd.img'", "'initrd /usb176.img'")
        old = "dest=esp/'commercial61-native-176';entry="
        assert remote.count(old) == 1
        remote = remote.replace(old, 'dest=esp;entry=', 1)
        old = 'assert not dest.exists() and not entry.exists()'
        assert remote.count(old) == 1
        remote = remote.replace(old, "assert not (dest/'usb176.img').exists() and not entry.exists()", 1)
        assert remote.count('dest.mkdir()\n') == 1
        remote = remote.replace('dest.mkdir()\n', '', 1)
        remote = remote.replace("dest/'initrd.img'", "dest/'usb176.img'")
        start = remote.index("old=(esp/'loader/entries/harmonyos-gpu-manual.conf').read_text()")
        end_anchor = 'assert estimated176<1800,estimated176\n'
        end = remote.index(end_anchor, start) + len(end_anchor)
        options_preflight = remote[start:end]
        remote = remote[:start] + remote[end:]
        anchor = 'assert not root.exists();root.mkdir()'
        assert remote.count(anchor) == 1
        remote = remote.replace(anchor, USB_PREFLIGHT + options_preflight + anchor, 1)
        source = local + split + remote
    elif operation == 'run-commercial-native':
        anchor = 'input=startcode,text=True'
        assert source.count(anchor) == 1
        overlay = json.loads((REPORT / 'overlay-result.json').read_text())
        check = ("from pathlib import Path\nimport hashlib\n"
                 "assert hashlib.sha256(Path('/boot/efi/usb176.img').read_bytes()).hexdigest()=="
                 + repr(overlay['sha256']) + "\n")
        source = source.replace(anchor, 'input=' + repr(USB_PREFLIGHT + check) + '+startcode,text=True', 1)
    elif operation == 'retrieve-commercial-evidence':
        early = json.loads((ROOT / 'reports/commercial61-native-175-compile-fix-1/early-return-inspection.json').read_text())
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        assert early['run'] not in source
        source = source.replace(anchor, anchor + repr(early['run']) + ', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in [*OPERATIONS, 'retain-entries']
    admission = json.loads((WORKFLOW_REPORT / 'workflow-test.json').read_text())
    assert all(admission.values())
    configure_local_transport()
    if sys.argv[1] == 'retain-entries':
        runpy.run_path(str(BASE / 'retain-latest-experiment-boot-entries-001.py'), run_name='__main__')
    else:
        operation = sys.argv[1]
        source = source176(operation)
        assert source == (WORKFLOW_REPORT / (operation + '.generated.py')).read_text()
        exec(compile(source, operation, 'exec'),
             {'__name__': '__main__', '__file__': str(BASE / (operation + '-176.py'))})
