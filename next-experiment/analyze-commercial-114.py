"""Apply existing immutable evidence readers to OOBE comparison 114."""
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
SCRIPTS = {
    'server': 'analyze-server-event-108.py',
    'reference': 'analyze-commercial-reference-108.py',
    'memory': 'analyze-original-memmgr-108.py',
    'review': 'review-commercial-return-108.py',
    'input': 'analyze-commercial-input-response-108.py',
    'frame': 'analyze-commercial-observation-108.py',
    'second-frame': 'analyze-commercial-observation-108.py',
    'secrecy': 'analyze-commercial-observation-108.py',
}


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in SCRIPTS
    kind = sys.argv[1]
    source = (BASE / SCRIPTS[kind]).read_text().replace('commercial61-native-108', 'commercial61-native-114')
    source = source.replace('commercial-workflow-108.py', 'commercial-workflow-114.py')
    if kind == 'input':
        source = source.replace("'108'", "'114'")
    sys.argv = [__file__] + ([kind] if kind in ('frame', 'second-frame', 'secrecy') else [])
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
