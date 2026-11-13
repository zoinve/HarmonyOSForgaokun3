"""Exercise the actual runner capture block without a live QEMU."""
from pathlib import Path
import tempfile
import textwrap

source = Path(__file__).with_name('runner-template.py').read_text()
start = source.rfind('   if ', 0, source.index('    shot+=1;target='))
block = textwrap.dedent(source[start:source.index('   if observation_done(elapsed,observed):')])
import hashlib

with tempfile.TemporaryDirectory() as directory:
    def run(error=None, enabled=True):
        def qmp(request):
            assert enabled, 'disabled capture must never call QMP'
            if error:
                raise AssertionError({'error': {'class': 'GenericError', 'desc': error}})
            Path(request['arguments']['filename']).write_bytes(b'P6 test')
        scope = dict(elapsed=60, next_shot=60, observed=None, shot=0,
                     observation_done=lambda *_: False, o=Path(directory),
                     d={'screenshots': []}, qmp=qmp, hashlib=hashlib,
                     c={'qmp_screenshots_enabled': enabled})
        exec(block, scope)
        return scope
    missing = run('no surface')
    assert not missing['d']['screenshots']
    assert missing['d']['screenshot_unavailable'][0]['reason'] == 'no surface'
    assert missing['next_shot'] == 180
    assert len(run()['d']['screenshots']) == 1
    assert run(enabled=False)['shot'] == 0
    try:
        run('permission denied')
    except AssertionError:
        pass
    else:
        raise AssertionError('unrelated screenshot errors must remain fatal')
print('PASS: no-surface capture is recorded, genuine capture and other errors preserved')
