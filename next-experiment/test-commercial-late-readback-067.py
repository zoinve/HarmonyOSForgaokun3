"""Compile and exercise the exact late gate without booting the device."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import tempfile

b = Path(__file__).resolve().parent
h = runpy.run_path(str(b / 'commercial-late-readback-067.py'))
gate = h['GATE']
test = r'''
#include <cerrno>
#include <cassert>
#include <thread>
#include <vector>
#include <atomic>
#include <time.h>
static timespec fake_now={};
static bool fail_clock=false;
static int fake_clock(clockid_t, timespec *out){
 if(fail_clock){errno=EIO;return -1;}
 *out=fake_now;return 0;
}
#define clock_gettime fake_clock
'''+gate+r'''
int main(){
 unsigned long long next=0;
 errno=EDOM;
 fake_now.tv_sec=99;assert(!late_observation067(&next));assert(next==0);
 fail_clock=true;assert(!late_observation067(&next));assert(errno==EDOM);
 fail_clock=false;
 fake_now.tv_sec=100;assert(late_observation067(&next));assert(errno==EDOM);
 assert(next==105000000000ULL);assert(!late_observation067(&next));
 fake_now.tv_sec=104;fake_now.tv_nsec=999999999;assert(!late_observation067(&next));
 fake_now.tv_sec=105;fake_now.tv_nsec=0;assert(late_observation067(&next));
 fake_now.tv_sec=145;assert(!late_observation067(&next));
 next=0;unsigned accepted=0;
 for(int second=0;second<200;++second){
  fake_now.tv_sec=second;
  if(late_observation067(&next))++accepted;
 }
 assert(accepted==9);
 next=0;fake_now.tv_sec=120;
 std::atomic<unsigned> winners{0};std::vector<std::thread> threads;
 for(unsigned i=0;i<32;++i)threads.emplace_back([&]{
  errno=ERANGE;if(late_observation067(&next))++winners;assert(errno==ERANGE);
 });
 for(auto &thread:threads)thread.join();
 assert(winners==1);
}
'''
with tempfile.TemporaryDirectory(prefix='late-readback-067-') as tmp:
    path = Path(tmp)
    source = path / 'test.cpp'
    source.write_text(test)
    subprocess.run(['g++', '-std=c++17', '-pthread', '-Wall', '-Wextra',
                    '-Werror', str(source), '-o', str(path / 'test')], check=True)
    subprocess.run([str(path / 'test')], check=True)

actual = Path('/home/zoinve/harmony-virgl-883/commercial-egl-067/egl-trace-067.cpp').read_text()
prior = Path('/home/zoinve/harmony-virgl-883/commercial-egl-035/egl-trace-035.cpp').read_text()
assert actual.count(gate) == 1
restored = actual.replace(gate + '\n', '', 1)
restored = restored.replace(
 ' static unsigned long long next_dispatch067=0;\n'
 ' if(sample033>16 && !late_observation067(&next_dispatch067)){errno=saved033;return;}',
 ' if(sample033>16){errno=saved033;return;}', 1)
restored = restored.replace(
 '            static unsigned long long next_copy067=0;\n'
 '            bool observe031=__atomic_fetch_add(&count031,1u,__ATOMIC_RELAXED)<8\n'
 '                || late_observation067(&next_copy067);',
 '            bool observe031=__atomic_fetch_add(&count031,1u,__ATOMIC_RELAXED)<8;', 1)
assert restored == prior, 'Unexpected change beyond two diagnostic observation gates'
result = dict(compiled_gate_passed=True, clock_failure_preserves_errno=True,
              concurrent_winners=1, late_samples_per_route_max=9,
              late_interval_seconds=[100, 145], interval_end_exclusive=True,
              min_spacing_seconds=5, exact_source_delta_verified=True,
              source_sha256=hashlib.sha256(actual.encode()).hexdigest(),
              target_runtime_verified=False, desktop_verified=False)
out = b.parent / 'reports/commercial-late-readback-test-067.json'
assert not out.exists(), 'Never overwrite numbered test evidence'
out.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
