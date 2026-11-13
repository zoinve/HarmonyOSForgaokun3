# Foundation log query 078: command failure preserved

## Actual result

The independent verifier completed once and preserved the original graph, real
ashmem module, original identities and permissive policy mode. It checked the
12 provider files, initrd, virtual kernel, all three complete SDK images, prior
native evidence and actual virtual-frame pixels. Hotplug returned; no Foundation
critical fault or guest reboot was observed. Desktop readiness remains false.

All three Foundation queries targeted the actual PID1178, at samples24/30/41.
Their child wait statuses were zero, but the original tool printed:

`Mutlti commands can't be used in combination [CODE: -31]`

Thus **the Foundation logging attempt failed**. No absence of Foundation errors
can be inferred from these outputs. The command incorrectly combined `-x` and
`-z`; checking that both switches existed in the original usage was insufficient
to establish that they could be combined. The completed 078 source, raw output
and verification record remain unchanged. It was not rerun.

The same normal original `bm` and `aa` requests also retained their real business
failure text despite zero process exits; no permissions, tokens, service
identities, authentication or startup-guide behavior were altered.

## Evidence

- `reports/original-graphics-boot-078-independent.json`
- `reports/baremetal-sdk-original-init-qemu-078/`
- `reports/original-graphics-078-verification-output.txt`

## Correction in a fresh experiment

079 removes only `-x` from the Foundation tail query, retaining original
`hilog -z 200 -P <actual-foundation-pid>` and its 12-second bound. A new offline
regression test requires tail to be the only command in this helper; both tests
failed for missing implementation first, then passed. The new verifier explicitly
reports any repeated command-combination error instead of treating exit0 as
query success.

079 was prepared and launched once; outcome is pending automatic completion at
the time of writing. The original service graph, providers, desktop requests,
480-second VM bound and QMP capture schedule are otherwise unchanged. Everything
is isolated to the WSL virtual machine: no MateBook SSH, host module loading,
Ubuntu boot/security/screen change or physical display experiment occurred.
