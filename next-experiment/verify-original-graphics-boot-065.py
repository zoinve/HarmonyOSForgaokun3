"""Check immutable graph evidence and actual private-query decoding, without readiness claims."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-064.py')))['source']
source = source.replace("number='064', tag='064'", "number='065', tag='065'")
source = source.replace('import hashlib\n', 'import hashlib\nimport runpy\n')
old = "        pids = sorted({int(p) for p in re.findall(prefix + rb'PROCESS sample=\\d+ pid=(\\d+) cmd=[^\\r\\n]*' + name.encode(), raw)})"
assert source.count(old) == 1
source = source.replace(old, "        pids = runpy.run_path(str(BASE / 'next-experiment/original-graphics-process-records-001.py'))['extract_process_pids'](raw, prefix, name)")
anchor = "sources=[('original-graphics-provider-002','graphics-provider/')]"
assert source.count(anchor) == 1
source = source.replace(anchor, '''assert hashlib.sha256(entries['graphics-dict-info.json'][1]).hexdigest()=='d8b36a8aca5c9adfd610395ba9de0368f782e475f7ae7d1be8241e8db8e5f50a'
''' + anchor)
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    hilog_lines = [line.decode(errors='replace') for line in raw.splitlines()
        if re.match(rb'\d\d-\d\d \d\d:\d\d:\d\d', line)]
    decoded_original_hilog_lines = [line for line in hilog_lines if 'OpenUuidFile fail' not in line]
    private_index_mounts_observed = len(re.findall(prefix + rb'HILOG_INDEX genuine_cache=1 private_query_namespace=1 readonly=1', raw))
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
        decoded_original_hilog_lines=decoded_original_hilog_lines,
        undecoded_hilog_message_count=sum('OpenUuidFile fail' in line for line in hilog_lines),
        private_index_mounts_observed=private_index_mounts_observed,
        private_index_mount_errors=[int(value) for value in re.findall(prefix + rb'HILOG_INDEX_ERROR errno=(\\d+)', raw)],
        ''')
compile(source, 'independent-original-graphics-065', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-065', 'exec'))
