# HarmonyOS crash capture 018–020: diagnosis confirmed, repair incomplete

## Outcome

One independent native crash is proven: `bluetooth_service`, UID 1002, PID 467, SIGABRT at 46.999 seconds in trial 018. Three complete, unchanged original fault files were reconstructed and hashed under `native-original-graphics-boot-018/fault-files/`. They are three representations of **one event**, not three crashes. A second independent crash has not been identified. Do not substitute Ubuntu crashes or ordinary on-demand service stops.

The attempted fail-closed vendor change is **not a completed repair**. Trials 019 and 020 produced no captured SIGABRT/SIGSEGV report during their bounded windows, but the original Bluetooth upper stack still killed and restarted its service. The change must not be described as stable Bluetooth support or a fix for both user-reported crashes.

## Proven chain

018 original fault evidence:

1. HCI Reset opcode `0x0c03` is sent around 29.997 s.
2. Its 12-second response deadline expires at 41.998 s: `command_timed_out`.
3. Firmware-dump transmission also fails.
4. The original five-second restart timer calls `abort` at 46.999 s.
5. The original stack contains `raise`, `abort`, and `libbt_bluetooth.z.so` offsets `0x34015c`, `0x352d54`, `0x3531c4`, `0x356064`, Build ID `47634678e07d4973d329eae6cc6cef62`.

Read-only disassembly of the SDK vendor library shows a virtual `/dev/hwbt` transport, including successful initialization callback before transport validation and channel-open failure returning zero. The actual board has a WCN6855 serial controller; Ubuntu's existing QCA setup was inspected only, never modified. The native HarmonyOS environment does not currently provision that real transport. No evidence supports changing DRM permissions or disabling SELinux as a remedy.

019 adds a vendor adapter that rejects a missing/non-character/unopenable transport and otherwise delegates to the retained original vendor implementation. It does not forge HCI responses, successful callbacks or identities. Host regression tests prove the missing-device failure contract. It still does not port the real controller.

020 adds only explicit error-path logging to a precreated RAM trace file plus focused original logs. Actual original `blue_host` UID 3021 records:

```
NATIVE_BT020 unavailable reason=missing_virtio_transport errno=2 uid=3021 success_callback=0
```

Original logs then show `vendorInterface_->init failed.`, `TL_Startup ret : 2`, `hdiInit failed: 2`; about 4.5 seconds later, `startup_timer_expired`, `bt hidl pid is:0`, `kill bt hidl abort`. Init reaps `bluetooth_service` PID 468 with SIGKILL at 33.413 s and samgr restarts it as PID 3201. This is a real remaining failure, not normal on-demand unloading and not proof of a second independent application crash. The effect and arguments of that upper-stack kill path require further investigation; do not infer a fully understood kill mechanism from the log text alone.

## Verification and preservation

- Exactly one new physical trial each for 018, 019 and 020; completed historical operational tests were not rerun.
- Read-only independent checks validate all 147 raw snapshot hashes, original RenderService/Foundation/composer/allocator identities, native Mesa mappings, stable target root and 12 permissive SELinux samples per trial. Early policy-loading audit records rolled out of the final kernel ring and are not fabricated.
- Original system/vendor/sys_prod images remain byte-identical; original userdata is never attached. Data is a disposable real 3 GiB RAM-backed ext4 filesystem.
- Each trial returned automatically to Ubuntu. Persistent default, screen-off timer, Ubuntu LSM and unrelated firmware entries are preserved. Boot random-seed rotation is recorded separately rather than falsely treated as immutable.
- 020 leaves 80 prior static EFI files unchanged. Its only reclaimed file was an unreferenced duplicate `native-original-graphics-009/initrd.img`, verified against the retained staged original before deletion. All numbered evidence remains.
- Current Ubuntu boot ID after 020: `0002e054-19d5-4bde-bd72-bdcb6cd3a452`.

Evidence: `native-harmony-crashes-018-020-verification.json`, each trial's immutable `runtime-result.json` and `native-logs`, 018 `fault-extraction.json`, and 019/020 `bluetooth-guard.json` plus source/compiler evidence. The original report's emulator build metadata is retained as SDK metadata, not rewritten to claim a native product identity.

## Remaining work

The genuine repair requires a target-only WCN6855/QCA firmware and transport integration across the diagnostic and service network namespaces, then successful real HCI reset/initialization and a stable original Bluetooth service. L410's HCI FD-broker architecture is relevant, but its Hi1103-specific translations and power behavior must not be copied into QCA as fake success. Alternatively, a source-matched upper-stack failure-path repair must preserve honest unavailability and avoid process-killing timeouts. Neither is implemented here. A second user-reported crash still needs its own report or reproduction; absence within these short windows does not prove absence generally.

All 019/020 changes are RAM-only experimental overlays, not permanent edits to the original SDK images or Ubuntu. No Ubuntu crash repair, security change, fake success implementation, or Bluetooth-ready claim was made.
