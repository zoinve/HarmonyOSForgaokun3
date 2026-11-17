"""Require verified current-namespace same-inode fix as well as baseline admission."""
from pathlib import Path
import hashlib
import json
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent


if __name__=='__main__':
    assert sys.argv[1:]==['--loader-test-fix-1'], 'preserve original failed unit-test evidence'
    fixture=json.loads((ROOT/'reports/live-debug-log-fixture-163-compile-fix-1/result.json').read_text())
    assert fixture['inherited_fd_failure_reproduced_and_reopen_fix_verified']
    assert hashlib.sha256((BASE/'live-debug-log-163.h').read_bytes()).hexdigest()==fixture['log_header_sha256']
    source=(BASE/'test-commercial-admission-161.py').read_text()
    for old,new in [('commercial61-native-161','commercial61-native-164'),('build-commercial-native-161.py','build-commercial-native-164.py'),
        ('helper_source161','helper_source164'),('loader161','loader164'),('live-debug-launcher-161','live-debug-launcher-164'),
        ('live-debug161','live-debug164'),("['live161']","['live164']"),('commercial-workflow-161.py','commercial-workflow-164.py'),
        ('source161','source164'),('estimated161','estimated164'),('live-debug-helper-161','live-debug-helper-164'),
        ('test-live-debug-loader-161.py','test-live-debug-loader-164.py')]:
        source=source.replace(old,new)
    source=source.replace("tests=['test-live-debug-loader-164.py',","tests=['test-live-debug-log-163.py','test-live-debug-loader-164.py',",1)
    source=source.replace('all_16_focused_baseline_scripts_pass','all_17_focused_baseline_scripts_pass')
    source=source.replace('    for test in tests:',"    test_report=report/'admission-loader-fix-1'\n    assert not test_report.exists()\n    test_report.mkdir()\n    for test in tests:",1)
    source=source.replace("(report/(test+'.stdout'))","(test_report/(test+'.stdout'))")
    source=source.replace("(report/(test+'.stderr'))","(test_report/(test+'.stderr'))")
    exec(compile(source,'test-commercial-admission-164.generated.py','exec'),{'__name__':'__main__','__file__':str(BASE/'test-commercial-admission-164.generated.py')})
