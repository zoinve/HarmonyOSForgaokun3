"""Offline synthetic perf records and exact original module/userland comparison."""
from pathlib import Path
import ast
import hashlib
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parents[1]
ROOT = Path('/home/zoinve/harmony-virgl-883')
TEST = r'''
#define main diagnostic_main
#include "INIT050"
#undef main
#include <assert.h>
int main(void)
{
    unsigned char source[8]={0,1,2,3,4,5,6,7},out[6]={0},expected[6]={6,7,0,1,2,3};
    hw050_ring_copy(out,source,8,6,6);assert(!memcmp(out,expected,6));
    size_t length=4096+128;unsigned char *memory=calloc(1,length);assert(memory);
    struct perf_event_mmap_page *meta=(void *)memory;meta->data_offset=4096;meta->data_size=128;meta->data_tail=80;meta->data_head=176;
    unsigned char record[96]={0};struct perf_event_header header={.type=PERF_RECORD_SAMPLE,.size=96};
    uint64_t ip=0x1234,ns=123456,abi=PERF_SAMPLE_REGS_ABI_64,regs[7]={11,12,13,14,15,16,17};uint32_t ids[2]={42,43};
    memcpy(record,&header,8);memcpy(record+8,&ip,8);memcpy(record+16,ids,8);memcpy(record+24,&ns,8);memcpy(record+32,&abi,8);memcpy(record+40,regs,56);
    for(unsigned i=0;i<96;++i)memory[4096+(80+i)%128]=record[i];
    struct hw050_event event={.tid=43,.spec=0,.used=1,.fd=open("/dev/null",O_RDONLY),.mapping=memory,.length=length};
    assert(event.fd>=0);hw050_addresses[0]=ip;hw050_drain(&event);
    assert(event.samples==1 && event.malformed==0 && meta->data_tail==176);
    unsigned char lost[24]={0};header.type=PERF_RECORD_LOST;header.size=24;uint64_t count=7;
    memcpy(lost,&header,8);memcpy(lost+16,&count,8);
    for(unsigned i=0;i<24;++i)memory[4096+(176+i)%128]=lost[i];
    meta->data_head=200;hw050_drain(&event);assert(event.lost==7 && meta->data_tail==200);
    meta->data_head=205;hw050_drain(&event);assert(event.malformed==1 && meta->data_tail==200);
    close(event.fd);free(memory);puts("PASS: wrapped sample, seven real register fields, lost records and partial header");return 0;
}
'''


def main():
    report = BASE / 'reports/commercial61-native-050'
    assert not (report / 'hwbreak-test.json').exists()
    work = ROOT / 'commercial61-native-050/hwbreak-unit'
    work.mkdir()
    source = TEST.replace('INIT050', str(ROOT / 'commercial61-native-050/init.c'))
    (work / 'test.c').open('x').write(source)
    result = subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(BASE / 'next-experiment'),
                             str(work / 'test.c'), str(BASE / 'next-experiment/baremetal-diagnostic-core.c'),
                             '-o', str(work / 'test')], capture_output=True)
    (report / 'hwbreak-test-compile.stderr').open('xb').write(result.stderr)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    result = subprocess.run([str(work / 'test')], capture_output=True)
    (report / 'hwbreak-test.stdout').open('xb').write(result.stdout)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    tree = ast.parse(runpy.run_path(str(BASE / 'next-experiment/build-native-return-overlay-033.py'))['payload'])
    helpers = {}
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))], type_ignores=[]), 'archive-helpers', 'exec'), helpers)
    old = helpers['parse'](ROOT / 'commercial61-native-045/initrd.img')
    new = helpers['parse'](ROOT / 'commercial61-native-050/initrd.img')
    assert set(old) == set(new)
    changed = [name for name in old if old[name] != new[name]]
    assert changed == ['init'], changed
    module = runpy.run_path(str(BASE / 'next-experiment/build-commercial-native-050.py'))
    assert 'tracefs' not in module['outer'] and 'uprobe_events' not in module['outer']
    for value in ['HW_BREAKPOINT_X', 'attr.disabled=1', 'attr.sample_regs_user=0x7f', 'attr.exclude_kernel=1', 'PERF_RECORD_LOST', '__ATOMIC_ACQUIRE', '__ATOMIC_RELEASE']:
        assert value in module['outer']
    manifest = dict(synthetic_ring_tests_passed=True, changed_archive_members=changed,
                    modules_byte_identical_to_045=True, original_bootstrap_byte_identical=True,
                    original_userland_byte_identical=True, hardware_attachment_runtime_verified=False,
                    helper_sha256=hashlib.sha256((BASE / 'next-experiment/commercial-hwbreak-050.h').read_bytes()).hexdigest())
    (report / 'hwbreak-test.json').open('x').write(json.dumps(manifest, indent=2))
    print(result.stdout.decode())
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
