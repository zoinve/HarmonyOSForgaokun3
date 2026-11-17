# Original broker startup and first-frame timing audit

This is a read-only follow-up to closed experiment 035, not another operational attempt. No original image, service profile, policy, permission or identity was changed. A genuine commercial desktop remains unverified.

## Confirmed broker failure

Original init selected `/vendor/etc/selinux/prebuild_sepolicy/policy.31` at guest 4.712233 seconds and subsequently logged policy-load success. Seven attempts to start the original `bms_broker` failed while setting its configured context `u:r:anco_service_broker:s0`, with error 22 (`EINVAL`). These failures occurred at approximately 38.932, 42.941, 46.949, 50.968, 54.983, 58.994 and 63.005 seconds.

The immutable original service configuration specifies the broker identity and context; its profile publishes SA 66816. Existing SAMGR and SceneBoard logs link unavailable SA 66816 to missing-package fallback waits. SceneBoard's main thread spent approximately 17.6 seconds in the AppGallery launcher query and four seconds each in Settings and Camera queries. Installed-package queries completed in milliseconds. This establishes a concrete failed dependency, not proof that it accounts for the entire black screen.

Read-only inspection of the packaged policy found no `anco_service_broker` identifier in either precompiled policy or the inspected system/vendor CIL files, including compatibility and developer variants. The selected policy is 1,059,024 bytes, SHA256 `1150198657a3d703aaf079ca4e6688dcdd15b1c5ecd04eca4c0cbeaf5ae46737`. The packaged system/vendor policy fingerprint files match exactly: `8d3a5d92419051a71c8acba76411745037e7b698ba91d9747e3db597c4e5ffcb`.

Permissive mode does not make an undefined security context valid. Removing the original context, substituting another service identity or inventing a new policy domain would not be a verified restoration of the original service and has not been done. An authentic matching policy has not yet been located.

The original payload's 44,319-row state-label inventory was also inspected read-only. It contains Linux compatibility SELinux libraries and a historical HDF shim, but no broker-domain label or apparent HarmonyOS policy file. This inventory is not a complete content search of the compressed state seed. The secondary Linux compatibility broker is not the original BMS broker and its shortcuts are not an acceptable substitute.

### State-seed archive follow-up

The compressed state seed was subsequently streamed read-only without extracting files. All **44,929 tar entry names** were inspected (6,125,803,520 decompressed bytes read). No entry name matched `prebuild_sepolicy`, `policy.31`, `system.cil`, `bms_broker` or `selinux-config`. A bounded content search of small configuration/script files found `bms_broker` only in two native-token JSON records, not a SELinux policy definition. One record has a carriage return in its parent directory name; it was preserved as data, not normalized or applied.

This closes the unsearched archive-name lead, not every possible content search: files over 1 MiB, other extensions and excluded Linux library/documentation/package paths were not content-scanned. No authentic matching policy was located by this search. Search scope and counts are recorded separately in `commercial61-native-035/state-seed-policy-search.json`; token contents were not copied into the report. The payload hash is referenced from its existing extraction manifest, not a repeated full-image hash operation.

## Timing correction

The latest completed scanout observed in 035 was black at guest **74.871892 seconds**. SceneBoard's first `ArkUi flush first frame messages.` log followed at **75.125 seconds**. Consequently the evidence must not be described as a black scanout of content committed after that first-flush message. Nor does the message establish that a later desktop frame reached the display.

The confirmed GL readbacks remain valid evidence of sampled black pixels at their recorded times. The original frontend/Mesa state comparison and zero sample-buffer configuration remain unchanged findings. None alone establishes the eventual desktop content or its absence after the first flush. Next investigation must follow actual application transactions and RenderService presentation, retaining original authentication, sandbox and permission checks.

Public source cross-check: OpenHarmony `OpenHarmony-6.0-Release`, `arkui_ace_engine/frameworks/core/pipeline_ng/pipeline_context.cpp`, logs this message at line 820 **before** calling `FlushMessages()` at lines 826/832. `FlushMessages()` delegates to `window_->FlushTasks(callback)` at line 1126 and can return early on the freeze-message path. Thus the message itself is not an acknowledgement of RenderService receipt or successful presentation. This public-source ordering is a reference finding, not proof that the commercial binary is byte-identical or that its freeze path was taken.

Source: https://raw.githubusercontent.com/openharmony/arkui_ace_engine/OpenHarmony-6.0-Release/frameworks/core/pipeline_ng/pipeline_context.cpp

The exclusive raw-derived `commercial61-native-035/broker-policy-timing-audit.json` preserves source-log hashes, the seven exact context failures, selected-policy record and first-flush ordering. Original runtime evidence is unchanged.

## Preservation

All operational diagnostics through 035 remain closed; their numbered logs and JSON are immutable. This audit does not change the last verified standard Ubuntu boot `ae587799-0092-448b-9f44-6d8822c91e71`, default boot, enabled/active screen-off timer or original images. Hardware adaptation remains after genuine original-desktop acceptance.
