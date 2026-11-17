"""Add a second real full-frame capture without changing composition."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
payload = runpy.run_path(str(b / 'build-commercial-composer-068.py'))['payload']
payload = payload.replace("work=root/'commercial-composer-068'", "work=root/'commercial-composer-075'").replace(
    "local=base/'reports/commercial-composer-068'", "local=base/'reports/commercial-composer-075'")
payload = payload.replace("old=root/'commercial-composer-030/composer-evidence-030.cpp'",
                          "old=root/'commercial-composer-068/composer-evidence-068.cpp'")
payload = payload.replace('commercial-full-frame-068.py', 'commercial-desktop-evidence-075.py')
payload = payload.replace('composer-evidence-068.cpp\';new_source', 'composer-evidence-075.cpp\';new_source')
payload = payload.replace("new_source=work/'composer-evidence-068.cpp'", "new_source=work/'composer-evidence-075.cpp'")
payload = payload.replace("['composer-evidence-068.cpp','link.stdout'", "['composer-evidence-075.cpp','link.stdout'")
payload = payload.replace('full_capture_limit=1,full_capture_interval_seconds=[120,145]',
                          'full_capture_limit=2,full_capture_interval_seconds=[[120,145],[140,145]]')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
