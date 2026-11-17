"""Verify immutable 136 evidence and distinguish enumeration from acceptance."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]


def summarize(text):
    results = [dict(module=m, status=int(s)) for m, s in re.findall(
        r'^MEDIA136_MODULE_RESULT module=(\w+) status=(\d+) binding_not_inferred=1$', text, re.M)]
    files = []
    pattern = (r'^MEDIA136_FILE_BEGIN stage=(\w+) path=(\S+) limit=(\d+)\n'
               r'(.*?)\nMEDIA136_FILE_END stage=\1 path=\2 bytes=(\d+) eof=([01]) errno=(\d+)$')
    for match in re.finditer(pattern, text, re.M | re.S):
        stage, path, limit, content, count, eof, error = match.groups()
        files.append(dict(stage=stage, path=path, content=content.strip(), bytes=int(count),
                          limit=int(limit), eof=eof == '1', errno=int(error)))
    states = [dict(stage=s, mono_ms=int(t), node=n, state=v) for s, t, n, v in re.findall(
        r'^GAOKUN_DRIVER133 stage=(\w+) mono_ms=(\d+) path=/sys/class/remoteproc/(remoteproc\d+) attr=state valid=1 value=(\w+)$', text, re.M)]
    nodes = [dict(stage=s, name=n, uid=int(u), gid=int(g), mode=m, major=int(a), minor=int(b))
             for s, n, u, g, m, a, b in re.findall(
                 r'^MEDIA136_SOUND_NODE stage=(\w+) name=(\S+) uid=(\d+) gid=(\d+) mode=(\d+) major=(\d+) minor=(\d+)$', text, re.M)]
    cards = [r for r in files if r['path'] == '/proc/asound/cards']
    pcm = [r for r in files if r['path'] == '/proc/asound/pcm']
    return dict(module_results=results, file_samples=files, remoteproc_states=states, sound_nodes=nodes,
                alsa_card_observed=any(re.search(r'^\s*\d+\s+\[', r['content'], re.M) for r in cards),
                alsa_pcm_observed=any(re.search(r'^\d+-\d+:', r['content'], re.M) for r in pcm),
                hci_class_observed=bool(re.search(r'^MEDIA136_CLASS_ENTRY .*path=/sys/class/bluetooth/hci\d+ ', text, re.M)),
                audio_playback_verified=False, native_audio_hdi_verified=False,
                bluetooth_initialization_verified=False, bluetooth_pairing_verified=False,
                observation_is_not_functional_acceptance=True)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-136'
    evidence = report / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], name
    phase = max((name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name)),
                key=lambda name: int(name[6:-4]))
    text = (evidence / 'raw' / phase).read_bytes().decode('utf-8', errors='replace')
    result = summarize(text)
    assert len(result['module_results']) == 18
    assert result['file_samples'] and result['remoteproc_states']
    baseline = runpy.run_path(str(ROOT / 'next-experiment/analyze-native-drivers-133.py'))['summarize']
    driver = baseline(text, (evidence / 'raw/interactive-hilog030.log').read_bytes().decode('utf-8', errors='replace'))
    result.update(phase_file=phase, phase_sha256=manifest['files'][phase]['sha256'],
                  verified_evidence_files=len(manifest['files']),
                  baseline_battery_consumption_observed=driver['genuine_battery_consumption_observed'],
                  baseline_backlight_correlated=driver['backlight_hardware_readback_correlated'])
    (report / 'media-runtime-analysis-138.json').open('x').write(json.dumps(result, indent=2))
    (report / 'driver-runtime-analysis-138.json').open('x').write(json.dumps(driver, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in
                     ['file_samples', 'remoteproc_states', 'sound_nodes']}, indent=2))
