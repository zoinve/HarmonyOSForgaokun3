"""Original iw PHY migration, preserving the target network namespace."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-081.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-081', 'commercial61-native-082').replace('COMMERCIAL081', 'COMMERCIAL082')
anchor = '        if(child>0){\n            for(unsigned i=0;i<14;++i){'
assert outer.count(anchor) == 1
replacement = r'''
        if(child>0){
            char pid082[32];
            snprintf(pid082, sizeof(pid082), "%d", child);
            char *move082[] = {"/network082/lib/ld-linux-aarch64.so.1", "--library-path",
                "/network082/usr/lib/aarch64-linux-gnu", "/network082/usr/sbin/iw",
                "phy", "phy0", "set", "netns", pid082, NULL};
            int moved082 = probe("wifi-namespace-move082", move082, 8);
            dprintf(1, "NETWORK082_PHY_MIGRATION status=%d association_requested=0\n", moved082);
            if (!moved082) {
                char *observe082[] = {"/network082/namespace-observe", pid082, NULL};
                (void)probe("wifi-target-observe082", observe082, 8);
            }
            network081_netifs();
            for(unsigned i=0;i<14;++i){'''
outer = outer.replace(anchor, replacement, 1)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace(
    'commercial61-native-081', 'commercial61-native-082')
addition = r'''
iw082=root/'native-iw-082'
record082=json.loads((iw082/'result.json').read_text())
assert record082['credentials_read'] is False and record082['ubuntu_network_modified'] is False
for row082 in record082['files']:
 path082=Path(row082['path'])
 assert path082.is_absolute() and '..' not in path082.parts
 name082='network082/'+str(path082).lstrip('/')
 body082=(iw082/str(path082).lstrip('/')).read_bytes()
 assert hashlib.sha256(body082).hexdigest()==row082['sha256']
 assert len(body082)==row082['bytes']
 assert name082 not in entries
 for parent082 in reversed(Path(name082).parents):
  if str(parent082)!='.':entries.setdefault(str(parent082),(stat.S_IFDIR|0o755,b''))
 entries[name082]=(stat.S_IFREG|0o755,body082)
helper082=base/'network-namespace-observe-082.c'
helperout082=work/'namespace-observe'
cmd082=['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(helper082),'-o',str(helperout082)]
r082=subprocess.run(cmd082,capture_output=True)
(local/'namespace-observe-build.stdout').open('xb').write(r082.stdout)
(local/'namespace-observe-build.stderr').open('xb').write(r082.stderr)
assert r082.returncode==0,r082.stderr.decode()
entries['network082/namespace-observe']=(stat.S_IFREG|0o755,helperout082.read_bytes())
shutil.copyfile(helper082,local/'namespace-observe.c')
record082.update(helper_source_sha256=sha(helper082),helper_sha256=sha(helperout082),
 target_namespace_preserved=True,association_requested=False,original_images_written=False)
(local/'iw-provenance.json').open('x').write(json.dumps(record082,indent=2))
'''
anchor = 'def member(name,mode,data,ino):'
assert payload.count(anchor) == 1
payload = payload.replace(anchor, addition + '\n' + anchor, 1)

if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
