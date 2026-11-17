"""Original mapper directory with own GPU providers; restored screen-off policy."""
from pathlib import Path
import inspect,runpy
source=runpy.run_path(str(Path(__file__).with_name('install-commercial-native-022.py')))['source']
source=source.replace('commercial61-native-022','commercial61-native-023').replace('Original SceneBoard resource mounts 022','Original mapper visibility 023')
source=source.replace("=='disabled'","=='enabled'").replace("=='inactive'","=='active'")
source=source.replace('timer_disabled=True','timer_enabled=True')
source=source.replace('installation-192-resume.','installation.')
# Retain the failed preflight's empty directory and logs; use fresh staging.
source=source.replace("lab/commercial61-native-023')","lab/commercial61-native-023-deploy-002')")
source=source.replace("report/'installation.stdout'","report/'installation-deploy-002.stdout'").replace("report/'installation.stderr'","report/'installation-deploy-002.stderr'")
guard="assert ('Default Entry: '+default) in status and ('Current Entry: '+default) in status and 'OneShot Entry:' not in status"
validate=runpy.run_path(str(Path(__file__).with_name('commercial-host-023.py')))['validate']
replacement=inspect.getsource(validate)+'''\nvalidate(dict(status=status,
 boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 release=subprocess.check_output(['uname','-r'],text=True).strip(),
 root_uuid=subprocess.check_output(['findmnt','-n','-o','UUID','/'],text=True).strip(),
 os_id=dict(line.split('=',1) for line in Path('/etc/os-release').read_text().splitlines() if '=' in line)['ID'].strip('"'),
 entry_sha256=sha(esp/'loader/entries/ego-s4diag-20261113.conf')))'''
assert source.count(guard)==1
source=source.replace(guard,replacement,1)
if __name__=='__main__':exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
