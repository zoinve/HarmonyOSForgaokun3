# Read-only SDK system test 025

## Why this test

Profile 003 and QEMU 024 verified real token/Binder positive and negative checks with the original production policy enforcing. This does not establish a working SDK service boot. Earlier original-SDK IPC/callback tests used a different kernel configuration without active SELinux.

The production policy permits an **exec transition** from init to samgr, but not a direct dynamic transition. The original image and its file-context configuration both label `/system/bin/samgr` `u:object_r:samain_exec:s0`. The binary-policy audit permits that type as a samgr entrypoint. No relabeling or policy amendment is warranted. These are static policy facts, not a successful service execution.

Evidence: `baremetal-sdk-system-labels001.json`, `baremetal-sdk-samgr-exec-audit-001.json`, and `baremetal-sdk-policy-roles-001.json`.

## In-progress preparation

`build-baremetal-sdk-storage-test-004.py` builds a separate QEMU-only console kernel, adding VirtIO MMIO and block transport (and its SG_POOL dependency if needed). It preserves the board profile, security settings, source changes, and every existing numbered output. A launched build is not a successful build; its result and preservation guards must be checked when it completes.

The build completed in 242.27 seconds. Exactly `CONFIG_VIRTIO_MENU`, `CONFIG_VIRTIO_MMIO`, and `CONFIG_VIRTIO_BLK` changed from disabled to built-in; no SG_POOL change was necessary. The test kernel is 18,086,400 bytes, SHA-256 `5968eea1728b4edd2a9bc898ef3c2fb39cf0e3ffbcb5f686b318c90be601604d`; test config SHA-256 `e7b98bc2ab4080e49e1e3b0316a6e8da041693c04895190fb5200b43a172fc2e`. Independent verification checked the artifact, both parent configs, the parent test kernel, critical source/driver hashes, and local/WSL result equality. See `baremetal-sdk-storage-test-004/independent-verification.json`. This is still a QEMU-only artifact, not a board installation.

`prepare-baremetal-sdk-system-read-025.py` adds bounded block-device discovery and read-only filesystem inspection to the already verified 023 enforcing-policy/identity fixture. The actual generated C compiled with `-Wall -Wextra -Werror`; executing it outside PID 1 returned 77 before mount/device operations. Preparation and QEMU payloads compile. No runtime mount result is available at this point.

Preparation subsequently completed: the static ARM64 init is 785,784 bytes, SHA-256 `a9e27b32c926b0b6fd258d8fecc93e19c4a99eb5bfacd0fa38e4c13183fe0f65`; generated C SHA-256 `bd4781fcfc354c85a118bbb1243bfb00359dc3b9f60ed81c86be35bcd2bdd267`. Its copied production policy remains SHA-256 `3119d6aae760a6d692459ce9d83aeb6354301bc1fb9b084d005664f6a543d8e5`. A fresh local check confirmed the current generated source matches the preparation manifest; all three new Python launchers and generated payloads compile. These checks do not establish runtime success. See `baremetal-sdk-system-read-025/result.json`.

## Runtime acceptance criteria

- The SDK system image is attached using QEMU `readonly=on`, with a streaming whole-image SHA-256/size check before and after the run.
- The guest verifies `BLKROGET=1` and mounts ext4 with `ro,nodev,nosuid,noexec,noload`: no journal replay, image mutation, or service execution.
- Original policy, enforcing mode, authorized init transition, and earlier identity positive/negative checks remain required.
- Under the original production init policy, verify the actual samgr xattr and ELF header from the original filesystem.
- Failures retain their serial logs and numbered results; no permissive fallback or permission grants are introduced.

No Ubuntu change, physical reboot, service startup, original-image replacement, download, or board-profile installation is part of test 025. A passing result will establish read-only filesystem/label integration, not HarmonyOS desktop readiness or a complete service boot.
# Runtime and independent verification

Trial 025 completed with the unchanged production policy enforcing, actual identity-device positive and negative checks passing, and the original `samgr` ELF and `samain_exec` label readable from a read-only block device mounted `ro,noload,nodev,nosuid,noexec`. This did not execute any SDK service.

Independent verification in `baremetal-selinux-qemu-025/independent-verification.json` checked both prepared files, the test kernel, local/WSL result and serial equality, and the entire original system image. The image remained SHA-256 `19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3`; serial SHA-256 is `4d6e8824a663643259b2e5afd29b56be467be6a7067a8fc58fa4a64a2ed8cffe`.

Follow-up 026 separately tests bounded original-executable domain entry, not service readiness. It removes only the guest mount's `noexec` flag after the 025 checks, retaining a read-only QEMU backend and `ro,noload,nodev,nosuid`. It uses the original configured UID/GID and supplementary groups, a policy-authorized exec transition, and no fabricated native token or policy edits. Ubuntu and the original image are not modified.
