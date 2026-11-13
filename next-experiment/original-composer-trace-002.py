"""Leave the original multiline LAYER_SETTER macro completely unchanged."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('original-composer-trace-001.py')))
strip_trace = parent['strip_trace']


def adapt(source):
    traced = parent['adapt'](source)
    injected = '\n    /*COMPOSER_TRACE*/ composer_trace("entry_name");'
    assert traced.count(injected) == 1
    traced = traced.replace(injected, '')
    assert strip_trace(traced) == source
    return traced
