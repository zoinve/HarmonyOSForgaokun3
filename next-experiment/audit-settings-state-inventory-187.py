'''Inventory supplied Settings install and access-token state without contents.'''
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
API = runpy.run_path(str(Path(__file__).with_name('audit-settings-seed-183.py')))
PREFIXES = {
    'settings_public_code': './.hmos-data/app/el1/bundle/public/com.huawei.hmos.settings',
    'settings_system_code': './.hmos-data/app/el1/bundle/public/+com.huawei.hmos.settings',
    'access_token_el0': './.hmos-data/service/el0/access_token',
    'access_token_el1': './.hmos-data/service/el1/public/access_token',
    'access_token_rdb': './.hmos-data/service/el1/public/database/access_token',
}


def category(name):
    return next((key for key, prefix in PREFIXES.items()
                 if name.rstrip('/') == prefix or name.startswith(prefix + '/')), None)


if __name__ == '__main__':
    folder = ROOT / 'reports/settings-state-inventory-187'
    assert not folder.exists(), 'immutable result already exists'
    rows = []

    def observe(name, size, kind):
        group = category(name)
        if group:
            rows.append(dict(path=name, bytes=size, file_type=oct(kind), category=group))

    result = API['scan_archive'](select=lambda name: False, observe=observe)
    result.pop('selected_files')
    result.update(entries=rows, content_read_scope='No archive file contents',
                  source_state_applied=False, credentials_exported=False,
                  category_counts={key: sum(row['category'] == key for row in rows) for key in PREFIXES})
    folder.mkdir()
    with (folder / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
