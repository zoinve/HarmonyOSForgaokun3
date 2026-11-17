from pathlib import Path
import runpy

b=Path(__file__).resolve().parent
if __name__=='__main__':
    w=runpy.run_path(str(b/'commercial-workflow-070.py'))
    w['configure_local_transport']()
    runpy.run_path(str(b/'retain-latest-experiment-boot-entries-001.py'),run_name='__main__')
