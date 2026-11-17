"""Retain diagnostic ownership correctly; no further commercial service change."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-002.py'))
s=p['inner'];start=s.index('static void commercial_command002');end=s.index('int main(void)',start)
diagnostics=s[start:end].replace('dprintf(199,','dprintf(commercial_diag_fd003,').replace('dup2(199,','dup2(commercial_diag_fd003,')
inner=s[:start]+'static int commercial_diag_fd003=-1;\n'+diagnostics+s[end:]
anchor='    native_persistent_capture030();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'    commercial_diag_fd003=fcntl(199,F_DUPFD_CLOEXEC,200);\n    if(commercial_diag_fd003<0)fail("retain commercial diagnostic evidence descriptor");\n'+anchor,1)
anchor='    execve(arguments[0], arguments, environment);'
inner=inner.replace(anchor,'    close(commercial_diag_fd003);\n'+anchor,1)
outer=p['outer'].replace('commercial61-native-002-%s','commercial61-native-003-%s').replace('COMMERCIAL002','COMMERCIAL003')
payload=p['payload'];assert payload.count('inner='+repr(p['inner']))==1 and payload.count('outer='+repr(p['outer']))==1
payload=payload.replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-002','commercial61-native-003')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
