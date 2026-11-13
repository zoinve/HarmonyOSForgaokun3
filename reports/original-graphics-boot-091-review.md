# Original graphics/account regression 091

## Verified outcome

- The fresh, private **8 GiB disk-backed sparse test volume** retained
  8,097,726,464 / 7,850,651,648 / 6,985,760,768 available bytes at samples
  24 / 30 / 41. No host device or existing userdata was attached.
- Genuine accountmgr PID1306 logged `Insert account 100 to database succeed.`
  at 08:05:04.105. This establishes that insert, not complete account activation.
  The earlier insufficient-storage message was not seen in these query excerpts.
- Original Foundation later processed SceneBoard metadata: `rdb SaveStorageBundleInfo
  -n com.ohos.sceneboard` at 08:06:30.460, followed by user100 resource processing.
  This is not installation-complete or launch evidence.
- The earlier original `bm` and `aa` requests still reported business failures,
  including aa10108101, despite child exit status zero. Their generic explanations
  are not root-cause evidence.
- Real QMP frames remained non-desktop: 120s had 16 nonblack pixels; 240s, 360s
  and 450s were entirely black. All were 1280x800 and independently compared
  between raw PPM pixels and lossless PNGs.

No Foundation critical-fault or guest-reboot marker was observed within the 480s
bound. Service readiness, desktop and physical scanout remain unverified.

## Evidence and preservation

- `reports/original-graphics-boot-091-independent.json`
- `reports/baremetal-sdk-original-init-qemu-091/result.json` and frame artifacts
- Serial SHA256: `161f82890dc8eaf5ebbe4be4f9c87b79e170d66b3c5596214a39263b1349fda7`
- Independent 8 GiB retained-volume SHA256:
  `007a8727686ddbdb7c753fd8d96cbfaf213b524a214f4c49f23d6ec132f81037`

Independent verification checked all three full original SDK images, kernel,
initrd, 12 injected provider files, genuine ashmem module, configuration-query
helper and 378 earlier native raw files. Original account/database creation,
credentials, policy and signature/storage checks were retained. SELinux remained
permissive in the guest; no Ubuntu or MateBook operation was performed.

## Verification corrections

The first independent check refused old090 frame paths. Its output remains in
`reports/original-graphics-091-verification-output.txt`. A second defect found
before successful verification would have shadowed the parent full-artifact
result with the volume-only subprocess result. Both were reproduced by failing
offline tests, corrected only in the then-uncompleted091 verifier, and followed
by five passing tests. The successful fresh output is
`reports/original-graphics-091-verification-output-002.txt`. No VM, preparation,
raw artifact or completed earlier verifier was rerun or overwritten.

## Next experiment

092 retains the same original services and 8 GiB test capacity, moves genuine bm/aa
requests later than the observed SceneBoard preinstall activity, and observes
later processes, service logs and actual virtual scanout. It does not assume
that timing explains the remaining failure, force-stop startup guidance, create
account/DB records manually, or relax legitimate checks. Runtime is pending.
