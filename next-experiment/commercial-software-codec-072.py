"""Admission and RAM-only integration of the tested original bridge backend."""
from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import re
import stat
import tarfile

BASE = Path(__file__).resolve().parents[1]
PREFIX = 'native-target/software-codec072/'
RUNTIME = '/system/lib64/commercial-software-codec072'


def files():
    report = BASE / 'reports/commercial-software-codec-bundle-072'
    record = json.loads((report / 'result.json').read_text())
    tests = [json.loads((BASE / name / 'result.json').read_text()) for name in [
        'reports/commercial-software-codec-helper-test-072',
        'reports/commercial-software-codec-helper-test-072-isolated-r2']]
    assert all(t['all_1980_frames_match'] and t['exact_peer_uid_rejection'] for t in tests)
    assert tests[0]['asan_ubsan_no_report'] and tests[1]['isolated_runtime_decode_verified']
    source = (BASE / 'next-experiment/commercial-software-codec-helper-072.c').read_bytes()
    assert all(t['source_sha256'] == hashlib.sha256(source).hexdigest() for t in tests)
    blob = (report / 'software-codec-runtime-072.tar.gz').read_bytes()
    assert len(blob) == record['archive_bytes']
    assert hashlib.sha256(blob).hexdigest() == record['archive_sha256']
    expected = {r['name']: r for r in record['runtime_files']}
    assert len(expected) == len(record['runtime_files'])
    assert sum(r['bytes'] for r in expected.values()) <= 512 * 1024 * 1024
    result = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as archive:
        for item in archive:
            name = item.name
            assert re.fullmatch(r'[A-Za-z0-9_.+-]+', name) and name not in ('.', '..')
            assert item.isfile() and name not in result and name in expected
            assert item.size == expected[name]['bytes']
            data = archive.extractfile(item).read()
            assert hashlib.sha256(data).hexdigest() == expected[name]['sha256']
            result[name] = data
    assert result.keys() == expected.keys()
    assert all(hashlib.sha256(result['helper']).hexdigest() == t['helper_sha256'] for t in tests)
    return result


def launcher(mode):
    assert mode in ('ring', 'legacy')
    suffix = 'h264x' if mode == 'ring' else 'video'
    sock = '/data/local/tmp/l410-kylin-' + suffix + '-decoder.sock'
    log = '/data/local/tmp/l410-kylin-' + ('h264' if mode == 'ring' else 'video') + '-decoder.log'
    return ('#!/system/bin/sh\nset -eu\nR=' + RUNTIME + '\nS=' + sock + '\n'
        'if [ -e "$S" ] || [ -L "$S" ]; then\n'
        '  [ -S "$S" ] && [ ! -L "$S" ] || exit 70\n'
        '  rm -f "$S"\nfi\n'
        'unset LD_PRELOAD LD_LIBRARY_PATH\n'
        'exec "$R/ld-linux-aarch64.so.1" --inhibit-cache --library-path "$R" '
        '"$R/helper" "$S" ' + mode + ' 1013 >>' + log + ' 2>&1\n').encode()


def additions():
    result = {'runtime/' + n: d for n, d in files().items()}
    result['l410-launch-kylin-h264-decoder.sh'] = launcher('ring')
    result['l410-launch-kylin-video-decoder.sh'] = launcher('legacy')
    return result


def add_entries(entries):
    entries = dict(entries)
    added = {}
    for name, data in sorted(additions().items()):
        full = PREFIX + name
        for parent in reversed(PurePosixPath(full).parents):
            if str(parent) == '.':
                continue
            if str(parent) not in entries:
                entries[str(parent)] = (stat.S_IFDIR | 0o755, b'')
                added[str(parent)] = entries[str(parent)]
            assert stat.S_ISDIR(entries[str(parent)][0])
        assert full not in entries
        entries[full] = (stat.S_IFREG | 0o555, data)
        added[full] = entries[full]
    return entries, added


def instrument(source):
    anchor = '    directory("/run/commercial-system005/upper/lib64",0755);'
    assert source.count(anchor) == 1
    upper = '/run/commercial-system005/upper'
    lines = [anchor, '    directory("' + upper + '/lib64/commercial-software-codec072",0755);']
    for name in sorted(files()):
        lines.append('    commercial_copy005("/software-codec072/runtime/' + name + '","' +
            upper + '/lib64/commercial-software-codec072/' + name + '",0555);')
    lines.append('    directory("' + upper + '/bin",0755);')
    for name in ('l410-launch-kylin-h264-decoder.sh', 'l410-launch-kylin-video-decoder.sh'):
        lines.append('    commercial_copy005("/software-codec072/' + name + '","' + upper + '/bin/' + name + '",0555);')
    lines.append('    dprintf(1,"COMMERCIAL072_SOFTWARE_CODEC_RAM_READY original_init_services=1 peer_uid=1013 stock_adapters_unchanged=1 runtime_decode_not_yet_verified=1\\n");')
    source = source.replace(anchor, '\n'.join(lines), 1)
    anchor = ' char root069[64];snprintf(root069,sizeof(root069),"/proc/%ld/root",pid);'
    assert source.count(anchor) == 1
    extra = r'''
 if(sample==10 || sample==18 || sample==28){
  char codec072[256];
  const char *logs072[]={"/data/local/tmp/l410-kylin-h264-decoder.log","/data/local/tmp/l410-kylin-video-decoder.log"};
  for(unsigned i072=0;i072<2;++i072){
   snprintf(codec072,sizeof(codec072),"%s%s",root069,logs072[i072]);
   commercial_stream043(codec072,sample,(unsigned)pid,32768);
  }
 }
'''
    return source.replace(anchor, anchor + '\n' + extra, 1)
