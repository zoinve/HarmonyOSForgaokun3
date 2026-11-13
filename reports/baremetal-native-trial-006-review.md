# Native trial006: profile003, diagnostic009

## Verified result

The authorized one-shot009 diagnostic ran on the MateBook, then returned to the original Ubuntu kernel `7.1.0-rc3-gaokun3+`. Ubuntu boot ID changed from `89d65d38-a2e5-45da-88f1-8affc0696d8a` to `aef850b8-528a-45c9-93c7-dbbd9b0f9c35`. Immediate SSH observation started about 0.0000015 seconds into the reconnect loop; the returned Ubuntu session was observed at about 38.10 seconds. This is observation latency, not exact boot duration.

Independent checks verified the byte count and SHA-256 of all188 collected raw files: 152 prior files and36 new cumulative snapshots, not36 independent tests. New evidence is under `native-diag-001-e1c82611-5cb0-4670-8d2f-350178c9950d`; final snapshot is `phase-036.log`. Device-tree model NUL bytes remain unchanged in raw evidence.

The actual native kernel was `7.1.0-rc3-gaokun3-el2`, with009 initrd and explicit `harmony.diag=1 enforcing=1`. Lab storage and all13 explicit module requests returned status0. The helper returned status0 and reported:

```
NATIVE_IDENTITY_READ002_PASS protocol=8 features=5 legacy_binder=1 selinux_active=1 enforcing=1 task_self=0000000000000000 task_first=0000000000000000 tokens_modified=0 permissions_modified=0 policy_loaded_by_probe=0 transactions_not_tested=1 desktop_not_tested=1
```

## Hardware retained

- Actual clock, combo-PHY, MDSS/DPU/DSI/DP, UCSI/HPD/auxiliary bridges, SPI/Himax and Adreno bindings were observed.
- DRM initialized at1.225915 seconds; GMU firmware loaded at1.226376 seconds. `card0` and `renderD128` exist. DSI-1 is connected and advertises `1600x2560`; both external DP connectors are disconnected.
- Himax touchscreen registered as input2/event2 at1.610951 seconds. This is registration, not verified physical touch events/calibration.
- DRM observation and enumeration returned0; the final diagnostic marker remains `desktop_verified=0`. Standalone GMU and EC battery child lack driver links, as in prior working comparisons; this does not erase the actual GMU firmware/DRM evidence.

## Preservation and return verification

Installation verified all73 pre-existing EFI files unchanged. Across the reboot the only tracked pre-existing EFI change was `loader/random-seed`, from `4f93ddd2b7f53bf7be71c4c20b8e546d8f98d569710e691ff4f8e19bcc25c6ba` to `c35143c247d558f3b7f8832debd3d5417629d6e61d10341368ee0d4dcf4eb720`. Do not restore stale entropy or claim every EFI byte was unchanged after reboot.

The independent return verifier confirmed the original persistent Ubuntu default, no pending one-shot, exact consumed009 entry, and enabled/active automatic screen-off timer. Its display runner refuses all setters: the active GDM session was already logically off, unchanged by verification. Service Result=success and ExecMainStatus=0 after this real reboot. Physical screen state was not directly observed. Collection mounted the lab partition read-only.

Sources: `baremetal-native-trial-006-evidence`, `baremetal-native-trial-006-collected/collection.json`, `baremetal-native-trial-006-independent-verification.json`, and `baremetal-boot-entry-installed-006.json`.

## Scope and next step

This verifies native profile003 legacy Binder and initial SELinux enforcing state while retaining display/touch enumeration. No SELinux policy was loaded in this diagnostic; therefore this is not original-policy authorization, native HarmonyOS userspace, physical scanout, touch interaction or GPU rendering proof. Earlier genuine SDK services and Binder sender identity were observed separately in QEMU; earlier OHOS Mesa rendering ran on Ubuntu. Those evidence sets must not be conflated.

Archive/remove only this consumed diagnostic entry after verification, retaining assets and all raw logs. Next investigate a bounded offscreen OHOS Mesa test on this actual native kernel, without replacing Ubuntu libraries or changing the persistent boot default. HarmonyMac is the confirmed reference; the second user-supplied reference remains unidentified in the retained context and is not claimed to have been reviewed.
