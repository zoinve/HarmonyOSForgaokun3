"""Manual interactive variant; never automatically terminate/reboot the target."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-027.py'))
inner=p['inner'].replace('if(sample==8)native_swipe_017();','(void)native_swipe_017; /* interactive: no injected swipe */').replace('if(sample==9)native_keyboard_027();','(void)native_keyboard_027; /* interactive: no injected keys */')
outer=p['outer'].replace('native-original-027-%s','native-interactive-029-%s')
start=outer.index('    /* Best effort only: cannot recover a kernel hard lock; no watchdog alteration. */')
end=outer.index('    char *pcie_phy[]',start)
outer=outer[:start]+'    /* Interactive mode: no physical-host reboot deadline. */\n'+outer[end:]
old='''            (void)kill(child,SIGKILL);
            (void)waitpid(child,NULL,WNOHANG);'''
assert outer.count(old)==1
outer=outer.replace(old,'''            dprintf(1,"NATIVE_INTERACTIVE029_RUNNING manual_exit_only=1 volatile_data=1\\n");
            snapshot();
            int state=0;pid_t got;
            do { got=waitpid(child,&state,0); } while(got<0 && errno==EINTR);
            dprintf(1,"NATIVE_INTERACTIVE029_TARGET_EXIT pid=%d status=%d auto_restart=0\\n",got,state);
            snapshot();''')
outer=outer.replace('reboot(RB_AUTOBOOT);','dprintf(1,"NATIVE_INTERACTIVE029_STOPPED manual_power_cycle_required=1\\n");')
assert 'reboot(' not in outer
payload=p['payload'].replace('native-original-graphics-boot-027','native-original-graphics-boot-029')
assert 'inner='+repr(p['inner']) in payload and 'outer='+repr(p['outer']) in payload
payload=payload.replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('outer_deadline_seconds=180,original_service_observation_seconds=70','outer_deadline_seconds=None,original_service_observation_seconds=None,interactive_manual_exit=True,automatic_input_injection=False')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
