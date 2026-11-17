# Native173 input baseline revalidation179

Date: 2026-11-16. Analysis only; no native boot or target change.

## Analyzer Correction

The148 analyzer joins MMI descriptors against touchscreen node names gathered
across all samples. If event numbers change, a descriptor from a different
observation can therefore be attributed to an earlier touchscreen identity.
It also permits module-live observations from separate or incomplete samples
to combine into a positive aggregate.

`analyze-input-baseline-179.py` instead requires matching begin/end stages and
same complete observation for device name and MMI fd, or all three storage
module states. Stage/timestamp-mismatched metadata is excluded. Incomplete and
mismatched-end observations are counted but not admitted. The148 analysis entry
point is also corrected so its downstream callers use same-complete-sample
joins. Historical reports/results remain unchanged;179 is the revalidation.

Six tests pass, including cross-sample event-node reuse, incomplete records,
mismatched end stage, wrong metadata stage/timestamp and split module states.
This is an analysis correctness fix, not a physical input-driver repair.

## Revalidated Native Evidence

`input-baseline-179/result.json` records the173 run and188 rehashed retrieved
files. Phase172 contains four complete observations and no rejected fragments:
8.738,32.138,53.784 and74.390 seconds after boot.

- The Himax touchscreen reports X/MT_X0..2559 and Y/MT_Y0..1599 in each sample.
- At32.138,53.784 and74.390 seconds, original MMI holds the touchscreen's real
  evdev node in the same observation. No cross-sample join is needed.
- All three storage modules are observed live together in a complete sample.
- The pre-service observation has no MMI touchscreen descriptor, as expected
  for that sample; it is not silently converted into positive acceptance.
- Event2, MMI PID844 and fd23 are historical observations, not selection rules.

Keep the native coordinate transform: Ubuntu boots a different DTB and its
portrait axis ranges do not justify replacing the native landscape ranges.
Outer root:root0600 permissions are not the original service-root permissions;
the independent152 service-namespace analysis remains relevant to that question.

## Remaining Verification

Metadata coverage ends at74.390 seconds; it is not a continuous desktop-session
trace. No physical corner accuracy, drag, multitouch, external USB HID hotplug
or storage file access is accepted by179. Do not change kernel transforms or
input ownership solely to address the unrelated Settings installation failure.
Working173 runtime, persistent desktop data and originals are unchanged.
