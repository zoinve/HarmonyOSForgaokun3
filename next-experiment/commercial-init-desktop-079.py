"""Read-only target network observation; no OOBE dismissal or completion."""
from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-init-desktop-078.py'))
SCRIPT = '''#!/system/bin/sh
printf 'COMMERCIAL079_NETWORK_OBSERVE no_guide_stop=1 no_completion_event=1\\n'
/system/bin/cat /proc/net/dev
/system/bin/cat /proc/net/route
exit 0
'''
CONFIG = dict(services=[dict(previous['CONFIG']['services'][0], name='matebook_desktop079')])


def update_config(body):
    original = json.loads(body)
    assert not any(s['name'].startswith('matebook_desktop') for s in original['services'])
    return (json.dumps(dict(original, services=original['services'] + CONFIG['services']), indent=2) + '\n').encode()
