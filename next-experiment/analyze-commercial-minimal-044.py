from pathlib import Path
import runpy
w = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-044.py')))
source = w['source044']('analyze-commercial-minimal')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
