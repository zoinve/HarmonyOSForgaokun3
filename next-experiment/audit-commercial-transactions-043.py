"""Read-only original ELF audit and hash-checked analysis of completed run 042."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'reports/commercial-transaction-audit-043'
IMAGE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')


def main():
    assert not OUT.exists(), 'Never overwrite numbered evidence'
    evidence = BASE / 'reports/commercial61-native-042/runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        blob = (evidence / 'raw' / name).read_bytes()
        assert len(blob) == item['bytes']
        assert hashlib.sha256(blob).hexdigest() == item['sha256']
    text = (evidence / 'raw/interactive-hilog030.log').read_text(errors='replace')
    pattern = re.compile(r'RS042 stage=(\w+) pid=(\d+) uid=(\d+) object=(\S+) value=(\d+) mono_us=(\d+)')
    records = [dict(stage=m[1], pid=int(m[2]), uid=int(m[3]), object=m[4],
                    value=int(m[5]), mono_us=int(m[6])) for m in pattern.finditer(text)]
    OUT.mkdir()
    libraries = []
    for name in ['librender_service_base.z.so', 'librender_service_client.z.so']:
        origin = '/system/lib64/' + name
        result = subprocess.run(['debugfs', '-R', 'cat ' + origin, str(IMAGE)],
                                capture_output=True, check=True)
        assert result.stdout.startswith(b'\x7fELF'), origin
        path = OUT / name
        path.write_bytes(result.stdout)
        symbols = subprocess.check_output(['aarch64-linux-gnu-nm', '-D', '--defined-only', str(path)], text=True)
        (OUT / (name + '.symbols.txt')).write_text(symbols)
        selected = []
        for line in symbols.splitlines():
            fields = line.split()
            if len(fields) < 3:
                continue
            symbol = fields[-1]
            if any(word in symbol for word in ['FlushImplicitTransaction', 'CommitTransaction',
                                               'RegisterApplicationAgent', 'SendTransaction',
                                               'SetRenderThreadClient', 'InitRenderThread']):
                selected.append(symbol)
        disassembly = subprocess.check_output(['aarch64-linux-gnu-objdump', '-d', '-C', str(path)], text=True)
        # Preserve only complete named methods relevant to this real integration failure.
        sections = re.split(r'(?=^[0-9a-f]+ <)', disassembly, flags=re.MULTILINE)
        relevant = ''.join(section for section in sections if any(
            word in section.split('\n', 1)[0] for word in
            ['FlushImplicitTransaction', 'CommitTransaction', 'RegisterApplicationAgent',
             'SendTransaction', 'SetRenderThreadClient', 'InitRenderThread']))
        (OUT / (name + '.transactions.asm')).write_text(relevant)
        libraries.append(dict(name=name, image_path=origin, bytes=len(result.stdout),
                              sha256=hashlib.sha256(result.stdout).hexdigest(), methods=selected))
    summary = dict(run=manifest['run'], verified_files=len(manifest['files']),
                   observer_records=len(records), stages=dict(Counter(r['stage'] for r in records)),
                   processes={str(pid): dict(stages=dict(Counter(r['stage'] for r in records if r['pid'] == pid)),
                                            values={stage: sorted({r['value'] for r in records if r['pid'] == pid and r['stage'] == stage})
                                                    for stage in sorted({r['stage'] for r in records if r['pid'] == pid})})
                              for pid in sorted({r['pid'] for r in records})},
                   original_libraries=libraries, images_modified=False, target_boot_repeated=False,
                   no_observed_commit_is_not_proof_of_no_submission=True, desktop_verified=False)
    (OUT / 'records.json').write_text(json.dumps(records, indent=2))
    (OUT / 'result.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
