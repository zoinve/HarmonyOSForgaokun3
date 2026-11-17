"""Execute the already generated475 retrieval using its intended WSL transport."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
if __name__ == '__main__':
    report = BASE.parent / 'reports/commercial61-native-471'
    assert not (report / 'runtime-evidence').exists()
    source = (report / 'retrieve-475.generated.py').read_text()
    runpy.run_path(str(BASE / 'commercial-workflow-235.py'))['configure_local_transport']()
    exec(compile(source, 'resume-cpufreq-retrieval-488.generated.py', 'exec'),
         dict(__name__='__main__', __file__=str(BASE / 'resume-cpufreq-retrieval-488.generated.py')))
