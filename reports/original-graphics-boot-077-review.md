# Original SceneBoard request 077

## Outcome

Original composer returned Commit=0 and its genuine hotplug callback completed,
but this is **not a working desktop**. The 240, 360 and 450-second virtual
1280x800 scanouts were entirely black. The 120-second frame contained only 16
nonblack pixels. Independent PPM/PNG decoding verified the captured pixels.

The original tools were executed without changing their credentials, tokens,
service configuration or SELinux policy:

- Sample23: `bm dump -n com.ohos.sceneboard` printed
  `error: failed to execute your command.`
- Sample29: `aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard`
  printed `error: failed to start ability.` and ErrorCode10108101.
- Both child wait statuses were zero. These are **business failures despite
  successful CLI process exits**, not evidence of a launched ability.

The generic internal-error text does not identify a permission, memory,
installation or readiness cause. Concurrent Foundation HAP reads show startup
work, not why the requests failed. No startup-guide stop, authentication bypass,
fake callback or original-service patch was applied.

## Evidence and preservation

- `reports/original-graphics-boot-077-independent.json`
- `reports/baremetal-sdk-original-init-qemu-077/` serial, four original PPMs/PNGs,
  result and capture evidence.
- The independent check verified all 12 provider files, real ashmem module,
  initrd, virtual kernel, all three complete original SDK images and all 378
  prior native raw files.
- Guest SELinux remained permissive with policy support retained. No Foundation
  critical fault or guest reboot was observed within the 480-second bound.
- Entire experiment ran in the isolated WSL virtual machine. No MateBook SSH,
  Ubuntu boot/default/security/screen setting or physical display change occurred.
  This is not a fresh observation of the host's screen state.

## Next boundary

078 keeps the same providers, original tools, service identities and isolated
virtual graph. It adds bounded tail queries of the actual Foundation PID after
the requests. The original `hilog` binary's own usage confirms `-z` means tail
(`-a` means head); no guessed logging option or fabricated decoder output is used.
078 was launched once and is pending automatic completion when this report was
written. Its eventual business/log output must be interpreted separately from
CLI exit status. Graphics and desktop readiness remain unverified.
