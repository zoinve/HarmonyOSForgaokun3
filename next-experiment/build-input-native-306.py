from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
RADIO = runpy.run_path(str(BASE / 'build-radio-native-297.py'))
ONCE = RADIO['MODULE']['once']

def outer306(source, old_digest, digest):
    source = RADIO['outer297'](source, old_digest, digest)
    source = source.replace('/commercial61-native-297/bootstrap-runtime087',
                            '/commercial61-native-306/bootstrap-runtime087')
    source = ONCE(source, '    pid_t radio261_broker = -1;',
                  '    pid_t radio261_broker = -1;\n    pid_t touch306 = -1;')
    anchor = '                if(i==4 && started083)native_live159_start(child);'
    start = r'''                if (i==4 && touch306<0) {
                    touch306=fork();
                    if (!touch306) {
                        execl("/input306/touch-monitor","touch-monitor306",NULL);
                        _exit(90);
                    }
                    dprintf(1,"TOUCH306_MONITOR_START pid=%d original_mmi_unchanged=1\n",touch306);
                }
'''
    source = ONCE(source, anchor, start + anchor)
    anchor = '    int trace285 = open('
    finish = r'''    if (touch306>0) {
        int status306=0;
        pid_t done306=waitpid(touch306,&status306,WNOHANG);
        if (!done306) {
            kill(touch306,SIGKILL);
            while (waitpid(touch306,&status306,0)<0 && errno==EINTR) {}
        }
        dprintf(1,"TOUCH306_MONITOR_END forced_stop=%d raw_wait_status=%d\n",!done306,status306);
    }
'''
    return ONCE(source, anchor, finish + anchor)

def extra306(compile_program, stage, entries):
    compile_program('touch-monitor', (BASE / 'native-touch-monitor-303.c').read_text())
    entries['input306'] = (0o40755, b'')
    entries['input306/touch-monitor'] = (0o100755, (stage / 'touch-monitor').read_bytes())

if __name__ == '__main__':
    runpy.run_path(str(BASE / 'driver-builder-305.py'))['build'](
        306, RADIO['runtime297'], outer306, RADIO['vendor297'], extra306)
