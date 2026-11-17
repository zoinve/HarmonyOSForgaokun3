from pathlib import Path
import runpy
import sys

BASE = Path(__file__).resolve().parent
previous = runpy.run_path(str(BASE / 'analyze-commercial-observation-087.py'))
if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in previous['SCRIPTS']
    if sys.argv[1] == 'secrecy':
        runpy.run_path(str(BASE / 'commercial-workflow-108.py'))['configure_local_transport']()
    source = previous['source087'](sys.argv[1]).replace('commercial61-native-087', 'commercial61-native-108')
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
