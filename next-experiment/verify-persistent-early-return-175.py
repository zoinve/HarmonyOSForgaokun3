"""Verify the prior desktop data survived the pre-init protection refusal."""
from pathlib import Path
import json

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/commercial61-native-175-compile-fix-1'

if __name__=='__main__':
    early=json.loads((REPORT/'early-return-inspection.json').read_text())
    assert early['guard_refusal_reasons']==['identity_size_or_readonly_guard']
    assert not any(early[key] for key in ['protection_marker_seen','native_original_start_seen',
                                         'original_init_handoff_seen','persistent_prepare_marker_seen'])
    source=(BASE/'verify-persistent-data-173.py').read_text()
    source=source.replace("REPORT = ROOT / 'reports/commercial61-native-173'",
                          "REPORT = ROOT / 'reports/commercial61-native-175-compile-fix-1'")
    source=source.replace("analysis = json.loads((REPORT / 'persistent-runtime-analysis.json').read_text())",
                          "analysis = json.loads((ROOT / 'reports/commercial61-native-173/persistent-runtime-analysis.json').read_text())")
    source=source.replace("REPORT / 'post-return-verification.json'",
                          "REPORT / 'preservation-difference-inspection-v2.json'")
    source=source.replace("number='173'", "number='175-early'")
    source=source.replace('commercial-workflow-173.py','commercial-workflow-175.py')
    source=source.replace('original_init_handoff_verified=True,full_native_storage_acceptance=True',
                          'original_init_handoff_verified=False,full_native_storage_acceptance=False,previous_desktop_marker_retained=True')
    exec(compile(source,'verify-persistent-early-return-175.generated.py','exec'),
         {'__name__':'__main__','__file__':str(BASE/'verify-persistent-early-return-175.generated.py')})
