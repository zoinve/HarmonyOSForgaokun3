from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent

def vendor_trace(source):
    helper = '''#include <dlfcn.h>
static void radio276_log(const char *operation, int result, int error)
{
    typedef int (*log_function)(int, int, unsigned, const char *, const char *, ...);
    log_function log = (log_function)dlsym(RTLD_DEFAULT, "HiLogPrint");
    if (log) log(3, 4, 0xD00105, "QcaTransport276",
        "operation=%{public}s result=%{public}d errno=%{public}d uid=%{public}u",
        operation, result, result < 0 ? error : 0, (unsigned)getuid());
}
'''
    anchor = 'static const BtVendorCallbacksT *callbacks;'
    assert source.count(anchor) == 1
    source = source.replace(anchor, helper + anchor, 1)
    anchor = 'int saved=errno;int fd=open('
    assert source.count(anchor) == 1
    source = source.replace(anchor, 'int saved=errno;radio276_log(operation,result,saved);int fd=open(', 1)
    return source

if __name__ == '__main__':
    module = runpy.run_path(str(BASE / 'build-radio-native-261.py'))
    once = module['once']
    source = (BASE / 'build-radio-native-261.py').read_text()
    source = source[source.index('if __name__ == '):]
    source = source.replace('commercial61-native-261', 'commercial61-native-276')
    source = once(source, '        stage = Path(tmp)', '''        stage = Path(tmp)
        for header in ['persistent-data-166.h', 'persistent-data-172.h', 'persistent-unmount-plan-201.h', 'native-live-debug-159.h']:
            os.link(parent / header, stage / header)''')
    source = once(source, '        vendor = once(vendor,', '        vendor = vendor_trace(vendor)\n        vendor = once(vendor,')
    source = once(source, '''        entries['radio261/hdf_devhost.cfg'] = (0o100644, config)
        for name in ['qca-broker', 'wifi-count', 'libbt_vendor.z.so']:
            entries['radio261/' + name] = (0o100755, (stage / name).read_bytes())''', '''        entries['native-target/radio261'] = (0o40755, b'')
        entries['native-target/radio261/hdf_devhost.cfg'] = (0o100644, config)
        entries['native-target/radio261/libbt_vendor.z.so'] = (0o100755, (stage / 'libbt_vendor.z.so').read_bytes())
        for name in ['qca-broker', 'wifi-count']:
            entries['radio261/' + name] = (0o100755, (stage / name).read_bytes())''')
    def outer276(text, old_digest, digest):
        result = module['outer'](text, old_digest, digest)
        assert result.count('/commercial61-native-261/bootstrap-runtime087') == 5
        return result.replace('/commercial61-native-261/bootstrap-runtime087',
                              '/commercial61-native-276/bootstrap-runtime087')
    env = dict(module, __name__='__main__', outer=outer276, vendor_trace=vendor_trace)
    exec(compile(source, 'build-radio-native-276.generated.py', 'exec'), env)
