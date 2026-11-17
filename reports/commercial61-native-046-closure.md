# Commercial 046: no persisted target runtime evidence

The single boot was requested at 2026-11-14T13:13:08.969166Z and Ubuntu
was observed again at 13:14:20.544609Z. The new Ubuntu boot ID is
720d2265-a928-4b2b-a6b8-eea2657d99f1. This is not proof that the target
ran, reached its timeout, or installed any original-service probes.
Do not repeat this numbered operational experiment.

The protected retrieval command reached the device but failed its exact-one
run-directory assertion with an empty match list. A subsequent ro,noload
inspection confirmed no commercial61-native-046 directory; commercial 045
is present. Both inspections unmounted the partition. No target trace,
kernel panic, scanout, or desktop result is available from this run.
The inspected Ubuntu pstore paths do not exist; this does not exclude a panic.

The return verifier completed successfully: Ubuntu current/default preserved,
107 prior EFI files unchanged, normal loader/random-seed change, authorized
removal of entry 044 accounted for, firmware and original commercial images
unchanged, evidence partition unmounted, original manual entry retained,
and the screen-off timer enabled/active.

Build inspection found that 046 rebuilt Image only. Its copied nvme.ko and
Module.symvers retain November 12 timestamps while vmlinux was rebuilt on
November 14. The new configuration enables TRACEPOINTS, TRACING, BPF_EVENTS,
and EVENT_TRACING; include/linux/module.h contains conditional module fields
for these options. Consequently the old module set cannot be assumed ABI
compatible despite the unchanged release string. This is a concrete build
defect and a possible explanation for an early storage-probe failure, not
runtime proof of the actual failure cause.

An independent 047 build rebuilds Image and modules together with unchanged
046 configuration and Binder source. It preserves all 046 files and does
not deploy or reboot the device. Desktop and interaction remain unverified.

The completed 047 module audit confirms both preserved 046 nvme.ko and
phy-qcom-qmp-pcie.ko have 1152-byte .gnu.linkonce.this_module sections,
whereas rebuilding with the trace configuration produces 1216-byte sections.
The loader explicitly rejects a section-size mismatch with ENOEXEC. This
proves the old modules are incompatible with the trace configuration; it
does not independently prove which error occurred during the unlogged boot.
Evidence: reports/native-trace-kernel-047/module-abi-audit.json.
The matching Image and modules have been built and installed only into the
local build staging tree, not onto the MateBook. The next candidate must
replace the initrd hardware module set as well as its kernel.
