from pathlib import Path
import runpy

w = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-061.py')))
if __name__ == '__main__':
    w['configure_local_transport']()
    exec(compile(w['source061']('run-commercial-native'), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
