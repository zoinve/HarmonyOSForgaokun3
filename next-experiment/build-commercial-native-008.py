"""Alias already-visible /system inside commercial sandboxes; keep original grants."""
from pathlib import Path
import runpy, subprocess
base = Path(__file__).resolve().parent
p = runpy.run_path(str(base/'build-commercial-native-007.py'))
anchor = '    const char *options="lowerdir=/system,upperdir=/run/commercial-system005/upper,workdir=/run/commercial-system005/work";'
assert p['inner'].count(anchor) == 1
extra = r'''
    directory("/run/commercial-system005/upper/etc/sandbox",0755);
    commercial_copy005("/sandbox-system008.json","/run/commercial-system005/upper/etc/sandbox/system-sandbox.json",0644);
    commercial_copy005("/sandbox-chipset008.json","/run/commercial-system005/upper/etc/sandbox/chipset-sandbox.json",0644);
    /* Original sandbox code creates no parent directories for symbol-links. */
    directory("/mnt/sandbox",0755);
    directory("/mnt/sandbox/system",0755);directory("/mnt/sandbox/system/usr",0755);
    directory("/mnt/sandbox/chipset",0755);directory("/mnt/sandbox/chipset/usr",0755);
    dprintf(1,"COMMERCIAL008_ALIAS existing_system_view_only=1 additional_mounts=0 original_service_identity=1\n");
'''
inner = p['inner'].replace(anchor, extra+anchor, 1)
outer = p['outer'].replace('commercial61-native-007-%s','commercial61-native-008-%s').replace('COMMERCIAL007','COMMERCIAL008')
assert outer.count('left033=420') == 1 and outer.count('elapsed033<240') == 1
outer = outer.replace('left033=420','left033=210').replace('elapsed033<240','elapsed033<90').replace('budget_seconds=240','budget_seconds=90')
payload = p['payload'].replace('inner='+repr(p['inner']), 'inner='+repr(inner), 1).replace('outer='+repr(p['outer']), 'outer='+repr(outer), 1)
payload = payload.replace('commercial61-native-007','commercial61-native-008').replace('outer_deadline_seconds=420,target_budget_seconds=240','outer_deadline_seconds=210,target_budget_seconds=90')
addition = r'''
import runpy
repair=runpy.run_path(str(base/'commercial-sandbox-008.py'))['repair']
for kind in ['system','chipset']:
 source='/system/etc/sandbox/'+kind+'-sandbox.json'
 original_json=subprocess.check_output(['debugfs','-R','cat '+source,str(original)],stderr=subprocess.DEVNULL)
 before=json.loads(original_json);after=repair(before)
 data=json.dumps(after,indent=2).encode()+b'\n'
 entries['native-target/sandbox-'+kind+'008.json']=(stat.S_IFREG|0o444,data)
 (local/('original-'+kind+'-sandbox.json')).open('xb').write(original_json)
 (local/('alias-'+kind+'-sandbox.json')).open('xb').write(data)
'''
assert payload.count('def member(') == 1
payload = payload.replace('def member(', addition+'\ndef member(', 1)
if __name__ == '__main__': raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
