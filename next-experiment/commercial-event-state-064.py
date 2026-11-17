"""Read public boot parameters and effective ACLs after original account startup."""
from pathlib import Path
import runpy

LOG = '/data/commercial-event-state064.log'
KEYS = [
    'bootevent.avsessionservice.ready', 'bootevent.huksService.ready',
    'bootevent.netmanager.ready', 'bootevent.netsysnative.ready',
    'bootevent.samgr.ready', 'bootevent.renderservice.ready',
    'bootevent.bootanimation.started', 'bootevent.bootanimation.finished',
    'bootevent.bms.main.bundles.ready', 'bootevent.appfwk.ready',
    'bootevent.lockscreen.ready', 'bootevent.launcher.ready',
    'bootevent.wms.ready', 'bootevent.account.ready',
    'bootevent.appspawn.started', 'bootevent.param_watcher.started',
    'bootevent.powermgr.ready', 'bootevent.hdf_devmgr.ready',
    'bootevent.composer_host.ready', 'bootevent.bootanimation.ready',
    'bootevent.boot.completed', 'persist.init.bootevent.enable',
]


def diagnostics():
    keys = ' '.join(KEYS)
    return '''(
    umask 077
    set -C
    exec > LOG064 2>&1 || exit 1
    printf 'COMMERCIAL064_EVENT_DIAGNOSTICS_BEGIN public_cli=1\n'
    /system/bin/id
    /system/bin/id composer_host
    /system/bin/id hdf_devmgr
    for path in /vendor/etc/param /vendor/etc/param/composer_host.para.dac /vendor/etc/param/hdf_devmgr.para.dac; do
        printf 'COMMERCIAL064_CONFIG path=%s\n' "$path"
        /system/bin/ls -ldn "$path"
    done
    /system/bin/cat /vendor/etc/param/composer_host.para.dac
    /system/bin/cat /vendor/etc/param/hdf_devmgr.para.dac
    for key in KEYS064; do
        printf 'COMMERCIAL064_ACL_BEGIN key=%s\n' "$key"
        /system/bin/param ls "$key"
        printf 'COMMERCIAL064_ACL_END result=%s\n' "$?"
    done
    for round in 0 1 2 3 4; do
        printf 'COMMERCIAL064_SNAPSHOT_BEGIN round=%s\n' "$round"
        /system/bin/cat /proc/uptime
        for key in KEYS064; do
            printf 'COMMERCIAL064_VALUE_BEGIN key=%s\n' "$key"
            /system/bin/param get "$key"
            printf 'COMMERCIAL064_VALUE_END result=%s\n' "$?"
        done
        printf 'COMMERCIAL064_SNAPSHOT_END round=%s\n' "$round"
        [ "$round" -eq 4 ] || /system/bin/sleep 15
    done
    printf 'COMMERCIAL064_EVENT_DIAGNOSTICS_END\n'
)
'''.replace('LOG064', LOG).replace('KEYS064', keys)


def repair(original):
    script = runpy.run_path(str(Path(__file__).with_name('commercial-account-order-063.py')))['repair'](original)
    anchor = '''        printf 'COMMERCIAL063_ACCOUNT_READY observed_value=%s\n' "$ready"
        exit 0'''
    assert script.count(anchor) == 1
    return script.replace(anchor, anchor.replace('        exit 0', diagnostics() + '        exit 0'), 1)


def instrument_outer(outer):
    anchor = '    char path[256],expected[128]={},actual[128]={},text[4096];\n'
    assert outer.count(anchor) == 1
    extra = ('    snprintf(path,sizeof(path),"/proc/%d/root' + LOG + '",child);\n'
             '    commercial_outer_stream044(path,32768);\n')
    return outer.replace(anchor, anchor + extra, 1)
