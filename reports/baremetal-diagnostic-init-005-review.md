# Diagnostic 005: offline supplier-closure candidate

## Evidence and hypothesis

Native trial 001 reached the real kernel, NVMe and isolated lab logging, but did not enumerate DRM or the touchscreen. Successful modprobe exit codes did not establish device binding.

The running Ubuntu supplier audit identified three available candidate modules omitted from diagnostic 004: `dispcc_sc8280xp`, `gpucc_sc8280xp`, and `phy_qcom_qmp_combo`. Candidate 005 loads these before `msm` and records device bindings before and after the module sequence. This addresses an observed dependency gap; it does not establish the exclusive cause of the missing display or touch devices.

## Offline artifact

- Path: `/mnt/harmony-lab/work/native-diagnostic-init-005/diagnostic-init.cpio.gz`
- Size: 24,217,165 bytes; 621 entries.
- SHA-256: `f3e990cb4215c551f086a851ba767cd7411e686a909203fd9a20ae09a2de5a16`
- All 620 base entries and the original base archive remain unchanged.
- Archive roundtrip and actual ARM64 non-PID1 refusal checks passed during packaging.
- Earlier numbered artifacts remain preserved.

## Test scope

`baremetal-diagnostic-005-tests.txt` records 17 targeted passing tests: core guards/process handling (5), budget policy (3), actual probe budget admission (3), actual snapshot file handling (4), and source-plan contracts (2). Static ARM64 compilation and binding-command shell syntax were also checked. These checks are not hardware-binding or display-readiness tests.

The original mount identity checks, exclusive persistent logs, shared budget and finalization remain in place. No authentication, identity, trust, SELinux policy or watchdog protection was changed. The lab partition was restored to writable preparation mode only after all 20 trial logs matched their saved hashes before and after the remount.

## Limits and next hardware evidence

005 has not been installed as a boot entry or booted. A future separately scheduled trial must inspect actual clock/PHY/MSM/DSI/SPI binding, supplier deferral, DRM connector enumeration and touchscreen registration. The new binding snapshots are observations, not readiness signals; no automatic wait or fabricated success was added.

The exact binding command extracted from generated 005 C was also executed read-only on the current Ubuntu kernel with BusyBox. It exited 0 in about 0.017 seconds, emitted 12,759 bytes of observations with no stderr, and reached its explicit non-readiness completion marker. See `baremetal-diagnostic-005-binding-command-audit.json`. This validates the command on the current system, not its execution under the candidate kernel or its sufficiency to diagnose every deferred probe.

`baremetal-diagnostic-005-module-closure.json` records successful offline dependency expansion for all 12 explicit module requests (PCIe PHY, NVMe and the 10 board modules). Every resulting insmod file exists byte-for-byte in the actual hash-verified 005 archive. `--show-depends` was used exclusively; no module was loaded. This establishes packaged dependency availability, not device binding or full firmware closure.

The 180-second userspace reboot fallback is still best effort, not kernel-hardlock recovery. Mount, fsync and unmount can stall despite command admission budgeting. HarmonyOS and its unresolved SDK7 identity ABI are not exercised by this diagnostic.

The independent archive and boot-configuration audit is recorded separately when completed in `baremetal-diagnostic-005-independent-verification.json`. No second reboot or one-shot selection is requested by this offline work.

### Independent audit blocked by connectivity

The attempted post-build SSH audit timed out connecting to `192.168.10.128:22` before the remote verification payload executed. A single ICMP check also timed out; the local workstation still had a `192.168.10.248/24` WLAN address and the effective SSH alias still targeted the expected host with strict host-key verification enabled. This does not identify whether the device is asleep, disconnected or using a different address, and is not evidence of a diagnostic boot failure. No successful independent-verification JSON was produced. Packaging evidence above remains distinct from this incomplete audit.

After the user reported connectivity restored, the read-only audit completed successfully. `baremetal-diagnostic-005-independent-verification.json` confirms the archive size/SHA, all 13 original loader files unchanged, only the consumed `harmony-native-diag-004+0-1.conf` diagnostic entry present, and no one-shot armed. The running kernel remains Ubuntu `7.1.0-rc3-gaokun3+`. No 005 entry was installed and no reboot was requested. This supersedes the temporary connectivity blocker, not the hardware-validation limitations above.
