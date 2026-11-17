"""Load packaged Wi-Fi power dependencies and observe real hardware readiness."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-079.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-079', 'commercial61-native-080').replace('COMMERCIAL079', 'COMMERCIAL080')
start = outer.index('                char *wifi079[] = ')
end = outer.index('                native_original();', start)
NETWORK = r'''
                char *power080[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", "pwrseq_qcom_wcn", NULL};
                (void)probe("wifi-power080", power080, 8);
                char *pci080[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", "pci_pwrctrl_pwrseq", NULL};
                (void)probe("wifi-pci-power080", pci080, 8);
                char *wifi080[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", "ath11k_pci", NULL};
                (void)probe("wifi-driver080", wifi080, 15);
                char *net080[] = {"/bin/busybox", "sh", "-c",
                    "echo NETWORK080_KERNEL_OBSERVATION_BEGIN; "
                    "i=0; ready=0; while [ $i -lt 40 ]; do "
                    "for n in /sys/class/net/*/phy80211; do "
                    "if [ -L $n ]; then echo NETWORK080_PHY_OBSERVED=$n; ready=1; break; fi; done; "
                    "[ $ready -eq 0 ] || break; i=$((i+1)); /bin/busybox sleep 0.25; done; "
                    "echo NETWORK080_POLLS=$i; /bin/busybox ls -l /sys/class/net /sys/class/ieee80211; "
                    "/bin/busybox cat /proc/net/dev /proc/net/route /proc/modules; "
                    "for n in /sys/class/net/*; do echo INTERFACE=$n; "
                    "/bin/busybox ls -l $n/device/driver $n/phy80211; "
                    "for a in operstate carrier address; do echo ATTRIBUTE=$a; /bin/busybox cat $n/$a; done; done; "
                    "for d in /sys/bus/pci/devices/* /sys/bus/platform/devices/*pcie* "
                    "/sys/bus/platform/devices/*wcn* /sys/bus/platform/devices/*wifi*; do "
                    "[ -d $d ] || continue; echo NETWORK080_DEVICE=$d; /bin/busybox ls -ld $d/driver; "
                    "for a in vendor device subsystem_vendor subsystem_device modalias waiting_for_supplier; do "
                    "if [ -f $d/$a ]; then echo ATTRIBUTE=$a; /bin/busybox cat $d/$a; fi; done; "
                    "for s in $d/supplier:*; do [ ! -e $s ] || /bin/busybox ls -ld $s; done; done; "
                    "if [ -r /sys/kernel/debug/devices_deferred ]; then "
                    "echo NETWORK080_DEFERRED; /bin/busybox cat /sys/kernel/debug/devices_deferred; fi; "
                    "/bin/busybox dmesg; echo NETWORK080_KERNEL_OBSERVATION_END_NOT_CONNECTIVITY; "
                    "[ $ready -eq 1 ] || exit 124", NULL};
                (void)probe("wifi-observation080", net080, 15);
'''
outer = outer[:start] + NETWORK + outer[end:]
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace(
    'commercial61-native-079', 'commercial61-native-080')

if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
