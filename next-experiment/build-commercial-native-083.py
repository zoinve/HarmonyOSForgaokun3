"""Real supplicant and scan through the existing bridge's control path."""
from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-082.py'))
inner = p['inner']
package = json.loads((b.parent / 'reports/commercial-network-inputs-audit-083/package.json').read_text())
installed = json.loads((b.parent / 'reports/commercial-network-inputs-audit-083/tool-installation.json').read_text())
assert installed['sha256'] == package['sha256'] and installed['bytes'] == package['bytes']
assert package['esp_payload'] is False
archive = '/mnt/ubuntu' + package['destination']
load = ('test ! -e /native-target/network083/usr && test ! -e /native-target/network083/lib && '
        'test "$(/bin/busybox sha256sum ' + archive + ')" = "' + package['sha256'] + '  ' + archive + '" && '
        '/bin/busybox tar -xzf ' + archive + ' -C /native-target && '
        'echo NETWORK083_TOOLS_VERIFIED_AND_EXTRACTED_RAM_ONLY')
outer = p['outer'].replace('commercial61-native-082', 'commercial61-native-083').replace('COMMERCIAL082', 'COMMERCIAL083')
anchor = '    if(okay){\n\n        char memory010'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '    if(okay){\n        char *load083[] = {"/bin/busybox", "sh", "-c", ' + json.dumps(load) + ', NULL};\n        if(probe("wifi-tools-load083", load083, 12))okay=0;\n    }\n\n' + anchor, 1)
anchor = 'static void native_original(void)'
function = r'''
static int network083_command(pid_t child, const char *mode)
{
    char pid[32], phase[80];
    snprintf(pid, sizeof(pid), "%d", child);
    snprintf(phase, sizeof(phase), "wifi-supplicant-%s083", mode);
    char *args[] = {"/network083-control", pid, (char *)mode, NULL};
    return probe(phase, args, !strcmp(mode, "start") ? 10 : 5);
}

'''
assert outer.count(anchor) == 1
outer = outer.replace(anchor, function + anchor, 1)
anchor = '            for(unsigned i=0;i<14;++i){'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, '            int started083=0;\n' + anchor, 1)
anchor = '                native_diagnostics(child);hw050_tick(child,0);snapshot();if(got==child)break;sleep(5);'
assert outer.count(anchor) == 1
outer = outer.replace(anchor, r'''
                native_diagnostics(child);hw050_tick(child,0);snapshot();if(got==child)break;
                if(i==2 && !moved082){
                    int start083=network083_command(child,"start");
                    started083=!start083;
                    dprintf(1,"NETWORK083_START_RESULT status=%d credentials_supplied=0 association_requested=0\n",start083);
                    if(started083){
                        (void)network083_command(child,"ping");
                        (void)network083_command(child,"scan");
                    }
                }
                if(i==4 && started083){
                    (void)network083_command(child,"scan_results");
                    (void)network083_command(child,"status");
                    (void)network083_command(child,"log");
                }
                sleep(5);''', 1)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace(
    'commercial61-native-082', 'commercial61-native-083')
addition = r'''
helper083=base/'network-supplicant-083.c'
helperout083=work/'network083-control'
command083=['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(helper083),'-o',str(helperout083)]
r083=subprocess.run(command083,capture_output=True)
(local/'supplicant-helper-build.stdout').open('xb').write(r083.stdout)
(local/'supplicant-helper-build.stderr').open('xb').write(r083.stderr)
assert r083.returncode==0,r083.stderr.decode()
entries['network083-control']=(stat.S_IFREG|0o755,helperout083.read_bytes())
entries['native-target/network083']=(stat.S_IFDIR|0o755,b'')
config083=b'ctrl_interface=DIR=/data/local/tmp/wpa_ctrl GROUP=1010\nupdate_config=0\nap_scan=1\n'
entries['native-target/network083/wpa.conf']=(stat.S_IFREG|0o444,config083)
shutil.copyfile(helper083,local/'network-supplicant.c')
package083=json.loads((base.parent/'reports/commercial-network-inputs-audit-083/package.json').read_text())
package083.update(helper_sha256=sha(helperout083),helper_source_sha256=sha(helper083),
 bootstrap_unchanged=True,original_service_configuration_unchanged=True,credentials_supplied=False,
 association_requested=False,target_pid_namespace_cleanup=True)
(local/'supplicant-provenance.json').open('x').write(json.dumps(package083,indent=2))
'''
anchor = 'def member(name,mode,data,ino):'
assert payload.count(anchor) == 1
payload = payload.replace(anchor, addition + '\n' + anchor, 1)

if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
