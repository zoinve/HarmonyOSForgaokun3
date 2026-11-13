"""Build only: capture bounded new trace lines, retaining original services/rendering."""
from pathlib import Path
import hashlib
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('build-native-original-graphics-boot-044.py')))
old_inner = parent['inner']
core_path = Path(__file__).with_name('native-perf-capture-045.h')
CORE = core_path.read_text()
core_sha = hashlib.sha256(core_path.read_bytes()).hexdigest()
HELPER = CORE + r'''
static void native_perf_capture045(unsigned sample)
{
    static off_t offset;
    static dev_t device;
    static ino_t inode;
    static size_t total;
    static unsigned epoch;
    static int stopped;
    static char data[65536];
    const size_t limit = 2U * 1024U * 1024U;
    int saved = errno;
    if (stopped) { errno = saved; return; }
    int fd = open("/data/native-perf-023.trace",O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
    if (fd < 0) {
        dprintf(1,"NATIVE_PERF_CAPTURE045_OPEN sample=%u errno=%d\n",sample,errno);
        errno = saved; return;
    }
    struct stat st;
    int stat_result=fstat(fd,&st);
    int stat_error=stat_result ? errno : 0;
    if (stat_result || !S_ISREG(st.st_mode) || st.st_nlink != 1 ||
        (st.st_uid != 0 && st.st_uid != 3036) || st.st_size < 0) {
        dprintf(1,"NATIVE_PERF_CAPTURE045_METADATA_ERROR sample=%u stat=%d errno=%d validation_failed=1\n",sample,stat_result,stat_error);
        close(fd); stopped=1; errno=saved; return;
    }
    if (inode != st.st_ino || device != st.st_dev || st.st_size < offset) {
        dprintf(1,"NATIVE_PERF_CAPTURE045_RESET sample=%u old_offset=%lld new_epoch=%u\n",sample,(long long)offset,epoch+1);
        device=st.st_dev; inode=st.st_ino; offset=0; ++epoch;
    }
    size_t per_sample = 0;
    int capacity_exhausted = 0;
    while (total < limit && per_sample < 1024U*1024U) {
        size_t capacity = limit-total;
        size_t sample_remaining = 1024U*1024U-per_sample;
        if (capacity > sample_remaining) capacity=sample_remaining;
        if (capacity > sizeof(data)) capacity=sizeof(data);
        struct capture045_result r=capture045_read(fd,offset,data,capacity);
        if (r.error) {
            if (r.error==EMSGSIZE && capacity<sizeof(data)) {
                if (limit-total <= sample_remaining) capacity_exhausted=1;
            }
            else {
                dprintf(1,"NATIVE_PERF_CAPTURE045_READ_ERROR sample=%u offset=%lld errno=%d\n",sample,(long long)offset,r.error);
                stopped=1;
            }
            break;
        }
        if (!r.complete) break; /* Retain a partial final line for the next sample. */
        dprintf(1,"NATIVE_PERF_CAPTURE045_BEGIN sample=%u epoch=%u offset=%lld bytes=%zu\n",sample,epoch,(long long)offset,r.complete);
        size_t done=0;
        while (done<r.complete) {
            ssize_t n=write(1,data+done,r.complete-done);
            if (n<0 && errno==EINTR) continue;
            if (n<=0) {
                dprintf(2,"NATIVE_PERF_CAPTURE045_WRITE_ERROR sample=%u errno=%d written=%zu\n",sample,n<0?errno:EIO,done);
                stopped=1; break;
            }
            done+=(size_t)n;
        }
        if (stopped) break;
        offset=r.next; total+=r.complete; per_sample+=r.complete;
        dprintf(1,"NATIVE_PERF_CAPTURE045_END sample=%u epoch=%u offset=%lld total=%zu\n",sample,epoch,(long long)offset,total);
    }
    if (total>=limit || capacity_exhausted) {
        dprintf(1,"NATIVE_PERF_CAPTURE045_LIMIT sample=%u limit=%zu captured=%zu completeness=0\n",sample,limit,total);
        stopped=1;
    }
    dprintf(1,"NATIVE_PERF_CAPTURE045_STATE sample=%u epoch=%u offset=%lld captured=%zu observed_size=%lld stopped=%d writer_buffer_tail_unknown=1\n",
            sample,epoch,(long long)offset,total,(long long)st.st_size,stopped);
    close(fd); errno=saved;
}
'''
ANCHOR = 'static void diagnostic_state_002('
CALL = '        diagnostic_file_002(sample,"/data/native-perf-023.trace");'
assert old_inner.count(ANCHOR) == old_inner.count(CALL) == 1
inner = old_inner.replace(ANCHOR, HELPER + '\n' + ANCHOR, 1)
inner = inner.replace(CALL, '        native_perf_capture045(sample);', 1)


def restore_inner(source):
    assert source.count(HELPER + '\n') == source.count('        native_perf_capture045(sample);') == 1
    return source.replace(HELPER + '\n', '', 1).replace('        native_perf_capture045(sample);', CALL, 1)


assert restore_inner(inner) == old_inner
frozen = Path(__file__).resolve().parents[1] / 'reports/native-original-graphics-boot-044'
assert (frozen/'bootstrap.c').read_bytes() == old_inner.encode()
assert (frozen/'init.c').read_bytes() == parent['outer'].encode()
outer = parent['outer'].replace('native-interactive-044-%s','native-interactive-045-%s').replace('NATIVE_UNATTENDED044','NATIVE_UNATTENDED045')
payload = parent['payload']
assert payload.count('inner='+repr(old_inner)) == payload.count('outer='+repr(parent['outer'])) == 1
payload = payload.replace('inner='+repr(old_inner),'inner='+repr(inner),1).replace('outer='+repr(parent['outer']),'outer='+repr(outer),1)
payload = payload.replace('native-original-graphics-boot-044','native-original-graphics-boot-045')
payload = payload.replace("original_work=Path('/home/zoinve/harmony-virgl-883/native-original-graphics-boot-043')",
                          "original_work=Path('/home/zoinve/harmony-virgl-883/native-original-graphics-boot-044')")
for old,new in [('changed_vs043','changed_vs044'),('baseline043_files','baseline044_files'),('preserved_vs043','preserved_vs044')]:
    payload = payload.replace(old,new)
guard = "from pathlib import Path\nimport hashlib\ncapture_core=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/native-perf-capture-045.h')\n"
guard += f"assert hashlib.sha256(capture_core.read_bytes()).hexdigest()=='{core_sha}'\n"
payload = guard + payload + f"\nassert hashlib.sha256(capture_core.read_bytes()).hexdigest()=='{core_sha}'\n"
payload = payload.replace('audit=dict(', f"audit=dict(capture_core_sha256='{core_sha}',bootstrap_source_changes_only_incremental_perf_capture=True,")
compile(payload,'native-incremental-capture-045-build','exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=900).returncode)
