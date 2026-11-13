from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'build-native-original-graphics-boot-031.py').is_file(),'missing repaired interactive candidate'
p=runpy.run_path(str(base/'build-native-original-graphics-boot-031.py'))
assert 'reboot(' not in p['outer'] and 'sleep(180)' not in p['outer']
assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET' in p['outer']
assert p['inner']==p['p']['inner']
assert 'native-binder-kernel-031' in p['payload']
s=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
s=s.replace('native-original-graphics-boot-001','native-original-graphics-boot-031')
s=s.replace("assert 'sleep(180); reboot(RB_AUTOBOOT)' in outer","assert 'reboot(' not in outer and 'pid_t deadline = fork()' not in outer")
s=s.replace("assert 'kill(child,SIGKILL)' in outer and 'snapshot();' in outer","assert 'kill(child,SIGKILL)' not in outer and 'waitpid(child,&state,0)' in outer")
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=s,text=True).returncode)
