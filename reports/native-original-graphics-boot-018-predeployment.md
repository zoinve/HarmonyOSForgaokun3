# HarmonyOS crash collection 018 — deployment blocked

Scope: the user's two **HarmonyOS** crashes, not Ubuntu crash reports.

- Candidate 018 builds successfully; nine artifact hashes pass the read-only candidate test. Original module/graphics/service credentials and the 017 input gesture are retained.
- Adds bounded original fault-file exports under `/data/log/faultlog` and `/data/log/hiview/stack` at samples 2, 5, 8 and 11, including byte offsets, completion and change indicators. Symlink entries are not followed. Exports are limited to 64 files and 8 MiB per sample, 2 MiB per file.
- Initrd SHA256: `630e074a61073ee461e3c7b297de4046ffde3a4a7009a3f5173738cbecd1a933`.
- Staging failed because SSH to `192.168.10.128:22` timed out. Two ICMP probes also failed. Router DHCP lease still assigns `192.168.10.128` to `ubuntu`; no alternate address was established.
- No remote staging, EFI cleanup/install, one-shot selection or physical trial was completed for 018. Native guard checks remain pending.

Existing 017 evidence confirms `bluetooth_service` PID 465, UID 1002, SIGABRT at approximately 49.78 seconds. A second application crash and either root cause are not yet established. Volatile target crash files from that completed trial were not retained; do not claim they were recovered. Ubuntu crash investigation was a scope error and is not a basis for this repair. No Ubuntu repair was performed.

Resume with staging 018 when the device is reachable, then verify guards, install the counted entry and run exactly one new capture trial. Preserve completed 017 and every existing report. Extract complete fault files with hashes before choosing a fix; truncated or changing exports must be labelled, not treated as complete crash reports.
