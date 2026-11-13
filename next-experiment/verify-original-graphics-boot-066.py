"""Independently retain actual dictionary/screen-query outcomes and graph evidence."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-064.py')))['source']
source = source.replace("number='064', tag='064'", "number='066', tag='066'")
source = source.replace('import hashlib\n', 'import hashlib\nimport runpy\n')
old = "        pids = sorted({int(p) for p in re.findall(prefix + rb'PROCESS sample=\\d+ pid=(\\d+) cmd=[^\\r\\n]*' + name.encode(), raw)})"
assert source.count(old) == 1
source = source.replace(old, "        pids = runpy.run_path(str(BASE / 'next-experiment/original-graphics-process-records-001.py'))['extract_process_pids'](raw, prefix, name)")
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    observed_dictionary_files = [dict(sample=int(sample), stat=int(rc), errno=int(err),
        bytes=int(size), mode=mode.decode(), realpath=path.decode())
        for sample, rc, err, size, mode, path in re.findall(prefix +
        rb'DICT_FILE sample=(\d+) stat=(-?\d+) errno=(\d+) size=(-?\d+) mode=(\d+) real=(\S+)', raw)]
    screen_dump_wait_statuses = [int(status) for status in re.findall(prefix + rb'SCREEN_DUMP_END status=(-?\d+)', raw)]
    hilog_lines = [line.decode(errors='replace') for line in raw.splitlines()
        if re.match(rb'\d\d-\d\d \d\d:\d\d:\d\d', line)]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
        observed_dictionary_files=observed_dictionary_files,
        screen_dump_requested=bool(prefix + b'SCREEN_DUMP original_tool=1 original_service=1' in raw),
        screen_dump_wait_statuses=screen_dump_wait_statuses,
        decoded_original_hilog_lines=[line for line in hilog_lines if 'OpenUuidFile fail' not in line],
        undecoded_hilog_message_count=sum('OpenUuidFile fail' in line for line in hilog_lines),
        ''')
compile(source, 'independent-original-graphics-066', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-066', 'exec'))
