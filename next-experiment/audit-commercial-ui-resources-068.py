"""Read-only check of the exact original UI resource inputs seen in logs."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

b = Path(__file__).resolve().parent
out = b.parent / 'reports/commercial-ui-resources-audit-068'
image = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
paths = ['/system/app/SystemResources/SystemResources.hap',
         '/system/app/SystemResources/SystemResourcesExt.hap',
         '/system/app/HwStartupGuide/HwStartupGuide.hap',
         '/system/app/SceneBoard/SceneBoard_EngineService.hap']
expected = ['welcome_land_one.mp4', 'welcome_land_two.mp4',
            'quick_setup_animate_pc.json', 'set_language_animage.json',
            'setting_up_system_animage.json', 'connecting_to_network_animage.json',
            'language_animation.json', 'basic_statement_cn.json']
out.mkdir()
rows = []
for path in paths:
    result = subprocess.run(['debugfs', '-R', 'cat '+path, str(image)], capture_output=True, check=True)
    data = result.stdout
    assert data and data.startswith(b'PK'), (path, result.stderr)
    target = out / Path(path).name
    target.open('xb').write(data)
    with zipfile.ZipFile(target) as archive:
        error = None
        bad = None
        try:
            bad = archive.testzip()
        except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
            error = str(exc)
        names = archive.namelist()
        metadata = {}
        indexes = []
        for name in names:
            if name == 'module.json' or name.endswith('/resources.index') or name == 'resources.index':
                try:
                    member = archive.read(name)
                    if name == 'module.json':
                        metadata = json.loads(member)
                    else:
                        indexes.append(dict(name=name, bytes=len(member),
                            sha256=hashlib.sha256(member).hexdigest(), prefix_hex=member[:64].hex()))
                except (zipfile.BadZipFile, RuntimeError, OSError, ValueError) as exc:
                    indexes.append(dict(name=name, error=str(exc)))
        rows.append(dict(original_path=path, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
            zip_crc_valid=bad is None and error is None, first_bad_crc_member=bad,
            zip_error=error, entries=len(names), module=metadata, resource_indexes=indexes,
            expected_assets={leaf:[n for n in names if n.endswith('/'+leaf) or n==leaf] for leaf in expected},
            rawfile_names=[n for n in names if '/rawfile/' in n]))
manifest = dict(original_image=str(image), files=rows, original_image_written=False,
                cryptographic_signatures_verified=False, operational_boot_performed=False,
                missing_file_alone_not_root_cause=True)
with (out / 'result.json').open('x') as f:
    json.dump(manifest, f, indent=2)
print(json.dumps({**manifest, 'files':[{k:v for k,v in row.items() if k not in (
    'module','rawfile_names')} for row in rows]}, indent=2))
