"""Preserve immutable hashes/identities; report actual composer stages, not readiness."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-068.py')))['source']
assert source.count("number='068', tag='068'") == 1
source = source.replace("number='068', tag='068'", "number='069', tag='069'")
source = source.replace('original-graphics-provider-002', 'original-graphics-provider-004')
anchor = '    evidence = dict('
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    composer_trace_rows = sorted(set(re.findall(
        rb'COMPOSER_TRACE pid=(\d+) uid=(\d+) stage=([A-Za-z0-9_]+) errno=(-?\d+)', raw)))
    actual_original_composer_trace = [dict(pid=int(pid), uid=int(uid),
        stage=stage.decode(), errno=int(error)) for pid, uid, stage, error in composer_trace_rows
        if int(pid) in identities['composer_host']['pids'] and int(uid) == 3036]
    actual_hotplug_callback_returned = any(row['stage'] == 'hotplug_callback_returned'
        for row in actual_original_composer_trace)
''' + anchor)
source = source.replace('evidence = dict(', '''evidence = dict(
        actual_original_composer_trace=actual_original_composer_trace,
        actual_hotplug_callback_returned=actual_hotplug_callback_returned,
        ''')
compile(source, 'independent-original-graphics-069', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-069', 'exec'))
