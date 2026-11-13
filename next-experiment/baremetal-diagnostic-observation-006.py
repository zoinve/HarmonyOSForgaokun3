"""Observation-only follow-up: same modules as 005, bounded DRM-node observation."""
import hashlib
import json


def observation_script():
    # An optional filesystem prefix permits offline fixture/chroot verification.
    return r'''root=${1:-}; i=0
echo DRM_OBSERVATION_BEGIN_NOT_READINESS
while :; do
    if [ -c "$root/dev/dri/card0" ] && [ -d "$root/sys/class/drm/card0" ]; then
        echo DRM_NODE_OBSERVED_NOT_DISPLAY_PROOF
        exit 0
    fi
    if [ "$i" -ge 20 ]; then
        echo DRM_NODE_NOT_OBSERVED
        exit 124
    fi
    /bin/busybox sleep 0.25 || exit 125
    i=$((i+1))
done
'''


def build_source(parent):
    assert hashlib.sha256(parent.encode()).hexdigest() == '21028f6407fdf44081c6cee70270457f4e71822377e2b7e025eb0ebdf1512c95'
    anchor = 'ae94400.phy ae96400.phy 998000.spi; do '
    assert parent.count(anchor) == 1
    parent = parent.replace(anchor, 'ae94400.phy ae96400.phy 998000.spi '
                            'ae90000.displayport-controller ae98000.displayport-controller '
                            '3d00000.gpu 3d6a000.gmu; do ')
    anchor = '                "echo BINDING_SNAPSHOT_COMPLETE_NOT_READINESS", NULL};'
    assert parent.count(anchor) == 1
    parent = parent.replace(anchor, r'''                "for d in /sys/bus/auxiliary/devices/* /sys/bus/platform/devices/*ucsi*; do "
                "[ ! -d $d ] || { echo AUX_OR_UCSI_DEVICE=$d; /bin/busybox ls -ld $d/driver; "
                "for a in waiting_for_supplier modalias; do "
                "[ ! -f $d/$a ] || { echo ATTRIBUTE=$a; /bin/busybox cat $d/$a; }; done; }; done; "
''' + anchor)
    anchor = '            (void)probe("binding-state", bindings, 5);'
    assert parent.count(anchor) == 2
    parent = parent.replace(anchor, '            (void)probe("bindings-before-modules", bindings, 5);', 1)
    wait = ('            char *observe[] = {"/bin/busybox", "sh", "-c", '
            + json.dumps(observation_script()) + ', NULL};\n'
            '            (void)probe("drm-observation-window", observe, 8);\n'
            '            (void)probe("bindings-after-modules", bindings, 5);')
    parent = parent.replace(anchor, wait, 1)
    return parent
