"""Resolve actual module dependencies and missing native startup integration."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
WANTED = ['qcom_q6v5_pas', 'qcom_pd_mapper', 'qcom_pdr_msg', 'qcom_glink_smem', 'apr',
          'snd_q6apm', 'q6apm_dai', 'q6apm_lpass_dais', 'q6prm_clocks', 'snd_soc_sc8280xp',
          'snd_soc_wsa883x', 'snd_soc_wcd938x', 'snd_soc_wcd938x_sdw',
          'snd_soc_lpass_va_macro', 'snd_soc_lpass_rx_macro', 'snd_soc_lpass_tx_macro',
          'snd_soc_lpass_wsa_macro', 'soundwire_qcom', 'hci_uart', 'btqca']


if __name__ == '__main__':
    report = ROOT / 'reports/audio-bluetooth-payload-135'
    assert not report.exists()
    host_reports = sorted((ROOT / 'reports').glob('audio-bluetooth-inputs-134-*/result.json'))
    assert len(host_reports) == 1
    host_bytes = host_reports[0].read_bytes()
    host = json.loads(host_bytes)
    # /proc/modules lists reverse users, not direct dependencies. Preserve the
    # first collection and correct its field label in this derived evidence.
    normalized = []
    for row in host['selected_modules']:
        row = dict(row)
        if 'dependencies' in row:
            row['used_by'] = row.pop('dependencies')
        normalized.append(row)
    path = BUILD / 'commercial61-native-133/initrd.img'
    metadata = json.loads((ROOT / 'reports/commercial61-native-133/result.json').read_text())
    expected = next(row['sha256'] for row in metadata['artifacts'] if row['name'] == 'initrd.img')
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    members = {name: data for name, _, data in parse(gzip.decompress(raw))}
    modules = {}
    with tempfile.TemporaryDirectory(prefix='audio135-modinfo-') as temporary:
        for wanted in WANTED:
            candidates = [(name, data) for name, data in members.items()
                          if name.endswith('.ko') and Path(name).stem.replace('-', '_') == wanted]
            assert len(candidates) <= 1, (wanted, [name for name, _ in candidates])
            if not candidates:
                modules[wanted] = dict(packaged=False)
                continue
            name, data = candidates[0]
            local = Path(temporary) / Path(name).name
            local.write_bytes(data)
            fields = {}
            for field in ['name', 'depends', 'vermagic', 'firmware']:
                value = subprocess.check_output(['modinfo', '-F', field, str(local)], text=True).strip()
                fields[field] = value.splitlines() if field == 'firmware' else value
            assert fields['name'] == wanted
            modules[wanted] = dict(packaged=True, path=name, sha256=hashlib.sha256(data).hexdigest(), **fields)
    firmware = {}
    for processor in host['remoteproc']:
        requested = processor['firmware']
        candidates = [(name, data) for name, data in members.items() if name.endswith('/' + requested)]
        firmware[processor['name']] = dict(requested=requested, packaged=bool(candidates),
            files=[dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()) for name, data in candidates])
    runtime = ROOT / 'reports/commercial61-native-133/runtime-evidence'
    manifest = json.loads((runtime / 'retrieval-manifest.json').read_text())
    phase_name = json.loads((ROOT / 'reports/commercial61-native-133/driver-runtime-analysis.json').read_text())['phase_file']
    phase = (runtime / 'raw' / phase_name).read_bytes()
    assert hashlib.sha256(phase).hexdigest() == manifest['files'][phase_name]['sha256']
    text = phase.decode('utf-8', errors='replace')
    import re
    loaded = set(re.findall(r'^([A-Za-z0-9_]+) \d+ \d+ \S+ Live ', text, flags=re.M))
    assert loaded, 'native loaded-module snapshot must be present'
    native = {name: dict(packaged=modules[name]['packaged'], loaded_in_recorded_guest=name in loaded,
                        explicit_probe_present='PHASE_BEGIN ' + name + '\n' in text) for name in WANTED}
    result = dict(host_report=str(host_reports[0].relative_to(ROOT)), host_report_sha256=hashlib.sha256(host_bytes).hexdigest(),
                  host_context='Ubuntu enumeration, not native HDI acceptance',
                  proc_modules_used_by_label_corrected=True, normalized_host_selected_modules=normalized,
                  direct_dependencies_source='modinfo depends from exact packaged kernel modules',
                  native_initrd_sha256=expected, native_phase_sha256=manifest['files'][phase_name]['sha256'],
                  load_observation_scope='exported kernel module snapshots, not proof of every later service action',
                  native_modules=modules, remoteproc_firmware=firmware, native_load_observation=native,
                  alsa_playback_verified=False, native_audio_hdi_verified=False,
                  bluetooth_controller_initialized_in_native_guest=False,
                  bluetooth_pairing_verified=False, target_state_modified=False)
    report.mkdir()
    (report / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(native_load_observation=native, remoteproc_firmware=firmware,
                         direct_dependencies={name: row.get('depends') for name, row in modules.items()}), indent=2))
