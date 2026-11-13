from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
builder=base/'build-native-original-graphics-boot-030.py'
assert builder.exists(),'missing persistent interactive capture candidate'
p=runpy.run_path(str(builder));outer=p['outer'];inner=p['inner']
assert 'reboot(' not in outer and 'sleep(180)' not in outer
assert '(void)kill(child,SIGKILL)' not in outer
assert 'waitpid(child,&state,0)' in outer
assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET' in outer
assert 'SYS_open_tree' in outer
assert 'interactive-hilog030.log' in outer and 'interactive-faults030.log' in outer
assert 'O_EXCL|O_NOFOLLOW' in outer
assert 'native_persistent_capture030();' in inner
assert '128*1024*1024' in inner and '64*1024*1024' in inner
assert 'close(198);close(199);' in inner
assert 'if(sample==8)native_swipe_017();' not in inner
assert 'if(sample==9)native_keyboard_027();' not in inner
print('PASS no reboot/target kill/input injection; bounded persistent capture, descriptors closed before init')
if __name__=='__main__':
 check=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
 check=check.replace('native-original-graphics-boot-001','native-original-graphics-boot-030')
 check=check.replace("assert 'sleep(180); reboot(RB_AUTOBOOT)' in outer","assert 'reboot(' not in outer and 'pid_t deadline = fork()' not in outer")
 check=check.replace("assert 'kill(child,SIGKILL)' in outer and 'snapshot();' in outer","assert 'kill(child,SIGKILL)' not in outer and 'waitpid(child,&state,0)' in outer")
 raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=check,text=True,timeout=120).returncode)
