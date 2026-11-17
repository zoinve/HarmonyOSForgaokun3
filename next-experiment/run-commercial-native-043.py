from pathlib import Path
import runpy

workflow = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-043.py')))
source = workflow['source043']('run-commercial-native')
if __name__ == '__main__':
    workflow['configure_local_transport']()
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
