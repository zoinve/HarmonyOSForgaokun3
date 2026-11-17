"""Own request logger: bounded concurrency, errno and no-follow behavior."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import shutil
import subprocess

base = Path(__file__).resolve().parent
module = runpy.run_path(str(base / 'commercial-allocator-observer-073.py'))
work = Path('/home/zoinve/harmony-virgl-883/commercial-allocator-logger-test-073-r2')
report = base.parent / 'reports/commercial-allocator-logger-test-073-r2'
work.mkdir()
report.mkdir()
source = r'''
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <fcntl.h>
#include <thread>
#include <unistd.h>
struct BufferAllocInfo {
    uint32_t width, height;
    int32_t format;
    uint64_t usage, expectedSize;
};
static const char *trace_path073;
#define COMMERCIAL073_TRACE_PATH trace_path073
''' + module['LOGGER'] + r'''
int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    trace_path073 = argv[1];
    std::atomic<int> errors{0};
    auto worker = [&] {
        BufferAllocInfo info{2560, 1440, 24, 0x1035, 5529600};
        for (int i = 0; i < 64; ++i) {
            errno = EDOM;
            allocator073_request(info);
            if (errno != EDOM) ++errors;
        }
    };
    std::thread threads[4];
    for (auto &thread : threads) thread = std::thread(worker);
    for (auto &thread : threads) thread.join();
    return errors ? 3 : 0;
}
'''
with (work / 'logger-test.cpp').open('x') as f:
    f.write(source)
compiler = shutil.which('g++')
assert compiler
command = [compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror', '-pthread',
    '-fsanitize=address,undefined', '-fno-omit-frame-pointer', str(work / 'logger-test.cpp'),
    '-o', str(work / 'logger-test')]
run = subprocess.run(command, capture_output=True, text=True, timeout=60)
assert run.returncode == 0, run.stderr
normal = work / 'normal.trace'
normal.open('xb').close()
target = work / 'symlink-target'
target.open('xb').close()
symlink = work / 'symlink.trace'
symlink.symlink_to(target)
cases = []
for name, path in [('normal', normal), ('missing', work / 'missing.trace'), ('symlink', symlink)]:
    run = subprocess.run([str(work / 'logger-test'), str(path)], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0 and not run.stderr, (name, run.returncode, run.stderr)
    cases.append(dict(name=name, returncode=run.returncode, stderr=run.stderr))
rows = normal.read_text().splitlines()
assert len(rows) == 128
pattern = r'COMMERCIAL073_ALLOC_REQUEST sequence=(\d+) pid=(\d+) uid=(\d+) width=2560 height=1440 format=24 usage=0x1035 expected=5529600 public_interface=1'
matches = [re.fullmatch(pattern, row) for row in rows]
assert all(matches)
assert {int(row[1]) for row in matches} == set(range(128))
assert not (work / 'missing.trace').exists() and target.read_bytes() == b''
result = dict(command=command, cases=cases, bounded_to_128_requests=True,
    four_thread_logging_complete=True, request_fields_preserved=True, errno_preserved=True,
    missing_trace_not_created=True, symlink_target_unchanged=True, asan_ubsan_no_report=True,
    logger_sha256=hashlib.sha256(module['LOGGER'].encode()).hexdigest(),
    own_logger_only=True, real_allocator_hardware_test=False, desktop_verified=False)
with (report / 'result.json').open('x') as f:
    json.dump(result, f, indent=2)
with (report / 'normal.trace').open('xb') as f:
    f.write(normal.read_bytes())
print(json.dumps(result, indent=2))
