"""Associate with the existing real Wi-Fi and observe unchanged native networking."""
from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-083.py'))
inner = p['inner']
connection = json.loads((b.parent / 'reports/commercial-network-inputs-audit-084/connection-ready.json').read_text())
assert connection['configuration_ready'] and not connection['credential_exported']
assert connection['file_mode'] == '0o400' and connection['parent_mode'] == '0o700'
path = '/mnt/ubuntu' + connection['destination']
target = '/native-target/network084/wpa.conf'
load = ('test ! -e ' + target + ' && test "$(/bin/busybox sha256sum ' + path + ')" = "' +
        connection['sha256'] + '  ' + path + '" && /bin/busybox cp ' + path + ' ' + target +
        ' && /bin/busybox chmod 0400 ' + target + ' && echo NETWORK084_PRIVATE_CONFIG_VERIFIED_RAM_ONLY')
outer = p['outer'].replace('commercial61-native-083', 'commercial61-native-084').replace('COMMERCIAL083', 'COMMERCIAL084')
outer = outer.replace('NETWORK083_START_RESULT', 'NETWORK084_START_RESULT').replace(
    'credentials_supplied=0 association_requested=0', 'credentials_supplied=1 association_requested=1')
outer = outer.replace('wifi-supplicant-%s083', 'wifi-supplicant-%s084').replace(
    '"/network083-control", pid,', '"/network084-control", pid,')
anchor = '    if(okay){\n\n        char memory010'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '    if(okay){\n        char *load084[]={"/bin/busybox","sh","-c",' + json.dumps(load) + ',NULL};\n        if(probe("wifi-private-config084",load084,8))okay=0;\n    }\n\n' + anchor, 1)
anchor = '                        (void)network083_command(child,"scan");'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '                        (void)network083_command(child,"status");', 1)
anchor = '                if(i==4 && started083){\n                    (void)network083_command(child,"scan_results");'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '                if((i==4 || i==7 || i==10 || i==13) && started083){\n                    (void)network083_command(child,"network");', 1)
# Preserve the failed-start log too; no diagnostic reads the private configuration.
anchor = '                sleep(5);'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '                if(i==4 && !started083)(void)network083_command(child,"log");\n' + anchor, 1)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace(
    'commercial61-native-083', 'commercial61-native-084')
addition = r'''
helper084=runpy.run_path(str(base/'commercial-network-helper-084.py'))['SOURCE']
helperpath084=work/'network084-control.c'
helperpath084.open('x').write(helper084)
helperout084=work/'network084-control'
cmd084=['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(helperpath084),'-o',str(helperout084)]
r084=subprocess.run(cmd084,capture_output=True)
(local/'association-helper-build.stdout').open('xb').write(r084.stdout)
(local/'association-helper-build.stderr').open('xb').write(r084.stderr)
assert r084.returncode==0,r084.stderr.decode()
entries['network084-control']=(stat.S_IFREG|0o755,helperout084.read_bytes())
entries['native-target/network084']=(stat.S_IFDIR|0o700,b'')
shutil.copyfile(helperpath084,local/'network-association.c')
connection084=json.loads((base.parent/'reports/commercial-network-inputs-audit-084/connection-ready.json').read_text())
connection084.update(helper_sha256=sha(helperout084),helper_source_sha256=sha(helperpath084),
 bootstrap_unchanged=True,original_service_configuration_unchanged=True,credentials_in_initrd=False,
 association_requested=True,original_dhcp_and_netmanager_unchanged=True)
(local/'association-provenance.json').open('x').write(json.dumps(connection084,indent=2))
'''
anchor = 'def member(name,mode,data,ino):'
assert payload.count(anchor) == 1
payload = payload.replace(anchor, addition + '\n' + anchor, 1)

if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
