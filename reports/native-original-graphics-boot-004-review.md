# Native original graphics 004 — DAC startup failure repaired

## Actual native result

One new physical boot completed and automatically returned to Ubuntu.
Trial run: `/mnt/harmony-lab/native-original-004-52ca9539-c615-44a2-a9b0-c35378982b03`.
Returned Ubuntu boot ID: `99628731-369e-41b3-9678-c03d25e74a01`.
All 49 collected raw snapshots pass SHA256 verification. The original 001–003
trials and their numbered evidence were not rerun or overwritten.

The isolated target child now resets umask to 022 before the original bootstrap;
the outer diagnostic process retains its private 077 mask. Actual pre-init stats
show `/system`, `/vendor` and both overlay upper roots are now 0755, root:root.
Original `sa_main` and musl interpreter remain 0755, root:2000. No original
service executable, identity, capability list, sandbox or critical-service
failure handling was replaced or relaxed.

The earlier recorded `execv ... errno 13` failure does not appear in the final
captured log. Original `storage_manager` PID 31 is present in samples 2–11,
rather than repeatedly exiting with the earlier exec failure.

| Original service | Namespace PID | UID | Original SELinux domain | Samples |
|---|---:|---:|---|---|
| RenderService | 637 | 1003 | `u:r:render_service:s0` | 3–11 |
| Foundation | 666 | 5523 | `u:r:foundation:s0` | 3–11 |
| Composer host | 920 | 3036 | `u:r:composer_host:s0` | 3–11 |
| Allocator host | 918 | 3041 | `u:r:allocator_host:s0` | 3–11 |

These PIDs are stable **at the observed sampling points**, not a claim of
indefinite stability or full service readiness. Original hilogd, samgr,
param_watcher and hdf_devmgr are also observed. `/proc/1/root/data` remains
accessible across all 12 samples, retaining the genuine namespace root fix.

RenderService maps the original librender_service, platform libc++, native
EGL bridge, Freedreno gallium, GBM backend, private Mesa NDK libc++ and real
libdrm. Composer and allocator each map their unmodified reference VDI provider.
There are 477 native Mesa mapping observations across the recorded services.
These are genuine native process mappings, not QEMU or a substitute test service.
They do **not** establish successful EGL context creation, modeset, vsync,
frame presentation, or desktop readiness.

## Remaining display integration boundary

The captured hilog excerpt includes Foundation `GetDefaultDisplayInfo: failed`
and display-power messages reporting null display information / display ID -1.
The excerpt contains no application-log entries attributed to PIDs 637, 918 or
920, so it does not identify the failed composer/display operation. Library
mapping alone is insufficient to infer that operation succeeded.

Next work should capture targeted original RenderService/composer logs and
genuine DRM connector/mode/FD state within a **new** bounded native trial,
then trace display enumeration and initialization. Do not bypass those calls,
invent boot-complete/display events, or rerun 004 to fill evidence gaps.

## Verification and preservation

- Native disposable OverlayFS regression reproduces 0700/X_OK failure with
  inherited mask 077, and 0755/X_OK success with 022. No target program, GPU,
  policy or original image was involved in that regression.
- Nine build artifacts, two real native non-PID1 refusal checks, and native
  bundle ELF/dependency/platform-C++ ABI checks pass.
- Independent runtime verifier checks all 49 hashes, actual DAC stats,
  service UID/domain evidence, native Mesa mapping and Ubuntu return.
- A deliberately altered snapshot in a disposable copy is rejected. Real raw
  snapshots remain unchanged.
- Twelve target SELinux samples are permissive (`enforce=0`), with original
  service SELinux domains present. Early policy-load audit has rolled out of
  the final kernel ring; the verifier explicitly records that limitation.
- Three original SDK image hashes remain unchanged. Loop images remain read-only;
  the writable data filesystem is the fresh RAM-backed 512 MiB loop image.
- Eighty static pre-existing EFI files pass post-boot checks. Normal boot-loader
  random-seed rotation is separately recorded, not asserted unchanged.
- Ubuntu remains the persistent default, one-shot selection is cleared, automatic
  screen-off is active, LAB is mounted read-only/noload, and Ubuntu's active LSM
  remains `capability,landlock`. A fresh separate host verification confirms these.
- The installer reclaimed only a hash-verified, unreferenced old 007 EFI initrd
  cache; its identical original build archive remains on LAB. See preboot review
  and installation journal for exact paths and hashes.

Evidence: `native-original-graphics-boot-004/independent-verification.json`,
`runtime-result.json`, `host-final-verification.json`, and `native-logs/`.
Desktop and physical frame presentation remain **unverified**.
