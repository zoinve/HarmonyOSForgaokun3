# Commercial desktop 022 — original SceneBoard resource mounts

## Narrow correction

021's original AppSpawn failed a required SceneBoard sandbox mount before application attachment. Its source pointed to a missing Kirin development directory. Another required source pointed to a missing fingerprint-development package overlay.

022 changes only these two SceneBoard-specific source paths in the RAM-only configuration:

- `/vendor/lib64/passthrough` receives the already granted, read-only `/system/lib64` library tree.
- `/system/app/SceneBoard` receives the actual original `/system/app/SceneBoard` directory, including the commercial `SceneBoard.hap` and its original modules.

Destinations, bind flags, required checks, sandbox `ON`, groups, permissions, other applications and common mounts are unchanged. No fingerprint/OOBE completion overlay is introduced. Original packages, application authorization, seccomp filters, service binaries and identities are preserved. Existing own MateBook hardware backends remain; there is no SDK userland substitution.

## Verification and deployment boundary

Offline tests cover the exact two-source difference, rejection of relaxed/unknown configurations, original resource existence and unchanged service/bootstrap code. Ordered archive extraction matches the complete build byte-for-byte and mode-for-mode. The bootstrap binary is byte-identical to 021. The new final overlay is 704,502 bytes, SHA256 `a8da3924bcc7905572face14444d0e5c846503731b9f020b27ff1ea2f0d951e1`.

The chain remains commercial 001 base → 017 directories → 016 hardware → 022 final. Strict SSH host-key validation, live memory admission, 32 MiB EFI reserve, original image hash checks, Ubuntu default and disabled/inactive custom screen-off timer remain required. Runtime results are pending; no desktop success is claimed. Acceptance requires an actual SceneBoard process and real desktop pixels, not a successful CLI request alone.

## Connection resumed and installation verified

The initial connection to `10.126.126.14` timed out before remote installation. Its original `installation.stdout` and `installation.stderr` are retained. The user restored connectivity and requested the 192 network; this run now uses per-command `HostName=192.168.10.128` and the existing trusted `HostKeyAlias=192.168.10.128`, without changing global SSH configuration or weakening host-key checks.

Installation subsequently succeeded; its separate `installation-192-resume.stdout`/`.stderr` and `installation-result.json` are authoritative. Both native non-PID1 execution guards refused with exit 77. All 104 existing EFI file hashes, Ubuntu default and the disabled timer were preserved; the old manual entry remains. EFI free space is 285,007,872 bytes. Installation itself did not select an entry or reboot. One separately guarded, bounded 022 boot attempt has now been launched; guest results remain pending.

## Actual result (closed; do not rerun)

The single run completed on 2026-11-13, 13:47:21–13:50:13 UTC, returning to Ubuntu boot ID `4b534f19-ffa1-457b-bb4f-46d274c23f48`. All 59 exported evidence files matched remote hashes; retrieval used `ro,noload` and unmounted the original evidence partition afterward. The configured target termination was observed.

The original SceneBoard process (PID 3373) now runs, resolving the earlier fatal private mount failure. However, all three genuine 160×256 captured scanouts remain entirely black. **Desktop and physical-input acceptance remain false.**

SceneBoard repeatedly fails to load `libmapper_service_1.0.z.so` and `ohos.hdi.display.buffer.v1_0.IMapper`. Read-only image inspection confirms the original library exists at vendor `/lib64/passthrough/libmapper_service_1.0.z.so`; the 022 `/system/lib64` bind hides it. Restoring the original vendor directory also requires retaining the four existing MateBook EGL/GLES providers instead of exposing the original Mali symlinks. This motivates the separate 023 candidate; it is not a success claim for 022.

Post-return verification confirms the four original image hashes, unchanged firmware, Ubuntu default, manual entry, unmounted LAB partition and the then-requested disabled/inactive timer. Of 104 prior EFI files, 103 are unchanged; only the boot-managed random seed rotated. Those historical results remain immutable. The user reauthorized Ubuntu screen-off on 2026-11-14; that policy change applies to subsequent work only.
