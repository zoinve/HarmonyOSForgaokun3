# Bluetooth Sandbox Diagnosis

Date: 2026-11-17, Asia/Shanghai.

User priority: Bluetooth, then multitouch, audio, and 120Hz. Bluetooth is not
accepted as working yet. Keep the working desktop173 and Ubuntu default.

## Experiment294

The original blue_host process (outer PID1482, original UID3021) was observed
in the target PID namespace. Its maps eventually contained six segments of
`/vendor/lib64/libbt_vendor.z.so`. The file visible through its root had16104
bytes, matching the built adapter's size. This is mapping evidence, not a
claim that file size alone proves identity.

All three scoped samples returned ENOENT for both `/native-bt-broker.sock`
and `/radio261/vendor.trace` through `/proc/1482/root`. The original service
sandbox therefore cannot use the paths chosen in261 through294. This explains
the absent broker attempts and absent file traces without requiring an ABI
change. The existing original vendor view does expose the adapter library.

Source: `commercial61-native-294/runtime-evidence/raw/phase-178.log`, markers
RADIO294_HOST, RADIO294_NODE, and RADIO294_VENDOR_MAP. Logs may be losslessly
compressed; use `next-experiment/compress-historical-logs-226.py:open_log`.

The original HDI disassembly in `bt-init-contract-293.txt` keeps init's zero
return value in w0 for opcode0 (POWER_ON). No opcode patch is justified by
that sequence alone.

## Experiment297 Change

Expose the same real broker socket and private trace file using RAM-only bind
mounts beneath `/vendor/lib64/harmony-graphics`, already present in the original
sandbox view. Socket ownership remains3021 and mode0600; broker peer checking
and original service UID, groups, capabilities, and sandbox configuration are
unchanged. The trace is the same bounded private RAM file as285. Original
images, active165 and authentication logic are unchanged.

The repair follows the endpoint-placement pattern already present in local
experiment022. No simulated HCI command, completion, firmware, or pairing
result is introduced. A successful build or mounted endpoint is not Bluetooth
acceptance. Runtime results are pending at the time this report is created.
