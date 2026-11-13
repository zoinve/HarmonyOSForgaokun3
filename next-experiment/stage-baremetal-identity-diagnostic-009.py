"""Stage only fresh 009 lab assets and verify actual ARM64 non-PID1 refusal."""
from pathlib import Path

source=Path(__file__).with_name('stage-baremetal-identity-diagnostic-008.py').read_text()
for old,new in [('baremetal-identity-diagnostic-008','baremetal-identity-diagnostic-009'),('native-identity-diagnostic-008','native-identity-diagnostic-009'),('baremetal-diagnostic-init-008','baremetal-diagnostic-init-009'),('baremetal-identity-native-package-001','baremetal-identity-native-package-002'),('baremetal-identity-native-read-009/sdk/native-probe','baremetal-native-identity-qemu-047/probe'),('native-identity-read-001','native-identity-read-002')]:
    assert old in source,old
    source=source.replace(old,new)
exec(compile(source,'stage009-generated','exec'),{'__file__':__file__,'__name__':__name__})
