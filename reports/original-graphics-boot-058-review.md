# Original RenderService display initialization: trial058

## Observed failure

The original RenderService ran with its original UID1003 and SELinux domain in
the permissive, isolated ARM64 virtual machine. Real bridge calls show successful
DRM discovery (`drm_open_result=0`), followed by `gbm_device=0` and
`bridge_error=0x3001`. No successful EGL initialization or desktop is established.
The guest later rebooted after its original Foundation critical-process fault;
QEMU rc0 does not mean service success.

Trial058 was executed once. Its serial SHA-256 is
`08dd230ad37282bf7755a574c9c8756fd6d527e81e2d00546d163b9519c75474`.
The independent record is `reports/original-graphics-boot-058-independent.json`.
It verifies 18 permissive-mode samples, original service identities, injected
artifacts, original SDK images and all378 earlier native raw files. Neither VDI
mapping was captured in this trial; earlier observations must not fill that gap.

## Packaging diagnosis and next experiment

The packaged GBM library embeds the runtime backend search directory
`/system/lib64/lab-virgl883/gbm`, but the isolated fixture installed its real
`dri_gbm.so` under `/system/lib64/harmony-mesa/gbm`. Its existing compatibility
alias covered `lab-softpipe-167`, not `lab-virgl883`. This runtime-loaded backend
is not discoverable from the normal DT_NEEDED closure alone.

Mesa source `src/gbm/main/backend.c` confirms that backend loading uses
`DEFAULT_BACKENDS_PATH`. Its `gbm_dri.c` calls `driCreateNewScreen3` and has real
software fallbacks; no guessed driver files or success stubs were added.

Trial059 changes only the volatile system-overlay compatibility path, adding
`lab-virgl883 -> harmony-mesa`. It retains the same EGL006 binaries, original
service credentials and policy, read-only SDK disks, and virtual GPU. Its outcome
is not assumed here. Ubuntu, the physical display and persistent boot settings
were not accessed or changed by this work.
