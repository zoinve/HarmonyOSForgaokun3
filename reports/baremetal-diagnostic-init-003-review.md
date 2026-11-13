# Diagnostic 003 — offline candidate review

## Scope and preserved state

Only preparation inside the isolated lab workspace is authorized. This work
does not install a boot entry, change the default Ubuntu boot, load candidate
modules into Ubuntu, reboot, or start HarmonyOS. Existing 001/002 artifacts and
the original SDK images are retained.

## Evidence behind the changes

- `baremetal-device-suppliers-002.json`: read-only running-Ubuntu graph,
  105 nodes, 236 edges, 17 offline module-name checks. Sixteen resolve; the
  running driver's name `pcieportdrv` does not resolve as a candidate module.
- `baremetal-display-input-suppliers-003.json`: candidate
  `CONFIG_PCIEPORTBUS=y` explains why an independently loadable PCIe port module
  is not required. This is a configuration check, not a successful device probe.
- Real EC ancestry includes `i2c_qcom_geni`; DSI supplier links include
  `qcom_refgen_regulator`; the real touchscreen is `himax_hx83121a_spi` on
  `spi_geni_qcom`, rather than the previously planned `i2c_hid_of` device.

002 adds the PCIe PHY phase before NVMe. 003 changes only the post-storage
module list: I2C controller, EC, REFGEN, panel, MSM, SPI controller, SPI touch.
The source-contract test checks supplier ordering and byte-identical source
outside that declaration. Neither source-contract test proves hardware success.
Keyboard/USB, firmware completeness and deferred-probe completion are not
established by this list.

## Fresh checks

- Five core tests passed: entry guards, exact storage identity, exclusive log
  directory creation, subprocess results/timeouts, non-PID1 refusal.
- Four tests against generated 003 logging code passed: multi-chunk copy and
  mode, existing-file refusal, symlink refusal, real file-size-limit failure.
- One 002 storage-plan contract and one 003 board-plan contract passed.
- ARM64 static compilation succeeded. Executing the candidate on the MateBook
  outside PID1 returned the expected refusal; no hardware path was entered.
- Packaging independently reparsed 621 entries and preserved all 620 base
  entries and the base archive. Generated source hashes are recorded in
  `baremetal-diagnostic-init-003.json`, not attributed to the unchanged local
  001 source file.

003 archive: `/mnt/harmony-lab/work/native-diagnostic-init-003/diagnostic-init.cpio.gz`

SHA-256: `829962063c9531596aad9a8db53706de3a7e3941e110f7cef6ddc063003a70a7`

## Not verified

No actual PID1 boot, candidate driver probe, physical display/input operation,
lab filesystem mount/log persistence/unmount, reboot or hardware recovery has
been tested. No HarmonyOS identity ABI patch is included; the SDK7 SPM protocol
gap remains unresolved. This diagnostic is not HarmonyOS startup.

The 180-second userspace reboot fallback cannot recover a kernel hard lock and
may interrupt a stalled log write. It is not a hardware watchdog or a verified
recovery guarantee. Existing protections are not disabled. The earlier missing
pstore and stale WINPE recovery-entry findings remain applicable.

Independent archive and unchanged-boot-configuration rechecks are recorded
separately in `baremetal-diagnostic-003-independent-verification.json` when
that read-only verification completes; they do not substitute for boot tests.
