"""Correlate config, Dock, lifecycle and guide evidence without claiming pixels."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / 'reports/commercial61-native-087'
    raw = folder / 'runtime-evidence/raw'
    manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
    for name, expected in manifest['files'].items():
        blob = (raw / name).read_bytes()
        assert len(blob) == expected['bytes'] and hashlib.sha256(blob).hexdigest() == expected['sha256']
    phase = max(raw.glob('phase-*.log'), key=lambda path: int(path.stem.split('-')[1]))
    phase_text = phase.read_text(errors='replace')
    hilog = (raw / 'interactive-hilog030.log').read_text(errors='replace')
    provenance = json.loads((folder / 'workspace-provenance.json').read_text())
    marker = ('COMMERCIAL087_WORKSPACE path=/system/etc/hw_launcher_default_workspace.json '
              'bytes=' + str(len((folder / 'workspace.json').read_bytes())) +
              ' sha256=' + provenance['workspace_sha256'] +
              ' original_hap_unchanged=1 activation_state_unchanged=1')
    patterns = {
        'original_config_loader': r'GetLayoutInfoFromConfig:|SmartDockLayoutConfig:|init from config length:',
        'dock_missing_app': r'appDataFromSystem is empty, bundleName:',
        'dock_finished': r'getResidentList send EVENT_SMARTDOCK_INIT_FINISHED',
        'native_freeze': r'THREAD_BLOCK_3S|THREAD_BLOCK_6S|APP_FREEZE|appfreeze_handle',
        'guide_network_timeout': r'InternetManager:wait net validate time out\. jump to wlan page',
        'guide_lifecycle': r'hwstartupguide.*(?:StartProcess|StartAbility|OnStart|onCreate|onDestroy)|(?:StartProcess|StartAbility).*hwstartupguide',
        'layout_permission_denial': r'CheckExtensionAbilityPermission check permission failed|REGISTER_LISTENER_FAILED',
    }
    highlights = {}
    for name, pattern in patterns.items():
        lines = [dict(line=index, text=line) for index, line in enumerate(hilog.splitlines(), 1)
                 if re.search(pattern, line, re.IGNORECASE if name == 'guide_network_timeout' else 0)]
        highlights[name] = dict(count=len(lines), first=lines[:20], last=lines[-20:] if len(lines) > 20 else [])
    pids = sorted({int(match.group(1)) for match in re.finditer(
        r'^\S+\s+\S+\s+(\d+)\s+\d+\s+[A-Z]\s+\S*com\.ohos\.sceneboard/', hilog, re.MULTILINE)})
    result = dict(run=manifest['run'], inherited_network_helper='086', inherited_layout_diagnostic='086',
                  ram_bootstrap_loader_success_marker='COMMERCIAL087_RUNTIME_BOOTSTRAP_VERIFIED_RAM_ONLY' in phase_text,
                  exact_workspace_bootstrap_marker_observed=marker in phase_text,
                  phase_sha256=hashlib.sha256(phase.read_bytes()).hexdigest(),
                  native_hilog_sha256=hashlib.sha256((raw / 'interactive-hilog030.log').read_bytes()).hexdigest(),
                  observed_sceneboard_pids=pids, highlights=highlights,
                  config_consumption_not_inferred_from_creation=True,
                  oobe_completion_proven=False, stable_interactive_desktop_proven=False)
    (folder / 'workspace-runtime-analysis-revision3.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps({key: value for key, value in result.items() if key != 'highlights'}, indent=2))
    print(json.dumps({key: value['count'] for key, value in highlights.items()}, indent=2))


if __name__ == '__main__':
    main()
