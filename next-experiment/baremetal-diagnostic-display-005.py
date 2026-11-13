"""Versioned supplier hypothesis and read-only binding evidence, not a boot action."""
import hashlib


def build_source(parent):
    assert hashlib.sha256(parent.encode()).hexdigest() == '8a7f42cb344b88dfb16782d5f4e0ca1002b5640561e6a40d6ca062bd158a0cfe'
    old = '"panel_himax_hx83121a", "msm", "spi_geni_qcom"'
    new = ('"panel_himax_hx83121a", "dispcc_sc8280xp", "gpucc_sc8280xp", '
           '"phy_qcom_qmp_combo", "msm", "spi_geni_qcom"')
    assert parent.count(old) == 1
    parent = parent.replace(old, new)
    anchor = '            const char *modules[]'
    observation = r'''            char *bindings[] = {"/bin/busybox", "sh", "-c",
                "echo DEVICE_BINDINGS; /bin/busybox cat /proc/uptime; "
                "echo LOADED_MODULES; /bin/busybox cat /proc/modules; "
                "for n in af00000.clock-controller 3d90000.clock-controller 88eb000.phy 8903000.phy "
                "ae00000.display-subsystem ae01000.display-controller ae94000.dsi ae96000.dsi "
                "ae94400.phy ae96400.phy 998000.spi; do "
                "d=/sys/bus/platform/devices/$n; echo DEVICE=$d; "
                "if [ -d $d ]; then /bin/busybox ls -ld $d/driver; "
                "for a in waiting_for_supplier modalias; do "
                "[ ! -f $d/$a ] || { echo ATTRIBUTE=$a; /bin/busybox cat $d/$a; }; done; "
                "else echo DEVICE_ABSENT; fi; done; "
                "for d in /sys/class/spi_master/spi*/device/spi*/spi*.0 /sys/bus/spi/devices/spi*.0; do "
                "[ ! -d $d ] || { echo SPI_DEVICE=$d; /bin/busybox ls -ld $d/driver; "
                "for a in waiting_for_supplier modalias; do "
                "[ ! -f $d/$a ] || { echo ATTRIBUTE=$a; /bin/busybox cat $d/$a; }; done; }; done; "
                "echo BINDING_SNAPSHOT_COMPLETE_NOT_READINESS", NULL};
            (void)probe("binding-state", bindings, 5);
'''
    assert parent.count(anchor) == 1
    parent = parent.replace(anchor, observation + anchor)
    anchor = '            if (status != 124 && status != 125) {'
    assert parent.count(anchor) == 1
    parent = parent.replace(anchor, '            (void)probe("binding-state", bindings, 5);\n' + anchor)
    return parent
