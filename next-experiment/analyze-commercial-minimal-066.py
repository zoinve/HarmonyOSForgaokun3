from pathlib import Path
import runpy

w = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-066.py')))
if __name__ == '__main__':
    exec(compile(w['source066']('analyze-commercial-minimal'), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
