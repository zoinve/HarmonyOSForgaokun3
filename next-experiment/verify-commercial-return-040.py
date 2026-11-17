from pathlib import Path
import runpy,subprocess
source=runpy.run_path(str(Path(__file__).with_name('verify-commercial-return-039.py')))['source'].replace("commercial61-native-039","commercial61-native-040").replace("commercial-return-audit-039","commercial-return-audit-040").replace("COMMERCIAL039","COMMERCIAL040").replace("ordered_chain_equals_full_039","ordered_chain_equals_full_040").replace("Post-flush render tasks 039","Reference direct EGL GLES route 040")
anchor="assert set(changed)<= {'loader/random-seed'},changed"
replacement="""# User authorized retention of only two diagnostic entry files.
retentions=[]
for archive in work.parent.glob('boot-entry-retention-*'):
 p=archive/'result.json'
 if p.is_file():retentions.append(json.loads(p.read_text()))
authorized={ 'loader/entries/'+r['name']:r['sha256'] for evidence in retentions for r in evidence['removed'] }
removed_entries=[n for n in changed if n in authorized and authorized[n]==j['efi_before'][n] and not (esp/n).exists()]
assert set(changed)<= {'loader/random-seed',*removed_entries},changed"""
assert source.count(anchor)==1
source=source.replace(anchor,replacement,1)
source=source.replace("boot_managed_changes=changed,","boot_managed_changes=[n for n in changed if n not in removed_entries],user_authorized_old_entries_removed=removed_entries,")
if __name__=="__main__":exec(compile(source,__file__,"exec"),{"__name__":"__main__","__file__":__file__})
