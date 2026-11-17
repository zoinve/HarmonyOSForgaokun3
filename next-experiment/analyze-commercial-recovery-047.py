"""Summarize recovered startup evidence without inferring an unobserved panic."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-047'


def main():
    recovered = ROOT / 'recovered-evidence'
    manifest = json.loads((recovered / 'recovery-manifest.json').read_text())
    for name, row in manifest['files'].items():
        data = (recovered / 'raw' / name).read_bytes()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    phase = (recovered / 'raw/phase-040.log').read_text(errors='replace')
    hilog = (recovered / 'raw/interactive-hilog030.log').read_text(errors='replace')
    faults = (recovered / 'raw/interactive-faults030.log').read_text(errors='replace')
    stamps = re.findall(r'01-01 (\d\d:\d\d:\d\d\.\d+)', hilog)
    result = dict(recovered_files=len(manifest['files']),
                  journal_replayed_on_copy_only=manifest['journal_replayed_on_copy_only'],
                  original_superblock_unchanged=manifest['original_superblock_unchanged'],
                  original_handoff='COMMERCIAL001_HANDOFF' in phase,
                  original_samples=re.findall(r'NATIVE_ORIGINAL_SAMPLE [^\n]+', phase),
                  trace_markers=re.findall(r'COMMERCIAL047_TRACE[^\n]+', phase),
                  normal_target_exit_observed='COMMERCIAL047 target_timeout=1' in phase,
                  final_hilog_stamp=stamps[-1] if stamps else None,
                  first_arkui_flush_observed='ArkUi flush first frame messages.' in hilog,
                  egl_swap_entry_observed='EGL031 stage=eglSwapBuffers-entry' in hilog,
                  egl_swap_exit_observed='EGL031 stage=eglSwapBuffers-exit' in hilog,
                  kernel_panic_observed=bool(re.search(r'Kernel panic|BUG:|Oops:', faults)),
                  zero_bytes={name: (recovered / 'raw' / name).read_bytes().count(b'\0')
                              for name in ['phase-040.log', 'interactive-hilog030.log', 'interactive-faults030.log']},
                  source_phase='phase-040.log', absence_does_not_prove_nonexecution=True,
                  actual_desktop_verified=False)
    (ROOT / 'recovery-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
