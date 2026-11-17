"""Make hardware-file parents explicit: Linux initramfs does not mkdir -p."""
from pathlib import PurePosixPath
import stat
def complete(entries):
    result=dict(entries)
    for name in entries:
        if not name.startswith('native-target/graphics016/'):
            continue
        for parent in reversed(PurePosixPath(name).parents):
            key=str(parent)
            if key=='.':continue
            if key in result:
                assert stat.S_ISDIR(result[key][0]), ('non-directory hardware parent',key)
            else:
                result[key]=(stat.S_IFDIR|0o755,b'')
    return result
