# Newly observed HarmonyOS 027 run: exit investigation

Inspected run: `native-original-027-d004726a-4b66-4f2b-86a5-67c1c0b49949`, distinct from the earlier collected 027 trial. The current Ubuntu boot ID is `3d7934b9-dc8a-4b16-b350-c97e7d45cfa2`; the 027 counted entry is now `+0-2`. Target filesystem timestamps reflect boot-relative time and were not used to establish wall-clock chronology.

## Findings

- Scanned all 59 retained snapshots remotely for crash signals and fault captures. Saved their SHA256 index, matching full final snapshot and deduplicated matching events in `harmony-recent-crash-028/`.
- All 14 original-init observations report `child=0 status=0`: no premature exit was observed by the diagnostic parent.
- Both `NATIVE_ORIGINAL_END` and `NATIVE_DIAGNOSTIC_END` are present. Final captured kernel time is approximately 74.9 seconds.
- The installed candidate's source explicitly observes 14 times at five-second intervals, then kills the diagnostic target namespace, saves the final evidence and calls `reboot(RB_AUTOBOOT)` (`native-original-graphics-boot-027/init.c`, lines 306–317 and 395–402). The observed return matches this deliberate short-trial shutdown, not an observed kernel or original-init crash.
- No captured SIGSEGV/SIGABRT exit, panic, GPU hang or crash stack was found. Fault directory exports at samples 2, 5, 8 and 11 each contain zero files. This does **not** exclude every application failure: logs are filtered/bounded and volatile data is gone after return.
- Several SIGKILL exits correlate directly with SAMGR on-demand service-stop requests. The observer's SIGALRM is its own diagnostic deadline, not evidence of an application crash.
- Current-host pstore is unavailable, not a verified empty persistent panic store.

## Scope and preservation

No new HarmonyOS boot, target changes, security changes or repair was performed. The LAB partition was restored to its established read-only/no-journal-replay mount solely to retrieve existing evidence. No Ubuntu crash reports were used. Existing trial logs and images remain untouched.

The confirmed problem explaining an apparent automatic “crash back to Ubuntu” here is that 027 is still a short diagnostic entry, not a persistent interactive installation. A longer interactive session requires a separately designed candidate and explicit recovery/evidence handling; no timeout or safety guard was silently disabled during this investigation.
