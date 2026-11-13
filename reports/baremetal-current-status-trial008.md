# Current status after native trial008

- **Native hardware / ABI:** legacy Binder protocol8/features5, active SELinux initial enforcing1, connected 1600×2560 DSI connector and Himax input registration passed. No policy or identities changed by diagnostic probes.
- **Native GPU + OHOS Mesa:** unchanged fence executable passes FD690 shader pixels, native fence and a second GBM-device DMA-BUF import/map under our own kernel. Mesa003's explicit `allow-kcmp=enabled` resolves the old fallback warning in the exercised native sandbox, following old-object RED/new-object GREEN and Ubuntu GPU tests. Only five library records changed; see `baremetal-native-trial-008-review.md`.
- **Original SDK services / policy:** separate QEMU original-init boots reached genuine SAMGR; PING and authentic native-type-1 reply identity passed under the SDK-selected developer policy. Earlier original SDK nested IPC tests lacked active SELinux. Neither scope is a full native service boot.
- **Not claimed:** bare-metal HarmonyOS desktop, physical display/input interaction, loaded-policy GPU authorization or complete service readiness. Legitimate SA List/Check authorization denials were not bypassed and no identities copied or invented.

Ubuntu returned with boot ID `7d801586-cb86-4983-ab3f-5e3f249b01df`; all 264 raw logs verified. Ubuntu remains default, GDM is already logically off and the screen-off timer is active. Cleanup005 archived/removed only consumed011; all other 82 EFI files, original images and logs were preserved. Keep the newly rotated random seed and use fresh numbers/baselines for future experiments.

Next integration boundary: the OHOS allocator/composer and display-service contracts, rather than repeating successful offscreen GPU tests. HarmonyMac reference is confirmed; the second user-provided reference remains unidentified, not replaced by an assumed project.
