# Profile file-event observation: 084 build failure, 085 pending

## Scope

083's separate UID0 diagnostic returned `/usr/system/profile` and read the
genuine `installs.json`. That does not establish what the original SAMGR loaded.
085 therefore adds notification-only `fanotify` observation before original init
starts, recording the actual event PID, mask, and kernel-reported file path.

There are no permission events, permission responses, target-process writes,
profile substitutions, database creation, or credential changes. The observer
does not approve access or alter parser/registration results. Failure to install
the watch is recorded, not represented as evidence that SAMGR skipped a file.

## Preserved failed preparation 084

`reports/original-graphics-084-prepare-output.txt` records the compiler rejecting
the unavailable optional `O_LARGEFILE` macro. No 084 VM was launched. The failed
work and launcher remain intact; the preparation was not rerun.

085 omits that optional flag for this fixed AArch64/64-bit-offset build. It keeps
read-only event descriptors, close-on-exec, notification-only masks, strict
compilation, and all existing guest guards.

## Preparation and pending run 085

- Preparation completed with init SHA-256
  `669ec1eb10fc4c06c97efe8f790743a7aad76f9be5fac289458b11759191d7ec`.
- Source SHA-256:
  `e8b149f96c49d7773003b129d90664e607d73ddcfa5ccba31c75362373c10729`.
- Original policy and HDF import configuration hashes remain unchanged.
- Explicit offline safety/parser tests: 4 passed. No operational test discovery.
- 085 launched once; result pending at the time of writing. Its output is
  `reports/original-graphics-085-launch-output.txt`.

The child observer polls with a deadline and processes at most one 8192-byte
batch after reaching its outer 2048-event threshold. It reports overflow and
actual errors; absence of a captured event alone is not proof of absence of
access. Independent verification attributes events only to SAMGR PIDs with
actual original UID/domain witnesses. Open/access observations do not prove
successful JSON parsing or SA511 registration.

The working composer/Mesa/ashmem/kernel stack is unchanged. This is still a
bounded, isolated software-rendered VM with three read-only original SDK images,
fresh disposable RAM userdata, and real guest SELinux permissive mode. No
MateBook/Ubuntu operation, host monitor, physical scanout, or desktop success is
claimed. The verifier retains full image, archive, provider, capture, and prior
378-file native-evidence checks.
