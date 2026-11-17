"""Use original workspace policy with a real app; load own bootstrap into RAM."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shutil
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
WORK = BUILD / 'commercial61-native-087'
REPORT = ROOT / 'reports/commercial61-native-087'
WORKSPACE = {
    'layoutDescription': {'pageCount': 1, 'row': 9, 'column': 15, 'maxPage': 1, 'maxForm': 80},
    'layoutInfo': [dict(container=-101, typeId=0, bundleName='com.huawei.hmos.browser',
                        moduleName='entry', abilityName='MainAbility', column=0, row=0,
                        screen=0, appIndex=0, area=[1, 1])],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_program(name, source):
    (WORK / (name + '.c')).open('x').write(source)
    command = ['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
               str(WORK / (name + '.c')), '-I', str(BASE), '-o', str(WORK / name)]
    if name == 'init':
        command.insert(-2, str(BASE / 'baremetal-diagnostic-core.c'))
    result = subprocess.run(command, capture_output=True)
    for suffix, value in (('stdout', result.stdout), ('stderr', result.stderr)):
        (REPORT / (name + '.' + suffix)).open('xb').write(value)
    assert result.returncode == 0, result.stderr.decode(errors='replace')
    shutil.copyfile(WORK / (name + '.c'), REPORT / (name + '.c'))


def member(name, mode, body, inode):
    name = name.encode() + b'\0'
    values = [inode, mode, 0, 0, 1, 0, len(body), 0, 0, 0, 0, len(name), 0]
    output = b'070701' + b''.join(f'{value:08x}'.encode() for value in values) + name
    output += b'\0' * (-len(output) % 4)
    output += body
    return output + b'\0' * (-len(output) % 4)


def main():
    assert not WORK.exists() and not REPORT.exists()
    WORK.mkdir()
    REPORT.mkdir()
    previous = runpy.run_path(str(BASE / 'build-commercial-native-086.py'))
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    old = {name: (mode, body) for name, mode, body in parse(gzip.decompress((BUILD / 'commercial61-native-086/initrd.img').read_bytes()))}
    workspace = json.dumps(WORKSPACE, separators=(',', ':')).encode() + b'\n'
    workspace_hash = hashlib.sha256(workspace).hexdigest()
    inner = previous['inner']
    anchor = '    commercial_system016();\n    const char *options="lowerdir=/system,'
    assert inner.count(anchor) == 1
    addition = '''    const char workspace087[] = WORKSPACE_LITERAL;
    const char *path087="/run/commercial-system005/upper/etc/hw_launcher_default_workspace.json";
    int fd087=open(path087,O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0644);
    if(fd087<0 || write(fd087,workspace087,sizeof(workspace087)-1)!=(ssize_t)(sizeof(workspace087)-1) || close(fd087))
        fail("volatile product workspace 087");
    dprintf(1,"COMMERCIAL087_WORKSPACE path=/system/etc/hw_launcher_default_workspace.json bytes=%zu sha256=WORKSPACE_HASH original_hap_unchanged=1 activation_state_unchanged=1\\n",sizeof(workspace087)-1);
'''.replace('WORKSPACE_LITERAL', json.dumps(workspace.decode())).replace('WORKSPACE_HASH', workspace_hash)
    inner = inner.replace(anchor, addition + anchor, 1)
    compile_program('bootstrap-runtime087', inner)
    runtime_hash = sha(WORK / 'bootstrap-runtime087')
    outer = previous['outer'].replace('commercial61-native-086', 'commercial61-native-087').replace('COMMERCIAL086', 'COMMERCIAL087')
    source = '/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-087/bootstrap-runtime087'
    destination = '/native-target/bootstrap'
    shell = (f'test -f {source} && test ! -L {source} && test -f {destination} && test ! -L {destination} && '
             f'test "$(/bin/busybox sha256sum {source})" = "{runtime_hash}  {source}" && '
             f'/bin/busybox cp {source} {destination} && /bin/busybox chmod 0755 {destination} && '
             f'test "$(/bin/busybox sha256sum {destination})" = "{runtime_hash}  {destination}" && '
             'echo COMMERCIAL087_RUNTIME_BOOTSTRAP_VERIFIED_RAM_ONLY')
    load = ('    if(okay){\n        char *load087[]={"/bin/busybox","sh","-c",' + json.dumps(shell) + ',NULL};\n'
            '        if(probe("workspace-bootstrap-load087",load087,8))okay=0;\n    }\n\n')
    anchor = '    if(okay){\n\n        char memory010[8192];'
    assert outer.count(anchor) == 1
    outer = outer.replace(anchor, load + anchor, 1)
    compile_program('init', outer)
    shutil.copyfile(BUILD / 'commercial61-native-086/bootstrap', WORK / 'bootstrap')
    shutil.copyfile(BUILD / 'commercial61-native-086/bootstrap.c', WORK / 'bootstrap.c')
    shutil.copyfile(WORK / 'bootstrap.c', REPORT / 'bootstrap.c')
    entries = dict(old)
    entries['init'] = (old['init'][0], (WORK / 'init').read_bytes())
    raw = b''.join(member(name, mode, body, index + 1)
                   for index, (name, (mode, body)) in enumerate(entries.items()))
    raw += member('TRAILER!!!', 0, b'', len(entries) + 1)
    (WORK / 'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    assert {name for name in old if old[name] != entries[name]} == {'init'}
    (REPORT / 'workspace.json').open('xb').write(workspace)
    provenance = dict(workspace_sha256=workspace_hash, runtime_bootstrap_sha256=runtime_hash,
                      runtime_bootstrap_bytes=(WORK / 'bootstrap-runtime087').stat().st_size,
                      runtime_source_sha256=sha(WORK / 'bootstrap-runtime087.c'),
                      full_archive_changed_members=['init'], original_hap_modified=False,
                      original_images_modified=False, oobe_state_modified=False,
                      package_metadata_fabricated=False, init_service_permissions_unchanged=True,
                      ram_only_workspace=True, runtime_bootstrap_source=source,
                      bootstrap_loaded_from_readonly_ubuntu=True, diagnostic_layout_tool_unchanged=True,
                      original_network_helpers_unchanged=True, runtime_verified=False)
    (REPORT / 'workspace-provenance.json').open('x').write(json.dumps(provenance, indent=2))
    result = json.loads((ROOT / 'reports/commercial61-native-086/result.json').read_text())
    names = ['init', 'bootstrap', 'init.c', 'bootstrap.c', 'initrd.img', 'bootstrap-runtime087', 'bootstrap-runtime087.c']
    result['artifacts'] = [dict(name=name, bytes=(WORK / name).stat().st_size, sha256=sha(WORK / name)) for name in names]
    result['external_runtime_bootstrap'] = provenance
    result['runtime_verified'] = False
    for directory in (WORK, REPORT):
        (directory / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(runtime_bootstrap_sha256=runtime_hash, archive_delta=['init']), indent=2))


if __name__ == '__main__':
    main()
