from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
if __name__ == '__main__':
    workflow = runpy.run_path(str(base/'commercial-workflow-091.py'))
    workflow['configure_local_transport']()
    runpy.run_path(str(base/'retain-latest-experiment-boot-entries-001.py'), run_name='__main__')
