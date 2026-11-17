"""Transform only the 168 outer lifecycle; keep original services unchanged."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
PREVIOUS = runpy.run_path(str(BASE / 'build-commercial-native-168.py'))

def outer172(source, digest, filesystem_uuid):
    source = PREVIOUS['outer168'](source, digest, filesystem_uuid)
    replacements = [
        ('#include "persistent-data-166.h"', '#include "persistent-data-172.h"'),
        ('            native_live159_stop();',
         '            native_live159_stop();\n            persistent172_pin(child);'),
        ('            snapshot();\n        }\n\n    }else dprintf(1,"NATIVE_ORIGINAL_REFUSED loop_setup',
         '            persistent172_reaped(child,got);\n            snapshot();\n        }\n\n    }else dprintf(1,"NATIVE_ORIGINAL_REFUSED loop_setup'),
        ('    persistent166_finish();', '    persistent172_finish();'),
    ]
    for old, new in replacements:
        assert source.count(old) == 1, old
        source = source.replace(old, new, 1)
    return source
