"""Candidate015 method-only diagnostic; unchanged Ubuntu default and reserve."""
from pathlib import Path
import ast,runpy
def launcher_source():
 source=runpy.run_path(str(Path(__file__).with_name('install-baremetal-diagnostic-entry-011.py')),run_name='offline_generator')['launcher_source']()
 for old,new in [
  ('baremetal-boot-entry-preflight-011.json','baremetal-boot-entry-preflight-012.json'),
  ('baremetal-boot-entry-installed-011.json','baremetal-boot-entry-installed-012.json'),
  ('boot-entry-install-011','boot-entry-install-012'),
  ('harmony-native-diag-014','harmony-native-diag-015'),
  ('native-identity-diagnostic-014','native-identity-diagnostic-015'),
  ('801eaaf844aea65d3d57df7350b488ebbd8793c3187fd6666e283e5c7960455b','2521acd99c47bf5465ea5ed2fe0eb0d687491350d4956058f8de5d4309abae53'),
  ('identity and cross-process GPU diagnostic 014','identity and composer-method GPU diagnostic 015')]:
  assert old in source,old
  source=source.replace(old,new)
 ast.parse(source)
 return source
if __name__=='__main__':exec(compile(launcher_source(),__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
