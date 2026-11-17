"""Inert, independently audited 045 staging at the user's new address."""
from pathlib import Path
import runpy

p = runpy.run_path(str(Path(__file__).with_name('native-presentation-session-045.py')))
source = runpy.run_path(str(Path(__file__).with_name('stage-native-original-graphics-boot-045.py')))['source']
source = p['connection_source'](source)
if __name__ == '__main__':
    exec(compile(source, 'stage045-attempt002', 'exec'), {'__name__': '__main__', '__file__': __file__})
