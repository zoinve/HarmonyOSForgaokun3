"""Resolve diagnostic forwarding through the actual mapper plugin handle."""
from pathlib import Path
import sys

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
source = (base / 'build-native-alloc-trace-938.py').read_text()
replacements = {
    "official-native-alloc-trace-938": "official-native-alloc-handle-939",
    "native-alloc-trace-938": "native-alloc-handle-939",
    "official-native-vendor-937/initramfs.cpio.gz": "official-native-alloc-trace-938/initramfs.cpio.gz",
    "5933fad14ba4495d2cf29265a0a588e6213d10c2b7cc66758edbae4a5daa7145":
        "a58a759c49a27b6ae3c28edd56882bd974afbf95c84b1a9332168f90ea9a7e2b",
    'Fn real = (Fn)dlsym(RTLD_NEXT, "{symbol}");': '''void *plugin = dlopen("/vendor/lib64/passthrough/libmapper_service_1.0.z.so", RTLD_NOW | RTLD_LOCAL);
    Fn real = plugin ? (Fn)dlsym(plugin, "{symbol}") : NULL;
    if (real == (Fn)trace_{method}) {{ puts("NATIVE939_SELF_RESOLUTION"); exit(126); }}''',
    'NATIVE938_': 'NATIVE939_',
}
for old, new in replacements.items():
    assert old in source, old
    source = source.replace(old, new)
if sys.argv[1:] == ['--resume-incomplete']:
    source = source.replace('assert not out.exists() and not work.exists()',
                            'assert not out.exists() and work.is_dir()')
    source = source.replace('work.mkdir()', 'assert work.is_dir()')
else:
    assert not sys.argv[1:]
exec(compile(source, str(base / 'build-native-alloc-trace-938.py'), 'exec'))
