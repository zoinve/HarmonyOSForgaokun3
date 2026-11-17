from pathlib import Path
import runpy

workflow = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-043.py')))
source = workflow['source043']('analyze-commercial-minimal')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
