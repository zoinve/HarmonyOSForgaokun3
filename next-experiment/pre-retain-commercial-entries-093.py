"""Archive only entry 091 before allocation-constrained 093 installation."""
from pathlib import Path
import json
import runpy

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    report = BASE.parent/'reports/commercial61-native-093'
    assert not (report/'installation-result.json').exists()
    assert all(json.loads((report/'admission-test.json').read_text()).values())
    assert json.loads((report/'overlay-result.json').read_text())['bytes'] < 4096
    source = (BASE/'retain-latest-experiment-boot-entries-001.py').read_text()
    anchor = 'assert len(commercial)>=2'
    assert source.count(anchor) == 1
    source = source.replace(anchor, "assert [p.name for p in commercial]==['commercial61-native-091.conf','commercial61-native-092.conf']", 1)
    assert source.count('commercial[-2:]') == 1
    source = source.replace('commercial[-2:]', 'commercial[-1:]', 1)
    workflow = runpy.run_path(str(BASE/'commercial-workflow-093.py'))
    workflow['configure_local_transport']()
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
