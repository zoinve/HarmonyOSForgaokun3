"""Throwaway four-disk probe configuration; no L410 image configuration is reused."""
from pathlib import Path

LAB = '/home/zoinve/.local/share/harmony-arm64-kvm-lab'


def build_config(rows, remote):
    names = ['system.img', 'vendor.img', 'sys_prod.img', 'userdata.img']
    assert [row['name'] for row in rows] == names
    command = ['qemu-system-aarch64', '-machine', 'virt,gic-version=3',
               '-cpu', 'host', '-accel', 'kvm', '-smp', '4', '-m', '6144',
               '-kernel', LAB + '/system-882/Image',
               '-initrd', remote + '/initramfs.cpio.gz',
               '-append', 'ohos.boot.hardware=hmos.emulator console=ttyAMA0 rdinit=/init panic=-1 loglevel=7',
               '-display', 'none', '-device', 'virtio-gpu-pci,xres=1920,yres=1080',
               '-device', 'qemu-xhci', '-device', 'usb-kbd', '-device', 'usb-mouse',
               '-qmp', 'unix:' + remote + '/qmp.sock,server=on,wait=off',
               '-serial', 'stdio', '-monitor', 'none', '-nic', 'none', '-no-reboot', '-S']
    disks = []
    for i, row in enumerate(rows):
        disk = dict(row, readonly=i != 3)
        if i == 3:
            disk['path'] = remote + '/userdata-permissive.img'
        disks.append(disk)
        command += ['-drive', 'if=none,id=d%d,format=raw,file=%s%s' %
                    (i, disk['path'], ',readonly=on' if disk['readonly'] else ''),
                    '-device', 'virtio-blk-pci,drive=d%d,serial=official-%s,addr=0x%x' %
                    (i, ['system', 'vendor', 'sysprod', 'userdata'][i], i + 3)]
    return dict(command=command, disks=disks, originals=rows,
                qmp_screenshots_enabled=False,
                inputs=[dict(remote=LAB + '/system-882/Image',
                             sha256='fb9dffc643f64c754c4a7a34e6fd3b9de6d60bd1ed2ba2aa6096f25bf7ad5474'),
                        dict(remote=remote + '/initramfs.cpio.gz',
                             sha256='92e447afc89aa83dc92d46ef009ce35c729d95a7cca1aa2f02d5353e3f663a19')])


def make_runner(remote, template):
    source = Path(template).read_text()
    replacements = {
        "expected={'d'+str(i):i!=4 for i in range(5)}":
            "expected={'d'+str(i):i!=3 for i in range(4)}",
        "shutil.copyfile(protected_original,work)":
            "assert all(sha(row['path'])==row['sha256'] for row in c['originals'])\nshutil.copyfile(Path(c['originals'][3]['path']),work)",
        " assert d['protected_userdata_original_unchanged']":
            " d['official_originals_after']={row['path']:sha(row['path']) for row in c['originals']}\n d['official_originals_unchanged']=all(d['official_originals_after'][row['path']]==row['sha256'] for row in c['originals'])\n assert d['protected_userdata_original_unchanged'] and d['official_originals_unchanged']",
    }
    for old, new in replacements.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    source = source.replace(LAB + '/system-868', remote)
    return source
