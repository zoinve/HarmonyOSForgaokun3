"""Check that the interactive harness has no timed termination/reboot paths."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
builder=base/'build-native-original-graphics-boot-029.py'
assert builder.exists(),'missing interactive candidate'
p=runpy.run_path(str(builder))
outer=p['outer'];inner=p['inner']
assert 'reboot(' not in outer
assert 'sleep(180)' not in outer and 'pid_t deadline = fork()' not in outer
assert '(void)kill(child,SIGKILL)' not in outer
assert 'NATIVE_INTERACTIVE029_RUNNING' in outer and 'waitpid(child,&state,0)' in outer
assert 'if(sample==8)native_swipe_017();' not in inner
assert 'if(sample==9)native_keyboard_027();' not in inner
assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET' in outer
assert 'SYS_open_tree' in outer
print('PASS interactive source: no harness reboot/deadline/target kill; no injected gestures')
if __name__=='__main__':
    import subprocess
    check=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
    check=check.replace('native-original-graphics-boot-001','native-original-graphics-boot-029')
    check=check.replace("assert 'sleep(180); reboot(RB_AUTOBOOT)' in outer","assert 'reboot(' not in outer and 'pid_t deadline = fork()' not in outer")
    check=check.replace("assert 'kill(child,SIGKILL)' in outer and 'snapshot();' in outer","assert 'kill(child,SIGKILL)' not in outer and 'waitpid(child,&state,0)' in outer")
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=check,text=True,timeout=120).returncode)
