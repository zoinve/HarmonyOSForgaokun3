"""Recover additional235 evidence after journal replay, reusing exact members."""
from pathlib import Path
import json
import runpy

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/commercial61-native-235'

if __name__ == '__main__':
    recovery = json.loads((BASE.parent / 'reports/lab-journal-recovery-246/result.json').read_text())
    assert recovery['outer_readonly_fsck_exit'] == 0
    assert recovery['active165_and_candidate197_content_unchanged']
    source = (REPORT / 'readable-retrieval-241.generated.py').read_text()
    old = "dest=root/'runtime-evidence';assert not dest.exists()"
    assert source.count(old) == 1
    source = source.replace(old, "dest=root/'runtime-evidence-recovered-247';assert not dest.exists()", 1)
    source = 'import os\n' + source
    old = "manifest['unreadable_directory_entry_observed']='phase-207.log'"
    assert source.count(old) == 1
    source = source.replace(old, "manifest['prior_unreadable_directory_entry']='phase-207.log'\nmanifest['outer_journal_recovery_verified']=True", 1)
    old = "dest.mkdir();raw=dest/'raw';raw.mkdir()"
    assert source.count(old) == 1
    source = source.replace(old, old + '\nreused=[]', 1)
    old = "  with (raw/name).open('xb') as f:f.write(data)"
    assert source.count(old) == 1
    replacement = """  prior=root/'runtime-evidence/raw'/name
  if prior.is_file() and prior.stat().st_size==len(data) and hashlib.sha256(prior.read_bytes()).hexdigest()==manifest['files'][name]['sha256']:
   os.link(prior,raw/name);reused.append(name)
  else:
   with (raw/name).open('xb') as f:f.write(data)"""
    source = source.replace(old, replacement, 1)
    old = "with (dest/'retrieval-manifest.json').open('x') as f:json.dump(manifest,f,indent=2)"
    assert source.count(old) == 1
    source = source.replace(old, "manifest['reused_exact_member_hardlinks']=reused\n" + old, 1)
    (REPORT / 'recovered-retrieval-247.generated.py').open('x').write(source)
    runpy.run_path(str(BASE / 'commercial-workflow-235.py'))['configure_local_transport']()
    exec(compile(source, 'recovered-retrieval-247', 'exec'),
         {'__name__': '__main__', '__file__': str(BASE / 'recovered-retrieval-247.py')})
