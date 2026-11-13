# Ubuntu screen-off helper 001

Scope: the user requested automatic display power-off after Ubuntu boots while native hardware diagnostics continue, including authorized reboots. The helper does not suspend the machine, stop GDM, change authentication, change boot entries, or interrupt SSH.

Installed helper: `/usr/local/libexec/harmony-lab-screen-off-001.py`. The `harmony-lab-screen-off-001.timer` timer starts after boot and retries every 10 seconds, allowing a graphical session to finish starting. Only active, local `seat0` Wayland/X11 sessions are considered. The helper uses that session user's existing D-Bus connection to set GNOME Mutter's `PowerSaveMode` to `3` (off), and reads the property back. Already-off sessions are not rewritten. Failures are reported to the journal, not silently treated as success.

Verification and deployment evidence are in `ubuntu-screen-off-001.json`; policy tests are `next-experiment/test-ubuntu-screen-off-001.py`. D-Bus power-state confirmation is not a physical observation of the panel, nor proof of behavior after a future reboot.

Deployment caught two integration issues before any completion claim: `loginctl` needs separate `--property` options (a comma-joined filter silently returned no session fields), and `ProtectHome=true` hid the session bus under `/run/user`. The installed helper uses separate options; the unit uses `ProtectHome=read-only` so the bus remains reachable without granting home-directory writes. Tests cover the observed loginctl argument behavior; the actual service must also pass its runtime check.

The earlier attempt to write backlight brightness `0` returned `EINVAL` even though the sysfs brightness/actual_brightness values became `0`; a subsequent `bl_power=4` write also returned `EINVAL`. These sysfs values alone are not used to claim successful panel control. The original requested brightness was `1256` out of `4095`, with `bl_power=0`, preserved for this boot in `/run/harmony-lab-screen-off-001.json` and in the deployment report.

To stop automatic power-off:

```sh
sudo systemctl disable --now harmony-lab-screen-off-001.timer
```

The current display may then be woken normally; restore brightness through the desktop if needed. An alternative temporary opt-out is creating `/etc/harmony-lab-screen-off.disabled`; remove only that opt-out file to resume future timer actions. Files are uniquely named and the installer refuses to overwrite an existing installation.

Important limitation: this service runs in Ubuntu only. Firmware, the boot menu, and the independent diagnostic initramfs do not run this service and may briefly illuminate the screen. Do not change diagnostic display initialization merely to hide that light, because it would alter the hardware experiment.
