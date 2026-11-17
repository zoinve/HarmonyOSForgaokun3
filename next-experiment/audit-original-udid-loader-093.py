"""Read original ELF dependency/symbol ownership; never execute target code."""
from pathlib import Path
import hashlib
import json
import posixpath
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
IMAGE = '/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img'


def main():
    out = ROOT/'reports/original-udid-loader-audit-093-r2'
    assert not out.exists()
    out.mkdir()
    paths = ['/system/lib64/init/libudidmodule.z.so', '/system/bin/init',
             '/system/lib64/chipset-sdk-sp/libbegetutil.z.so', '/system/lib64/libinit_module_engine.so',
             '/system/lib64/chipset-sdk/libmbedtls.z.so', '/system/lib64/chipset-pub-sdk/libsec_shared.z.so']
    records = []
    for index, initial in enumerate(paths):
        path = initial
        links = []
        for _ in range(8):
            status = subprocess.run(['debugfs', '-R', 'stat '+path, IMAGE], capture_output=True, check=True)
            stat = status.stdout.decode()
            assert 'Inode:' in stat, (path, status.stderr.decode())
            target = re.search(r'Fast link dest: "([^"]+)"', stat)
            if not target:
                assert 'Type: regular' in stat, (path, stat)
                break
            links.append(dict(path=path, target=target[1]))
            path = posixpath.normpath(posixpath.join(posixpath.dirname(path), target[1]))
        else:
            raise AssertionError('bounded original symlink resolution')
        body = subprocess.run(['debugfs', '-R', 'cat '+path, IMAGE], capture_output=True, check=True).stdout
        assert body.startswith(b'\x7fELF'), path
        saved = f'{index:02d}-'+Path(path).name
        binary = out/saved
        binary.open('xb').write(body)
        dynamic = subprocess.check_output(['readelf', '-dW', str(binary)], text=True)
        symbols = subprocess.check_output(['readelf', '--dyn-syms', '-W', str(binary)], text=True)
        (out/(saved+'.dynamic.txt')).open('x').write(dynamic)
        (out/(saved+'.symbols.txt')).open('x').write(symbols)
        owned = {}
        for line in symbols.splitlines():
            columns = line.split()
            if len(columns) >= 8 and columns[0].rstrip(':').isdigit():
                owned[columns[7].split('@')[0]] = columns[6] != 'UND'
        records.append(dict(requested=initial, resolved=path, links=links, bytes=len(body),
            sha256=hashlib.sha256(body).hexdigest(), saved_as=saved,
            needed=re.findall(r'Shared library: \[([^]]+)\]', dynamic),
            identity_symbols={key: owned.get(key) for key in ('SystemReadParam', 'SystemWriteParam', 'StartupLog',
                'GetParameter', 'SetParameter', 'GetDevUdid', 'InitModuleMgrInstall', 'InitAddPreCfgLoadHook')}))
    module, init, client, engine = records[:4]
    assert module['sha256'] == '322f5cf59d309e4306e59bf47c11e01748c26d1039492c6e05e9afebe8f9e11c'
    repo = ROOT/'references/OpenHarmony-startup-init-6.0-audit090'
    commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    assert commit == 'd6b79e48ac513d1737dd878b53311aa629bc81dc'
    source = subprocess.check_output(['git', '-C', str(repo), 'show', commit+':services/modules/udid/udid_static.c'])
    (out/'udid_static.c').open('xb').write(source)
    result = dict(original_elf_records=records,
        original_module_imports_server_write=module['identity_symbols']['SystemWriteParam'] is False,
        original_init_exports_server_write=init['identity_symbols']['SystemWriteParam'] is True,
        client_exports_server_write=client['identity_symbols']['SystemWriteParam'] is True,
        engine_exports_server_write=engine['identity_symbols']['SystemWriteParam'] is True,
        engine_is_original_empty_stub_link=engine['resolved'].endswith('/libinit_stub_empty.so'),
        upstream_hook=dict(commit=commit, path='services/modules/udid/udid_static.c',
            sha256=hashlib.sha256(source).hexdigest(), uses_original_precfg_hook=b'InitAddPreCfgLoadHook(0, UDidCalc)' in source),
        exact_092_dlerror_not_captured=True, public_source_not_full_private_binary_equivalence=True,
        first_attempt_preserved='reports/original-udid-loader-audit-093',
        first_attempt_failure='top-level libmbedtls path absent; actual dependency is in chipset-sdk',
        target_elf_executed=False, original_images_written=False, identities_or_provisioning_modified=False)
    (out/'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
