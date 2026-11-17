from pathlib import Path
import ast
import hashlib
import json
import runpy
import subprocess

B = Path(__file__).resolve().parent
ROOT = Path('/home/zoinve/harmony-virgl-883')
REPORT = B.parent / 'reports/commercial61-native-066'
STREAM_TEST = r'''
static void test_stream066(void)
{
    char path[]="/tmp/perf-stream066-XXXXXX";
    int input=mkstemp(path);assert(input>=0);
    char chunk[1000];memset(chunk,'x',sizeof(chunk));
    for(unsigned i=0;i<40;++i)assert(write(input,chunk,sizeof(chunk))==sizeof(chunk));
    assert(close(input)==0);
    FILE *capture=tmpfile();assert(capture);
    commercial_diag_fd003=fileno(capture);
    errno=EDOM;commercial_stream043(path,1,0,32768);assert(errno==EDOM);
    commercial_stream043(path,2,0,262144);
    assert(fflush(capture)==0 && fseek(capture,0,SEEK_SET)==0);
    char *text=calloc(1,100000);assert(text);
    size_t count=fread(text,1,99999,capture);assert(count>72000);
    assert(strstr(text,"bytes=32768 eof=0 errno=0"));
    assert(strstr(text,"bytes=40000 eof=1 errno=0"));
    free(text);fclose(capture);commercial_diag_fd003=-1;
    assert(unlink(path)==0);
}
'''

if __name__ == '__main__':
    before = runpy.run_path(str(B / 'build-commercial-native-065.py'))
    after = runpy.run_path(str(B / 'build-commercial-native-066.py'))
    helper = runpy.run_path(str(B / 'commercial-perf-stream-066.py'))
    assert after['inner'] == helper['repair'](before['inner'])
    assert after['inner'].replace(helper['NEW'], helper['OLD'], 1) == before['inner']
    assert after['outer'].replace('commercial61-native-066', 'commercial61-native-065').replace('COMMERCIAL066', 'COMMERCIAL065') == before['outer']
    for bad in ['', helper['OLD'] + helper['OLD']]:
        try:
            helper['repair'](bad)
        except AssertionError:
            pass
        else:
            raise AssertionError('Ambiguous source was accepted')
    tree = ast.parse(runpy.run_path(str(B / 'build-native-return-overlay-033.py'))['payload'])
    helpers = {}
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef))], type_ignores=[]), 'archive-helpers', 'exec'), helpers)
    old = helpers['parse'](ROOT / 'commercial61-native-065/initrd.img')
    new = helpers['parse'](ROOT / 'commercial61-native-066/initrd.img')
    assert set(old) == set(new)
    changed = sorted(name for name in old if old[name] != new[name])
    assert changed == ['init', 'native-target/bootstrap'], changed
    work = ROOT / 'commercial61-native-066/perf-stream-unit-revision3'
    work.mkdir()
    current_tests = ast.parse(runpy.run_path(str(B / 'test-commercial-hwbreak-065.py'))['source'])
    test = next(ast.literal_eval(node.value) for node in current_tests.body
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'TEST' for t in node.targets))
    start = after['inner'].index('static void commercial_stream043(')
    end = after['inner'].index('static void commercial_binder_debug043(', start)
    stream_source = 'static int commercial_diag_fd003=-1;\n' + after['inner'][start:end]
    test = test.replace('int main(void)', stream_source + STREAM_TEST + '\nint main(void)', 1)
    test = test.replace('    unsigned char source[8]', '    test_stream066();\n    unsigned char source[8]', 1)
    source = test.replace('INIT050', str(ROOT / 'commercial61-native-066/init.c'))
    (work / 'test.c').open('x').write(source)
    compilation = subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(B), str(work / 'test.c'), str(B / 'baremetal-diagnostic-core.c'), '-o', str(work / 'test')], capture_output=True)
    (REPORT / 'perf-stream-test-revision3-compile.stderr').open('xb').write(compilation.stderr)
    assert compilation.returncode == 0, compilation.stderr.decode(errors='replace')
    result = subprocess.run([str(work / 'test')], capture_output=True)
    (REPORT / 'perf-stream-test-revision3.stdout').open('xb').write(result.stdout)
    (REPORT / 'perf-stream-test-revision3.stderr').open('xb').write(result.stderr)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    subprocess.run(['python3', str(B / 'test-commercial-account-order-063.py')], check=True)
    subprocess.run(['python3', str(B / 'test-commercial-event-state-064.py')], check=True)
    baseline = json.loads((B.parent / 'reports/commercial61-native-065/hwbreak-test-revision3.json').read_text())
    assert baseline['synthetic_ring_tests_passed'] and baseline['executable_memory_tests_passed']
    manifest = dict(exact_delta_from_065=changed, exact_read_only_source_delta=True,
                    all_other_archive_members_byte_identical=True, synthetic_ring_tests_passed=True,
                    bootstrap_sha256=hashlib.sha256(new['native-target/bootstrap'][1]).hexdigest(),
                    bounded_stream_bytes=262144, desktop_verified=False)
    (REPORT / 'perf-stream-test.json').open('x').write(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))
