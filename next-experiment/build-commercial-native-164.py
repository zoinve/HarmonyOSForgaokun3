"""Use proven same-inode current-namespace reopening; keep all original native services."""
from pathlib import Path
import inspect
import json
import runpy

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent


def loader164(digest,source='/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-helper-164/live-debug164',destination='/run/live-debug164'):
    loader=runpy.run_path(str(BASE/'build-commercial-native-161.py'))['loader161']
    return loader(digest,source,destination).replace('LIVE161_LOADER','LIVE164_LOADER')


def helper_source164():
    source=runpy.run_path(str(BASE/'build-commercial-native-161.py'))['helper_source161']()
    source=source.replace('LIVE161','LIVE164')
    anchor='#include "live-debug-storage-161.h"'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+'\n#include "live-debug-log-163.h"',1)
    old='    if (live_storage161_bind(196,ROOT159 "/logs/hilog",1) || live_storage161_bind(197,ROOT159 "/logs/native",2) || live_storage161_key(KEY159,ROOT159 "/etc/diag/host_ed25519")) return 93;'
    new='''    int hilog = live_log163_reopen(196,1);
    if (hilog < 0) return 93;
    int native = live_log163_reopen(197,2);
    if (native < 0) { close(hilog); return 93; }
    int failed = live_storage161_bind(hilog,ROOT159 "/logs/hilog",1) ||
        live_storage161_bind(native,ROOT159 "/logs/native",2) ||
        live_storage161_key(KEY159,ROOT159 "/etc/diag/host_ed25519");
    close(hilog);
    close(native);
    if (failed) return 93;'''
    assert source.count(old)==1
    return source.replace(old,new,1)


if __name__=='__main__':
    fixture=json.loads((ROOT/'reports/live-debug-log-fixture-163-compile-fix-1/result.json').read_text())
    assert fixture['inherited_fd_failure_reproduced_and_reopen_fix_verified']
    import hashlib
    assert hashlib.sha256((BASE/'live-debug-log-163.h').read_bytes()).hexdigest()==fixture['log_header_sha256']
    source=(BASE/'build-commercial-native-161.py').read_text()
    source=source.replace('helper_source161','helper_source164').replace('loader161','loader164')
    source=source.replace('commercial61-native-161','commercial61-native-164')
    source=source.replace('live-debug-helper-161','live-debug-helper-164').replace('live-debug161','live-debug164')
    source=source.replace('live-debug-launcher-161','live-debug-launcher-164')
    source=source.replace("metadata['live161']","metadata['live164']").replace('ordered_chain_equals_full_161','ordered_chain_equals_full_164')
    source=source.replace('LIVE161_LOADER','LIVE164_LOADER')
    start=source.index('def helper_source164(')
    end=source.index('def loader164(',start)
    source=source[:start]+inspect.getsource(helper_source164)+'\n\n'+source[end:]
    exec(compile(source,'build-commercial-native-164.generated.py','exec'),{'__name__':'__main__','__file__':str(BASE/'build-commercial-native-164.generated.py')})
