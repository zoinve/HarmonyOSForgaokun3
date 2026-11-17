"""Keep init argv bounded; execute the diagnostic from a separate script file."""
from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-init-desktop-076.py'))
SCRIPT = previous['SCRIPT'].replace('COMMERCIAL076', 'COMMERCIAL077')
service = dict(previous['CONFIG']['services'][0], name='matebook_desktop077',
               path=['/system/bin/sh', '/commercial-desktop077.sh'])
CONFIG = dict(services=[service])


def update_config(body):
    original = json.loads(body)
    assert not any(s['name'].startswith('matebook_desktop') for s in original['services'])
    result = dict(original, services=original['services'] + CONFIG['services'])
    return (json.dumps(result, indent=2) + '\n').encode()
