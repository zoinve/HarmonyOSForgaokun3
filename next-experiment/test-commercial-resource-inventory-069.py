"""Compile the exact observer and admit only its read-only archive delta."""
from pathlib import Path
import ast
import hashlib
import json
import runpy
import subprocess

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
h = runpy.run_path(str(b / 'commercial-resource-inventory-069.py'))
work = root / 'commercial-resource-inventory-test-069'
work.mkdir()
fixture = work / 'root'
folder = fixture / 'system/app/HwStartupGuide/resources/rawfile'
folder.mkdir(parents=True)
video = folder / 'welcome_land_one.mp4'
video.write_bytes(b'ORIGINAL-FILE-FIXTURE\0')
before = hashlib.sha256(video.read_bytes()).hexdigest()
source = r'''
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <assert.h>
static int commercial_diag_fd003=1;
static void commercial_stream043(const char *p,unsigned s,unsigned i,unsigned n){
 (void)p;(void)s;(void)i;(void)n;
}
'''+h['HELPER']+r'''
int main(int argc,char **argv){
 assert(argc==2);errno=EDOM;
 resource069_path(10,(long)getpid(),argv[1],"/system/app/HwStartupGuide");
 assert(errno==EDOM);
 resource069_path(10,(long)getpid(),argv[1],"/system/app/HwStartupGuide/resources/rawfile/welcome_land_one.mp4");
 assert(errno==EDOM);
 resource069_path(10,(long)getpid(),argv[1],"/data/storage/el1/bundle/pc_hwstartupguide/resources.index");
 assert(errno==EDOM);
 commercial_resource_inventory069(0,(long)getpid());assert(errno==EDOM);
 return 0;
}
'''
(work / 'test.c').open('x').write(source)
command = ['gcc','-O2','-Wall','-Wextra','-Werror',str(work/'test.c'),'-o',str(work/'test')]
compiled = subprocess.run(command, capture_output=True)
(work / 'compile.stderr').open('xb').write(compiled.stderr)
assert compiled.returncode == 0, compiled.stderr.decode(errors='replace')
tested = subprocess.run([str(work / 'test'),str(fixture)], capture_output=True)
(work / 'test.stdout').open('xb').write(tested.stdout)
(work / 'test.stderr').open('xb').write(tested.stderr)
assert tested.returncode == 0, tested.stderr.decode(errors='replace')
assert b'bytes='+str(len(video.read_bytes())).encode()+b' errno=0' in tested.stdout
assert b'hex='+video.read_bytes().hex().encode() in tested.stdout
assert b'lstat=-1 lerrno=2 stat=-1 serrno=2' in tested.stdout
assert b'name=resources type=' in tested.stdout
assert hashlib.sha256(video.read_bytes()).hexdigest() == before
old = runpy.run_path(str(b / 'build-commercial-native-068.py'))
new = runpy.run_path(str(b / 'build-commercial-native-069.py'))
assert new['inner'] == h['instrument'](old['inner'])
assert new['inner'].replace(h['HELPER']+'\n','',1).replace(
    '            if(!strcmp(text,"com.huawei.hmos.hwstartupguide"))commercial_resource_inventory069(sample,id);\n','',1) == old['inner']
assert new['outer'].replace('commercial61-native-069','commercial61-native-068').replace(
    'COMMERCIAL069','COMMERCIAL068') == old['outer']
tree = ast.parse(runpy.run_path(str(b / 'build-native-return-overlay-033.py'))['payload'])
helpers = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(
    n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'archive-helpers','exec'),helpers)
before_archive = helpers['parse'](root / 'commercial61-native-068/initrd.img')
after = helpers['parse'](root / 'commercial61-native-069/initrd.img')
assert set(before_archive) == set(after)
changed = sorted(k for k in after if before_archive[k] != after[k])
assert changed == ['init','native-target/bootstrap'], changed
manifest = dict(compiled_observer_passed=True, fixture_source_unchanged=True,
    stat_prefix_missing_and_directory_observations_tested=True, errno_preserved=True,
    exact_read_only_source_addition=True, exact_delta_from_068=changed,
    all_other_archive_members_byte_identical=True, original_service_credentials_unchanged=True,
    live_private_object_reads=False, filesystem_mutation_by_observer=False,
    target_runtime_verified=False, desktop_verified=False)
with (b.parent / 'reports/commercial61-native-069/admission-test.json').open('x') as f:
    json.dump(manifest,f,indent=2)
print(json.dumps(manifest,indent=2))
