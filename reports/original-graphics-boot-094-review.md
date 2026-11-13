# Original graphical boot 094 — genuine SceneBoard spawn, not a desktop

## Independently verified progress

Restoring the actual original `init_early` `/mnt` tmpfs prerequisite allows genuine AppSpawn to report SceneBoard **result 0**:

- Original daemon PID 1688, `08:07:12.549`: child `com.ohos.sceneboard`, PID 4106, appId 16, result 0; the subsequent completion message also reports result 0.
- Passive observations see PID 4106 first in the original fork/setup phase (sample 49: UID 0, domain `u:r:appspawn:s0`), then after the original identity transition (sample 61: all four UIDs 20020029, domain `u:r:sceneboard_hap:s0`). These are separate, non-atomic observations; no caller identity or sandbox check was changed by the fixture.
- At samples 24, 30, 41, 49 and 61, actual `statvfs` reads report `/` flags **5** (`RDONLY|NODEV`) and `/mnt` flags **4098** (`NOSUID|RELATIME`, writable). The original read-only root and application sandbox remain in place.

Evidence: `original-graphics-boot-094-independent.json`, serial SHA-256 `097e7e009e29d85d787dd49352548d3758a7d475c60e5ac0d03bed9d00b43395`.

## Still failing / not established

- All four captured 1280×800 QMP frames (120, 360, 480, 600 seconds) are black. There is no verified desktop or physical-display result. The 650-second frame was not captured because the original guest rebooted at about 626.515 seconds.
- Original Foundation reports `THREAD_BLOCK_3S` for SceneBoard PID 4106 at `08:08:21.023`. Earlier SceneBoard PID 3157 was killed. These observations do not identify the blocking subsystem.
- The genuine `bm` and `aa` business requests still report failure despite CLI exit status 0. A successful AppSpawn reply alone is not completed ability startup.
- Original `watchdog_service` exits/restarts and Foundation writes `startup.device.ctl` / `ohos.startup.powerctrl` precede shutdown. Parameter values were not captured, so the exact reboot cause is **unknown**. No watchdog or reboot protection is disabled. No Foundation critical fault was observed.

## Verification and preservation

The first read-only verifier attempt stopped before writing its JSON because the new mount-state reader used undefined `root` instead of existing `BASE`. An AST regression test failed first; only the then-uncompleted 094 verifier was corrected. Four offline tests passed; the fresh `original-graphics-094-verification-output-002.txt` records the successful retry. The first failure output remains intact. The VM and preparation were not rerun.

All 12 injected provider files, real ashmem, configuration-query helper, initrd, kernel, three original SDK images, 378 previous native evidence files and the private 8 GiB test-data volume passed inherited independent checks. Original services, profiles, credentials, policy, signature/permission checks and all three references remain unchanged. All operations were local isolated WSL/QEMU; no MateBook/Ubuntu boot, security, screen-off or physical scanout was changed.

## Fresh 095 diagnostic

095 adds only passive identification of the actual main `com.ohos.sceneboard` process and bounded original `hilog -z 400 -P <actual-pid>` queries at samples 41, 49 and 61. It keeps the verified `/mnt` mount and all existing providers, original services, identities and protections. Runtime and pixel results are pending at this report's creation.

Two offline 095 tests passed. Preparation succeeded once: init 853,968 bytes, SHA-256 `83e901d2d5c0de18baa97d8eefcedf047b339b832e75a3e894433a034dad4d71`. Original policy and graphics init config hashes remain unchanged.
