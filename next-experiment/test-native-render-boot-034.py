"""Read-only source contract and artifact verification for one bounded run."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'build-native-original-graphics-boot-034.py').is_file(),'missing accelerated bounded candidate'
p=runpy.run_path(str(base/'build-native-original-graphics-boot-034.py'))
assert p['inner']==p['p']['inner']
assert 'left033=420' in p['outer'] and 'elapsed033<240' in p['outer']
assert 'native-interactive-034-%s' in p['outer']
assert "root/'native-render-034'" in p['payload']
assert 'automatic_input_injection=True' not in p['payload']
check=runpy.run_path(str(base/'test-native-interactive-031.py'))['s']
check=check.replace('native-original-graphics-boot-031','native-original-graphics-boot-034')
check=check.replace("assert 'reboot(' not in outer and 'pid_t deadline = fork()' not in outer", "assert 'left033=420' in outer and 'elapsed033<240' in outer")
check=check.replace("assert 'kill(child,SIGKILL)' not in outer and 'waitpid(child,&state,0)' in outer", "assert 'waitpid(child,&state,WNOHANG)' in outer")
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=check,text=True).returncode)
