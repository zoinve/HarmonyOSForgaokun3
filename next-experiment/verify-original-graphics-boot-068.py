"""Verify authentic HDF log queries alongside unchanged original graph evidence."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-067.py')))['source']
old = "number='067', tag='067'"
assert source.count(old) == 1
source = source.replace(old, "number='068', tag='068'")
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    original_hdf_log_queries = [dict(sample=int(sample), pid=int(pid), target=int(target))
        for sample, pid, target in re.findall(prefix +
        rb'HDF_HILOG_QUERY sample=(\d+) pid=(\d+) target=(\d+) original_tool=1', raw)]
    original_hdf_log_query_results = [dict(pid=int(pid), wait_status=int(status))
        for pid, status in re.findall(prefix + rb'HDF_HILOG_EXIT pid=(\d+) status=(-?\d+)', raw)]
    queried_hdf_pids = {row['pid'] for row in original_hdf_log_queries}
    decoded_original_hdf_lines = [line for line in hilog_lines
        if (match := re.match(r'\d\d-\d\d \d\d:\d\d:\d\d\.\d+\s+(\d+)\s+', line))
        and int(match.group(1)) in queried_hdf_pids and 'OpenUuidFile fail' not in line]
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
        original_hdf_log_queries=original_hdf_log_queries,
        original_hdf_log_query_results=original_hdf_log_query_results,
        decoded_original_hdf_lines=decoded_original_hdf_lines,
        ''')
compile(source, 'independent-original-graphics-068', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-068', 'exec'))
