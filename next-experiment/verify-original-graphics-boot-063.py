"""Independently verify unchanged originals and actual targeted HiLog evidence."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('verify-original-graphics-boot-062.py')))['source']
assert "number='062', tag='059'" in source
source = source.replace("number='062', tag='059'", "number='063', tag='063'")
source = source.replace('evidence = dict(', r'''evidence = dict(
        targeted_original_hilog_queries=[dict(sample=int(sample), pid=int(pid))
            for sample, pid in re.findall(prefix + rb'HILOG_QUERY sample=(\d+) pid=(\d+) original_tool=1', raw)],
        targeted_original_hilog_wait_statuses=[int(value)
            for value in re.findall(prefix + rb'HILOG_EXIT status=(\d+)', raw)],
        ''')
compile(source, 'independent-original-graphics-063', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'independent-original-graphics-063', 'exec'))
