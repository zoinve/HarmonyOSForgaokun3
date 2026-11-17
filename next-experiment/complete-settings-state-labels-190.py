'''Resolve missing candidate labels through the original file-context policy.'''
import csv
import ctypes
import ctypes.util
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')


class Option(ctypes.Structure):
    _fields_ = [('type', ctypes.c_int), ('value', ctypes.c_char_p)]


class FilePolicy:
    def __init__(self, path):
        self.lib = ctypes.CDLL(ctypes.util.find_library('selinux'), use_errno=True)
        self.lib.selabel_open.argtypes = [ctypes.c_uint, ctypes.POINTER(Option), ctypes.c_uint]
        self.lib.selabel_open.restype = ctypes.c_void_p
        self.lib.selabel_lookup_raw.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p),
                                               ctypes.c_char_p, ctypes.c_int]
        self.lib.selabel_lookup_raw.restype = ctypes.c_int
        self.lib.selabel_close.argtypes = [ctypes.c_void_p]
        self.lib.freecon.argtypes = [ctypes.c_char_p]
        option = Option(3, str(path).encode())
        self.handle = self.lib.selabel_open(0, ctypes.byref(option), 1)
        if not self.handle:
            raise OSError(ctypes.get_errno(), 'original file-context policy open failed')

    def lookup(self, path, mode):
        assert path.startswith('/data/') and '..' not in Path(path).parts
        context = ctypes.c_char_p()
        code = self.lib.selabel_lookup_raw(self.handle, ctypes.byref(context), path.encode(), mode)
        if code:
            raise OSError(ctypes.get_errno(), 'original file-context lookup failed')
        try:
            return context.value.decode()
        finally:
            self.lib.freecon(context)

    def close(self):
        if self.handle:
            self.lib.selabel_close(self.handle)
            self.handle = None


if __name__ == '__main__':
    work = BUILD / 'settings-state-labels-190'
    report = ROOT / 'reports/settings-state-labels-190'
    assert not work.exists() and not report.exists(), 'preserve numbered outputs'
    source_data = (ROOT / 'reports/settings-preinstall-state-189/result.json').read_bytes()
    source = json.loads(source_data)
    labels = Path(source['archive']).with_name('preinstall-labels.tsv')
    label_data = labels.read_bytes()
    assert hashlib.sha256(label_data).hexdigest() == source['labels_sha256']
    reader = runpy.run_path(str(Path(__file__).with_name('audit-board-driver-contracts-126.py')))
    policy_path = '/system/etc/selinux/targeted/contexts/file_contexts'
    policy_data = reader['read'](reader['IMAGES'] / 'p111-system.kr990-ext4-v1.img', 'cat ' + policy_path)
    work.mkdir(mode=0o700)
    policy_file = work / 'original-file-contexts'
    with policy_file.open('xb') as stream:
        stream.write(policy_data)
    original = list(csv.DictReader(label_data.decode().splitlines(), delimiter='\t'))
    mapping = {row['path']: row['selinux'] for row in original}
    assert len(mapping) == len(original), 'duplicate source labels require explicit resolution'
    additions = []
    policy = FilePolicy(policy_file)
    try:
        for row in source['members']:
            if row['path'] not in mapping:
                context = policy.lookup('/data/' + row['path'], row['kind'] | row['mode'])
                additions.append(dict(path=row['path'], selinux=context,
                                      origin='original system file_contexts lookup'))
                mapping[row['path']] = context
    finally:
        policy.close()
    assert set(mapping) == {row['path'] for row in source['members']}
    output = work / 'complete-preinstall-labels.tsv'
    with output.open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['path', 'selinux'], delimiter='\t')
        writer.writeheader()
        writer.writerows(dict(path=path, selinux=context) for path, context in sorted(mapping.items()))
    result = dict(input_report_sha256=hashlib.sha256(source_data).hexdigest(),
                  input_labels_sha256=hashlib.sha256(label_data).hexdigest(),
                  original_policy_path=policy_path, original_policy_sha256=hashlib.sha256(policy_data).hexdigest(),
                  original_source_label_count=len(original), additions=additions,
                  completed_label_count=len(mapping), complete_labels_path=str(output),
                  complete_labels_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  existing_source_labels_unchanged=True, all_candidate_members_have_labels=True,
                  target_modified=False, host_security_configuration_changed=False,
                  original_policy_changed=False, candidate_data_filesystem_prepared=False)
    report.mkdir()
    with (report / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({key: value for key, value in result.items() if key != 'additions'}, indent=2))
