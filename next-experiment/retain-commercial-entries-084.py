from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
if __name__ == '__main__':
    workflow = runpy.run_path(str(b / 'commercial-workflow-084.py'))
    workflow['configure_local_transport']()
    runpy.run_path(str(b / 'retain-latest-experiment-boot-entries-001.py'), run_name='__main__')
