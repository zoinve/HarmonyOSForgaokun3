"""Correct target-root verification; keep 157 and its negative evidence intact."""
from pathlib import Path
import inspect

BASE = Path(__file__).resolve().parent


def adapt(source, archive_hash):
    assert source.count('#include "native-live-debug-157.h"') == 1
    assert archive_hash in source
    return source.replace('LIVE157','LIVE158').replace('native_live157','native_live158').replace('native-live-debug-157.h','native-live-debug-158.h')


def helper_source158():
    source = (BASE / 'live-debug-launcher-157.c').read_text().replace('157','158')
    source = source.replace('#define _GNU_SOURCE\n','#define _GNU_SOURCE\n#include "live-debug-root-158.h"\n',1)
    old = '''    snprintf(path,sizeof(path),"/proc/%ld/root/system/bin/init",target);
    if (stat(path,&source) || !S_ISREG(source.st_mode)) return 79;'''
    new = '''    snprintf(path,sizeof(path),"/proc/%ld/root",target);
    int target_root = open(path,O_PATH | O_DIRECTORY | O_CLOEXEC);
    int original_init = target_root < 0 ? -1 : live_root158_open(target_root,"system/bin/init");
    int root_error = original_init < 0 ? errno : 0;
    int root_valid = original_init >= 0 && !fstat(original_init,&source) && S_ISREG(source.st_mode);
    if (original_init >= 0) close(original_init);
    if (target_root >= 0) close(target_root);
    if (!root_valid) {
        dprintf(1,"LIVE158_ROOT_REFUSED errno=%d target_root_resolution=1\\n",root_error);
        return 79;
    }
    dprintf(1,"LIVE158_ROOT_VERIFIED in_root_resolution=1 original_inode_only=1\\n");'''
    assert source.count(old) == 1
    return source.replace(old,new,1)


if __name__ == '__main__':
    source = (BASE / 'build-commercial-native-157.py').read_text().replace('157','158')
    source = source.replace('commercial61-native-153','commercial61-native-157')
    source = source.replace('reports/live-debug-inputs-158','reports/live-debug-inputs-157')
    start = source.index('def adapt(')
    end = source.index("\n\nif __name__ == '__main__':",start)
    source = source[:start] + inspect.getsource(adapt) + '\n\n' + inspect.getsource(helper_source158) + source[end:]
    anchor = '    work.mkdir();report.mkdir()'
    assert source.count(anchor) == 1
    addition = '''
    helper_source = helper_source158()
    (work / 'live-debug-launcher-158.c').open('x').write(helper_source)
    header_source = (BASE / 'native-live-debug-157.h').read_text().replace('157','158').replace('live-debug-inputs-158','live-debug-inputs-157')
    (work / 'native-live-debug-158.h').open('x').write(header_source)
'''
    source = source.replace(anchor,anchor + '\n' + addition,1)
    source = source.replace("BASE / 'live-debug-launcher-158.c'","work / 'live-debug-launcher-158.c'")
    source = source.replace("BASE / 'native-live-debug-158.h'","work / 'native-live-debug-158.h'")
    anchor = "'-Werror',str(work / 'live-debug-launcher-158.c')"
    assert source.count(anchor) == 1
    source = source.replace(anchor,"'-Werror','-I',str(BASE),str(work / 'live-debug-launcher-158.c')",1)
    # Keep the common builder's explicit compile and full-chain invariants.
    namespace = {'__name__':'__main__','__file__':str(BASE / 'build-commercial-native-158.generated.py'),'inspect':inspect}
    exec(compile(source,'build-commercial-native-158.generated.py','exec'),namespace)
