"""Execute the single 124 boot and its immutable retrieval/verification steps."""
from pathlib import Path
import json
import runpy
import sys

BASE=Path(__file__).resolve().parent
configure_local_transport=runpy.run_path(str(BASE/'commercial-workflow-123.py'))['configure_local_transport']
if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ['run-commercial-native','retrieve-commercial-evidence','verify-commercial-return','retain-entries']
    configure_local_transport()
    report=BASE.parent/'reports/commercial61-native-124'
    assert json.loads((report/'admission-test.json').read_text())['exact_full_123_filesystem_match']
    if sys.argv[1]=='retain-entries':
        runpy.run_path(str(BASE/'retain-latest-experiment-boot-entries-001.py'),run_name='__main__')
    else:
        source=(report/(sys.argv[1]+'.generated.py')).read_text()
        exec(compile(source,sys.argv[1],'exec'),{'__name__':'__main__','__file__':str(BASE/(sys.argv[1]+'-124.py'))})
