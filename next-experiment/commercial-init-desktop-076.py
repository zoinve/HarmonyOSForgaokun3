"""Original init owns a distinctly named, minimally permitted diagnostic service."""
from pathlib import Path
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
SCRIPT = (b / 'commercial-direct-desktop-075.sh').read_text()
SCRIPT = SCRIPT.replace('COMMERCIAL075', 'COMMERCIAL076')
# The prior snapshot exporter deliberately retains its stable evidence filename.
CONFIG = dict(services=[dict(name='matebook_desktop076',
    path=['/system/bin/sh', '-c', SCRIPT], uid='root', gid=['root', 'system', 'shell'],
    permission=['ohos.permission.START_ABILITIES_FROM_BACKGROUND',
                'ohos.permission.GET_BUNDLE_INFO_PRIVILEGED',
                'ohos.permission.KILL_APP_PROCESSES',
                'ohos.permission.CLEAN_BACKGROUND_PROCESSES', 'ohos.permission.DUMP'],
    secon='u:r:sh:s0', sandbox=0, once=1, **{'start-mode': 'boot'})])


def update_config(body):
    original = json.loads(body)
    assert 'matebook_desktop076' not in {item['name'] for item in original['services']}
    result = dict(original, services=original['services'] + CONFIG['services'])
    assert result['services'][:-1] == original['services']
    assert {k:v for k,v in result.items() if k != 'services'} == {k:v for k,v in original.items() if k != 'services'}
    return (json.dumps(result, indent=2) + '\n').encode()
