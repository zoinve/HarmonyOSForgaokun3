# Native Battery Module Run 131

The single boot on 2026-11-16 loaded huawei_gaokun_battery successfully and
bound huawei_gaokun_ec.psy.0 to huawei_gaokun_battery.psy. Its real
gaokun-ec-battery supply reported present=1, capacity=98, status=Full,
voltage_now=8297000 microvolts and current_now=0 microamps. The EC adapter
reported type USB and online=1. No temperature node was reported.

This establishes the battery kernel path in the diagnostic guest, not Battery
HDI or UI acceptance. The unchanged seed hash/copy operation exceeded its
12-second probe limit. The launcher correctly refused the incomplete loop
setup before starting original HarmonyOS services. No desktop regression can
be inferred from a run that never launched the original runtime.

The standard reader refused the absent desktop snapshot before exporting any
evidence. The separate early-exit reader retained physical-serial and original
UDID digest scanning, including the digest from hash-verified prior run 130.
It exported 63 files whose hashes all matched; the LAB partition was mounted
read-only with noload and unmounted in finally. No second boot was attempted.

Post-return verification passed for Ubuntu current/default, firmware, four
original images, manual entry, enabled/active screen-off timer and all prior
EFI files except normal random-seed change and authorized archived removal of
entry 124. At this checkpoint the retained experiments were 130/131.

Next candidate 133 uses the independently built real EC module 132, whose only
source change is the power-supply registration name battery, matching the
unchanged original Battery HDI discovery contract. This is a real kernel
power_supply registration, not a synthetic file or reported hardware reading.
The original kernel image/source/config, EC access and charging code are
unchanged. The existing seed content/hash remains unchanged; only its probe
limit increases to 36 seconds within the existing diagnostic budget. New
sysfs snapshots are read-only and preserve missing-value errors explicitly.
