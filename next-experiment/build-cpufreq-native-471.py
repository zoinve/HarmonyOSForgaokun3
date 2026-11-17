"""Supply the real EPSS L3 interconnect dependency before native services."""
from pathlib import Path
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
PRIOR = runpy.run_path(str(BASE / 'build-driver-interactive-458.py'))
MODULE = Path('/home/zoinve/harmony-virgl-883/native-binder-kernel-045/out/drivers/interconnect/qcom/icc-osm-l3.ko')


def dependency471(source):
    anchor = '            const char *modules[] = {"i2c_qcom_geni",'
    assert source.count(anchor) == 1, 'expected original board module initialization'
    helper = '''            char *icc471[] = {"/bin/busybox", "insmod", "/cpufreq471/icc-osm-l3.ko", NULL};
            (void)probe("cpufreq-icc-provider-471", icc471, 15);
            char *freq471[] = {"/bin/busybox", "sh", "-c",
                "echo CPUFREQ471_BEGIN_REAL_SYSFS; "
                "i=0; while [ ! -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq ] && [ $i -lt 20 ]; do "
                "/bin/busybox sleep 0.1; i=$((i+1)); done; "
                "for p in /sys/devices/system/cpu/cpufreq/policy*; do "
                "[ -d $p ] || continue; echo POLICY=$p; "
                "for a in scaling_driver related_cpus scaling_cur_freq scaling_min_freq scaling_max_freq; do "
                "echo ATTRIBUTE=$a; /bin/busybox cat $p/$a; done; done; "
                "echo CPUFREQ471_END_NOT_TASK_MANAGER_ACCEPTANCE", NULL};
            (void)probe("cpufreq-real-sysfs-471", freq471, 5);
'''
    return source.replace(anchor, helper + anchor, 1)


def outer471(source, old_digest, digest):
    source = PRIOR['outer458'](source, old_digest, digest)
    old = '/commercial61-native-458/bootstrap-runtime087'
    assert old in source
    return dependency471(source.replace(old, '/commercial61-native-471/bootstrap-runtime087'))


def extra471(compile_program, stage, entries):
    PRIOR['PRIOR']['extra454'](compile_program, stage, entries)
    info = subprocess.check_output(['modinfo', str(MODULE)], text=True)
    assert '7.1.0-rc3-gaokun3-el2 SMP preempt mod_unload aarch64' in info
    fields = dict(line.split(':', 1) for line in info.splitlines() if ':' in line)
    assert fields['name'].strip() == 'icc_osm_l3'
    assert not fields['depends'].strip()
    assert 'of:N*T*Cqcom,epss-l3' in info
    entries['cpufreq471'] = (0o40755, b'')
    entries['cpufreq471/icc-osm-l3.ko'] = (0o100644, MODULE.read_bytes())


if __name__ == '__main__':
    original = PRIOR['PRIOR']['PRIOR']['PRIOR']['PRIOR']['PRIOR']
    runpy.run_path(str(BASE / 'driver-builder-305.py'))['build'](
        471, original['runtime401'], outer471,
        original['OLD']['AUDIO']['RADIO']['vendor297'], extra471)
