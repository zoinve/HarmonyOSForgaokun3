from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    runpy.run_path(str(BASE / 'commercial-workflow-108.py'))['configure_local_transport']()
    runpy.run_path(str(BASE / 'retain-latest-experiment-boot-entries-001.py'), run_name='__main__')
