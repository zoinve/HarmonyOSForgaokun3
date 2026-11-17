from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
ORIGINAL = runpy.run_path(str(BASE / 'build-radio-native-261.py'))

def runtime285(source):
    source = ORIGINAL['runtime'](source)
    anchor = '    dprintf(1,' + chr(34) + 'RADIO261_ORIGINAL_HDF'
    extra = '''    int trace = open('/radio261/vendor.trace', O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW, 0600);
    if (trace < 0 || fchown(trace, 3021, 3021) || close(trace))
        fail('QCA285 private trace creation');
'''.replace(chr(39), chr(34))
    assert source.count(anchor) == 1
    return source.replace(anchor, extra + anchor, 1)

def trace_outer285(source):
    old = '900, 180, requested'
    assert source.count(old) == 1
    source = source.replace(old, '360, 120, requested', 1)
    anchor = '    if (radio261_broker > 0) {'
    extra = '''    int trace285 = open('/native-target/radio261/vendor.trace', O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
    if (trace285 >= 0) {
        struct stat info285;
        char text285[16385];
        if (!fstat(trace285, &info285) && S_ISREG(info285.st_mode) &&
            info285.st_uid == 3021 && info285.st_size < 16384) {
            ssize_t size285 = read(trace285, text285, sizeof(text285)-1);
            if (size285 > 0) {
                text285[size285] = 0;
                dprintf(1, 'RADIO285_VENDOR_TRACE_BEGIN\\n%sRADIO285_VENDOR_TRACE_END\\n', text285);
            }
        }
        close(trace285);
    }
'''.replace(chr(39), chr(34))
    assert source.count(anchor) == 1
    return source.replace(anchor, extra + anchor, 1)

if __name__ == '__main__':
    source = (BASE / 'build-radio-native-276.py').read_text()
    source = source.replace('276', '285')
    anchor = '    return source'
    assert source.count(anchor) == 1
    source = source.replace(anchor,
        '    source = source.replace(' + repr('/data/native-bt-020.trace') + ', ' + repr('/radio261/vendor.trace') + ')\n' + anchor, 1)
    anchor = '    once = module[' + repr('once') + ']'
    source = source.replace(anchor, '    module[' + repr('runtime') + '] = runtime285\n' + anchor, 1)
    source = source.replace("result = module['outer'](text, old_digest, digest)",
                            "result = trace_outer285(module['outer'](text, old_digest, digest))", 1)
    exec(compile(source, 'build-radio-native-285.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'build-radio-native-285.generated.py'),
              runtime285=runtime285, trace_outer285=trace_outer285))
