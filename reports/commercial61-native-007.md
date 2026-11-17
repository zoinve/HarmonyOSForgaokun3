# Commercial 007 — user-reported freeze; manual recovery

The user reported **“卡死了我重启进入Ubuntu了”**. The runner's `returned: true` means only that Ubuntu became reachable again; it does **not** establish automatic recovery. Do not rewrite that historical runner output or claim the watchdog succeeded. The last recovered process samples precede the reset; no final timeout/target-exit record was captured. The precise cause of the perceived freeze is not established.

64 files were retrieved once, with matching remote/local hashes, using a read-only `noload` mount of the LAB partition, subsequently unmounted. Ubuntu boot ID after recovery is `c11fcf7a-40bb-4c66-a605-97045e1bff5f`. Ubuntu remains default, no one-shot selection remains, and the custom forced-screen-off timer remains disabled.

## Actual profile-discovery evidence

The observer ran as the original samgr process identity, PID 85, UID/GID 5555, then executed the unchanged commercial daemon. Its private `/run` log could not open (`ENOENT`) because that path is not exposed inside the original service sandbox; its kernel-log fallback captured the actual results. This was not a Unix ownership failure.

`const.cust.config_dir_layer` was successfully read as:

```
/usr/system:/usr/system/variant/pc/base:/usr/system/variant/pc/china:/sys_prod:/chip_prod
```

Original `GetCfgFiles("profile")` returned no paths. In that same service context, `/system/profile` opened successfully and contained 209 JSON files, including the original `installs.json` for SA 511. The original sandbox exposes `/system/profile` and `/system/variant`, but not `/usr`. Consequently the canonical config-layer paths and the sandbox-visible paths disagree. No configuration parameter, service identity, permission check, or SA registration was overridden by the observer.

Next bounded repair: add only `/usr/system -> /system` inside the existing system/chipset sandboxes, preserving all original mounts and other settings. This aliases already visible files rather than exposing the host `/usr`, disabling the sandbox, or fabricating SA 511. Verify path resolution offline before another boot. Graphics still requires the real MateBook FD690 backend in place of the original Kirin/Mali hardware selection; no working commercial desktop has been demonstrated.
