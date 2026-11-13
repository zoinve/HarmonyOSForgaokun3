# Candidate014: private cross-process DMA-BUF and native-fence diagnostic

## Verified preparation

- Archive: 31,260,248 bytes, SHA-256 `801eaaf844aea65d3d57df7350b488ebbd8793c3187fd6666e283e5c7960455b`.
- Independent archive verification preserves all 620 inert-parent records, including bytes, mode, UID and GID. Compared with candidate011, the record set is identical and **only** `opt/native-mesa-001/probe` changes.
- Kernel, DTB, modules, diagnostic init, identity helper, render-only launcher and all eight runtime libraries remain unchanged from their previously verified inputs. The launcher and helper retain their diskless ARM64 refusal/cleanup evidence.
- All six staged files on the lab partition match their recorded sizes and hashes. Direct ARM64 execution of init, launcher and identity helper refuses with status77 and the expected diagnostic guard message.
- All 302 saved trial010 logs were verified locally and remotely before and after restoring only the isolated lab mount to read-write.

## What this experiment tests

The unchanged OHOS runtime and Mesa003 execute the IPC002 probe. A producer exports a real DMA-BUF and native fence over a private Unix socket to a separately executed consumer. The consumer waits on the received fence, independently opens the render device, imports the buffer, closes its received DMA-BUF descriptor and checks actual pixels. The producer also closes both transferred duplicate descriptors and validates the consumer acknowledgement and PID. The producer's existing GPU readback, independent GBM import and native-fence checks remain.

This exact probe has passed on the MateBook under the Ubuntu kernel, with independent bundle, live sandbox-policy and system-state verification. Candidate014 has **not yet** been booted under the native diagnostic kernel.

## Isolation and interpretation

The existing private PID/mount/network namespaces, UID/GID65534, empty groups and capabilities, no-new-privileges and renderD128-only device view remain. No primary DRM node, modeset, token assignment or permission-store modification is introduced. The existing 25-second GPU phase admission, 180-second best-effort deadline and 30-second reserve remain; these do not guarantee recovery from a kernel hard lock or stalled filesystem operation.

Initial SELinux enforcing state without a loaded policy is not policy-authorized GPU execution. This private transport is not the HDI wire protocol; a passing fence test does not prove the fence was initially unsignaled. This is not a compositor, scanout, touch-event, full HarmonyOS boot or desktop test.

## Boot preparation

EFI capacity is checked before installation. The 64MiB reserve will not be reduced. If necessary, only an unreferenced older diagnostic asset set will be hash-verified and archived on the isolated lab partition before removal from the ESP. Ubuntu's persistent default and automatic logical screen-off remain unchanged. Reboot, if performed, uses one-shot boot counting and immediate bounded SSH observation without an initial fixed sleep.

HarmonyMac is the confirmed user reference used for the existing graphics adaptation. The second user reference remains unidentified in the restored record; no claim is made that both have been reviewed.
