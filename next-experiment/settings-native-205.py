"""Allow original BMS recovery time; gate one CLI launch on real boot parameters."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXPECTED_DATA = 'e7e18b21f4e1d0d6a4acd652edc13b64c0ab4f3540ea6ddb155ea107f4e57fb4'


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new, 1)


def outer205(source):
    old = '/commercial61-native-201/bootstrap-runtime087'
    assert source.count(old) == 5
    source = source.replace(old, '/commercial61-native-205/bootstrap-runtime087')
    source = once(source, '#include "settings-launch-201.h"', '#include "settings-launch-205.h"')
    source = once(source, 'if(i==10)settings201_start(child);', 'if(i==10)settings205_start(child);')
    source = once(source, 'target_budget_seconds=150', 'target_budget_seconds=720')
    source = once(source, 'elapsed033<150', 'elapsed033<720')
    source = once(source, 'unsigned left033=270;', 'unsigned left033=900;')
    return once(source, '                if(elapsed033%15==0)native_full_export068(child);',
        '                if(elapsed033%15==0)settings205_start(child);\n'
        '                if(elapsed033%15==0)native_full_export068(child);')


def launch205(source):
    source = source.replace('settings201', 'settings205').replace('SETTINGS201', 'SETTINGS205')
    start = source.index('        char *const args[] = {"/system/bin/aa","start"')
    end = source.index('        execve(args[0],args,env);', start)
    replacement = r'''        static const char script[] =
            "read_param() { set -- $(/system/bin/param get $1 2>/dev/null); printf '%s' ${1:-}; }; "
            "bms=0; account=0; appfwk=0; "
            "case $(read_param bootevent.bms.main.bundles.ready) in true) bms=1;; esac; "
            "case $(read_param bootevent.account.ready) in true) account=1;; esac; "
            "case $(read_param bootevent.appfwk.ready) in true) appfwk=1;; esac; "
            "printf 'SETTINGS205_READINESS bms=%s account=%s appfwk=%s original_parameters_read_only=1\n' $bms $account $appfwk; "
            "[ $bms$account$appfwk = 111 ] || exit 75; "
            "printf 'SETTINGS205_REQUEST original_aa=1 original_ams_user_selection=1 fixed_request=1\n'; "
            "exec /system/bin/aa start -b com.huawei.hmos.settings -a com.huawei.hmos.settings.MainAbility -m pc_settings";
        char *const args[] = {"/system/bin/sh", "-c", (char *)script, NULL};
        char *const env[] = {"PATH=/system/bin:/vendor/bin", "HOME=/", NULL};
'''
    source = source[:start] + replacement + source[end:]
    source = once(source, '    static int attempted;\n', '    static int attempted;\n    static int output = -1;\n')
    source = once(source, '    attempted = 1;\n    int fd=openat(',
        '    if (output < 0) output=openat(')
    source = once(source, '    if (fd < 0) {', '    int fd=output;\n    if (fd < 0) {')
    source = once(source, '    close(fd);\n    dprintf(1,"SETTINGS205_COMMAND_RESULT',
        '    if (result != 75) { attempted=1; close(output); output=-1; }\n'
        '    dprintf(1,"SETTINGS205_COMMAND_RESULT')
    return source


def header205():
    return launch205((BASE / 'settings-launch-201.h').read_text())
