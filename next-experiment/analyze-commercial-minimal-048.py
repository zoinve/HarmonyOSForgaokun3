from pathlib import Path
import runpy
w = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-048.py')))
source = w['source048']('analyze-commercial-minimal')
if __name__ == '__main__':
    w['configure_local_transport']()
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
