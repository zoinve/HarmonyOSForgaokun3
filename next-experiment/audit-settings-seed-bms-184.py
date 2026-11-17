'''Inspect only original BMS JSON records; never restore or synthesize state.'''
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = runpy.run_path(str(Path(__file__).with_name('audit-settings-seed-183.py')))
BUNDLE = 'com.huawei.hmos.settings'


def bms_path(name):
    return re.search(r'/(?:bms|bundle_manager_service|bundlemgr)/', name) is not None


def summarize_json(data):
    value = json.loads(data)
    matches = []

    def visit(node, matched_key=False):
        if isinstance(node, dict):
            if matched_key or node.get('bundleName') == BUNDLE:
                public_fields = ['bundleName', 'versionName', 'versionCode', 'codePath',
                                 'baseCodePath', 'hapPath', 'appType']
                matches.append(dict(keys=sorted(node), fields={
                    key: node[key] for key in public_fields
                    if key in node and isinstance(node[key], (str, int, bool))}))
            for key, child in node.items():
                visit(child, key == BUNDLE or key.startswith(BUNDLE + '_'))
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                settings_records=matches, raw_content_exported=False)


if __name__ == '__main__':
    folder = ROOT / 'reports/settings-seed-bms-184'
    assert not folder.exists(), 'immutable result already exists'
    entries = []
    hap_entries = []

    def observe(name, size, kind):
        if bms_path(name):
            entries.append(dict(path=name, bytes=size, file_type=oct(kind)))
        if PurePosixPath(name).suffix.lower() == '.hap' and kind == 0o100000:
            hap_entries.append(dict(path=name, bytes=size))

    result = ARCHIVE['scan_archive'](
        select=lambda name: bms_path(name) and name.endswith('.json'),
        inspect=summarize_json, observe=observe)
    result.update(bms_entries=entries, all_regular_hap_entries=hap_entries,
                  content_read_scope='Regular JSON files within original BMS directories only',
                  installed_state_restored=False, credentials_exported=False,
                  settings_repair_verified=False)
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
