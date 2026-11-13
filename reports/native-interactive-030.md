# HarmonyOS 030 — manual interactive app-exit capture

## Installed entry

Select **HarmonyOS 030 - NO AUTO REBOOT - persistent app crash capture** from the boot menu. Installation did not select it or reboot the machine. Ubuntu remains the default; 029 remains available.

030 retains 029's real hardware adaptation, service credentials, target SELinux permissive mode, input rotation, keyboard/touchpad modules, GPU path and Bluetooth transport. It does not add automatic gestures or key presses, change app permissions, suppress failures, or fix the app-exit cause.

## What changed

029's original short passive snapshots remain, but two independent collectors now continue after that observation window:

- `interactive-hilog030.log`: unfiltered output of the original `/system/bin/hilog`, including application lifecycle, SceneBoard/window, input and fault messages. Pipe bytes are saved unchanged between explicitly identified collector status records. Capacity: **128 MiB**, with reserved space for termination markers. Reader EOF can trigger bounded retries; read/write errors or capacity stop this collector only.
- `interactive-faults030.log`: original fault files under `/data/log/faultlog` and `/data/log/hiview/stack`, exported every ten seconds using the existing byte-offset/hex/completion/change protocol. Symlink entries are not followed. Capacity: **64 MiB** (kernel-enforced per collector); exports are also bounded by directory depth, file count and per-file/per-pass bytes. Repeated files can occur. A capacity-hit partial export is not a complete crash report. At the hard size limit this diagnostic collector may terminate with SIGXFSZ; that is not an app crash.

Both files are created exclusively with mode 0600 inside the new LAB run directory:

`/mnt/harmony-lab/native-interactive-030-<boot-uuid>/`

The diagnostic parent passes only these two writable file descriptors to the collectors. They are closed before the original init and its services execute; no LAB directory descriptor is newly exposed to those services. Hilog writes are fsynced during collection/idle/EOF/capacity handling; fault exports are fsynced after each pass. A sudden power loss can still lose the in-progress tail. Reaching either capture limit does **not** terminate the target namespace or reboot.

The outer harness has no 70/180-second target termination or reboot timer; it waits for the original target to exit. `panic=0` is retained. Hardware/firmware resets and original target failures cannot be ruled out. The actual `/data` is still a volatile 3 GiB RAM filesystem: only these exported logs and the existing LAB snapshots persist, not app data or every possible fault file.

## Reproduction

1. Boot 030 manually and unlock normally.
2. Open **Settings** and one other failing application, preferably separately; note their names and approximate order/time. Avoid manual window-close gestures during the initial observation so we can distinguish a requested close from an unsolicited exit.
3. After the failure, wait at least **15 seconds** for fault export and sync.
4. Return to Ubuntu manually. If the target offers no working shutdown/restart, use the previously established physical power-cycle recovery. Do not delete/reuse the run directory.
5. Tell the agent reproduction is finished; collect and hash the two persistent files plus the existing snapshots before making a root-cause fix.

## Verification and limitations

- Build passed GNU static bootstrap and OHOS graphics compilation with existing strict compiler checks. Nine artifacts passed hash/guard-source checks; two native non-PID1 executions correctly refused with exit 77.
- The actual pipe/file helper passed byte-for-byte preservation, EOF sync, exact capacity and delayed-event-after-idle tests in disposable host fixtures. These tests do not launch HarmonyOS services or probe host hardware.
- Installed initrd and candidate-local touch DTB hashes were independently verified; manual uncounted entry, `panic=0`, preserved 029, unchanged Ubuntu default/current boot, no one-shot selection and active screen-off timer were freshly checked. See `native-original-graphics-boot-030/installation-final-verification.json`.
- **030 has not been booted by the agent. End-to-end persistent collection under original init remains unverified until this reproduction. App exits are not repaired.** Root cause from 029 remains unknown: the captured Settings timeline shows a genuine MainAbility foreground followed about 7.8 seconds later by a SceneBoard close request, not why that request happened.
- One initial compile attempt rejected `pipe2` because the inherited feature-macro ordering hid its declaration. Replaced it with `pipe` plus explicit close-on-exec flags before any child fork; rejected build sources were preserved under `*-build-rejected-001`.
- Only the unreferenced, byte-identical EFI cache `native-original-graphics-020/initrd.img` was reclaimed after reference/hash checks and a before-delete journal. Its staged original and historical evidence remain. The installer verified 88 other pre-existing EFI files unchanged and 91,181,056 bytes free, preserving Ubuntu default and firmware entries.

Initrd SHA256: `a123991734d4687750f8be89e27b242bf348f8f425abfa44351dd7dc90db428f`.
