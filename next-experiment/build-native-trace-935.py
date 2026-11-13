"""Expose existing bridge trace in a new diskless fixture; no driver changes."""
from pathlib import Path
import gzip
import hashlib
import json
import subprocess

base = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
root = Path('/home/zoinve/harmony-virgl-883')
out = base / 'official-native-trace-935'
work = root / 'native-trace-935'
assert not out.exists() and not work.exists()
old = (base / 'official-native-present-934/initramfs.cpio.gz').read_bytes()
assert hashlib.sha256(old).hexdigest() == 'd037f4b7f3c5b509832a610a094c99c066bc4f73ea3d29907b6b448a4bf9866e'
source = (root / 'native-present-934/probe.c').read_text()
source = '#include <dirent.h>\n#include <sys/stat.h>\n' + source
anchor = 'int main(void)'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
static void dump_bridge_trace(void)
{
    DIR *dir = opendir("/dev/gpu893-trace");
    if (!dir) { perror("NATIVE935 trace opendir"); return; }
    struct dirent *ent;
    while ((ent = readdir(dir))) {
        if (ent->d_name[0] == '.') continue;
        char path[512];
        snprintf(path, sizeof(path), "/dev/gpu893-trace/%s", ent->d_name);
        FILE *file = fopen(path, "r");
        if (!file) continue;
        printf("NATIVE935_TRACE_BEGIN %s\n", ent->d_name);
        char line[2048];
        while (fgets(line, sizeof(line), file)) fputs(line, stdout);
        fclose(file);
        puts("NATIVE935_TRACE_END");
    }
    closedir(dir);
}
''' + anchor)
anchor = '    setvbuf(stdout, NULL, _IONBF, 0);'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n    require(mkdir("/dev/gpu893-trace", 0700) == 0, "create diagnostic trace directory");\n    require(atexit(dump_bridge_trace) == 0, "register diagnostic trace dump");')
source = source.replace('NATIVE934_', 'NATIVE935_')
work.mkdir()
(work / 'probe.c').write_text(source)
libs = root / 'official-frontend-probe-927'
subprocess.run([str(root / 'window-bridge/toolchain/ohos-cc'), '-O2', '-Wall', '-Wextra',
    '-I' + str(root / 'prefix/include'), str(work / 'probe.c'), str(libs / 'libEGL.so'),
    str(libs / 'libGLESv3.so'), '-ldl', '-Wl,-rpath,/system/lib64/lab-softpipe-167',
    '-Wl,-rpath-link,' + str(libs), '-o', str(work / 'probe')], check=True)
raw = gzip.decompress(old)
chunks, pos, changed = [], 0, []
while True:
    begin = pos
    h = raw[pos:pos+110]
    assert h[:6] == b'070701'
    size, ns = int(h[54:62], 16), int(h[94:102], 16)
    name = raw[pos+110:pos+109+ns].decode()
    start = (pos+110+ns+3) & ~3
    pos = (start+size+3) & ~3
    if name == 'gpu-userspace-probe':
        body = (work / 'probe').read_bytes()
        chunk = h[:54] + f'{len(body):08x}'.encode() + h[62:] + raw[begin+110:start] + body
        chunks.append(chunk + b'\0' * (-len(chunk) % 4))
        changed.append(name)
    else:
        chunks.append(raw[begin:pos])
    if name == 'TRAILER!!!': break
assert changed == ['gpu-userspace-probe']
archive = gzip.compress(b''.join(chunks), mtime=0)
out.mkdir()
(out / 'initramfs.cpio.gz').write_bytes(archive)
(out / 'manifest.json').write_text(json.dumps(dict(initrd_sha256=hashlib.sha256(archive).hexdigest(),
    changed_entries=changed, disks_attached=0, desktop_verified=False), indent=2))
print((out / 'manifest.json').read_text())
