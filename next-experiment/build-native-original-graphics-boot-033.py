"""Unattended cursor validation: bounded target lifetime, independent reboot fallback."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-032.py'))
inner=p['inner']
outer=p['outer'].replace('native-interactive-032-%s','native-interactive-033-%s').replace('NATIVE_INTERACTIVE032','NATIVE_UNATTENDED033')
anchor='    /* Interactive mode: no physical-host reboot deadline. */'
assert outer.count(anchor)==1
outer=outer.replace(anchor,r'''
    /* Armed before module/storage I/O. Separate process survives a blocked parent.
     * Last-resort reboot intentionally avoids a potentially blocked sync path.
     * This is not a hardware watchdog and cannot recover a wedged kernel.
     */
    pid_t deadline033=fork();
    if(deadline033<0){reboot(RB_AUTOBOOT);hold();}
    if(!deadline033){
        unsigned left033=420;
        while(left033)left033=sleep(left033);
        dprintf(2,"NATIVE_UNATTENDED033 fallback_reboot=1 sync_skipped=1\n");
        reboot(RB_AUTOBOOT);hold();
    }
''',1)
start=outer.index('            dprintf(1,"NATIVE_UNATTENDED033_RUNNING')
end=outer.index('        }\n        kill(broker',start)
outer=outer[:start]+r'''
            dprintf(1,"NATIVE_UNATTENDED033_RUNNING target_budget_seconds=240\n");
            int state=0;pid_t got=0;
            for(unsigned elapsed033=70;elapsed033<240;++elapsed033){
                got=waitpid(child,&state,WNOHANG);
                if(got==child || (got<0 && errno!=EINTR))break;
                if(elapsed033%15==0)snapshot();
                sleep(1);
            }
            if(got==0){
                dprintf(1,"NATIVE_UNATTENDED033 target_timeout=1\n");
                kill(child,SIGKILL);
                for(unsigned n=0;n<10;++n){
                    got=waitpid(child,&state,WNOHANG);
                    if(got==child || (got<0 && errno!=EINTR))break;
                    sleep(1);
                }
            }
            dprintf(1,"NATIVE_UNATTENDED033_TARGET_EXIT pid=%d status=%d\n",got,state);
            snapshot();
'''+outer[end:]
outer=outer.replace('NATIVE_UNATTENDED033_STOPPED manual_power_cycle_required=1','NATIVE_UNATTENDED033_STOPPED returning_to_ubuntu=1')
anchor='    hold();\n    return 1;'
assert outer.count(anchor)==1
outer=outer.replace(anchor,'    sync();\n    reboot(RB_AUTOBOOT);\n    hold();\n    return 1;',1)
payload=p['payload'].replace('native-original-graphics-boot-032','native-original-graphics-boot-033')
assert payload.count('outer='+repr(p['outer']))==1
payload=payload.replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('outer_deadline_seconds=None,original_service_observation_seconds=None,interactive_manual_exit=True',
    'outer_deadline_seconds=420,original_service_observation_seconds=240,interactive_manual_exit=False')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
