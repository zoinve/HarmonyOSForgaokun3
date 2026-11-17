# Commercial desktop 021 — correct the actual `aa start` arguments

## Scope and reason

020's real captured CLI output rejected the added `-u 100` option, while returning exit code 0. The earlier inference from strings in the executable was incorrect. This attempt restores the reference's ordinary command:

```sh
/usr/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard
```

It leaves user selection and authorization to the original commercial Ability Manager. No account is fabricated or force-activated; no guide is stopped. The prior original HUKS ordering, stock account-service retry and framework/package readiness checks remain. The startup diagnostic now says `user_selection=aa_default`, not an asserted user ID. A CLI exit code is only a diagnostic, never desktop acceptance.

## Built and checked

The bootstrap binary is byte-identical to 020. Only the desktop launcher contents and the unique outer diagnostic run identifier change. Original commercial service binaries, package checks, seccomp filters, sandbox checks, identities and the four read-only source images remain unchanged. The existing own MateBook hardware backends are retained; no SDK userland is added.

The ordered initramfs chain remains commercial 001 base → 017 directory preparation → 016 hardware files → the new 021 final overlay. Exhaustive ordered member/parent/byte/mode verification passed. The new overlay is 704,533 bytes, SHA256 `e5e82f95d333269e056dd863818ca8e02b8da582e80997090154d582da37dc4e`.

Offline regression tests passed for the exact reference argument vector, real child cleanup deadline/memory admission, and strict captured PPM decoding. Source checks retain strict trusted SSH host-key checking, original source-image paths and the disabled/inactive custom screen-off timer. EFI installation restores the **32 MiB free-space reserve** following the separately authorized, backed-up cleanup; no additional old files are deleted.

## Runtime status

The single controlled run completed on 2026-11-13, 13:13:44–13:16:11 UTC. Ubuntu returned with boot ID `96723015-d912-44a7-8960-8cdd786d2b6a`. All 59 exported files matched their remote hashes; retrieval used a read-only `noload` mount and unmounted it afterward. The configured target termination is recorded. The test retained 8 GiB volatile data with live memory admission, a 90-second target budget, 15-second bounded cleanup and 210-second independent software deadline. These do not guarantee recovery from a kernel/device shutdown hang.

The original CLI now actually reports `start ability successfully.` Foundation submits the SceneBoard load request. However, the original AppSpawn child fails its required individual sandbox bind: the source `/data/local/tmp/l410-sceneboard-r18-passthrough-v2` is absent, producing `errno:2` and hook result `218103816`. Its second required development source, `/data/local/tmp/l410-fp-completion-v3/SceneBoard`, is also not provisioned by the immutable commercial images/fresh data environment. Neither developer overlay is a reason to disable sandbox checks or fabricate guide/fingerprint completion.

There is no SceneBoard process acceptance. All three genuine captured scanouts are black. Package installation, working GPU operations and successful CLI submission are **not a working desktop**. The next bounded correction normalizes only those two sources to already available read-only libraries and the original commercial SceneBoard package, retaining destinations and fail-closed checks.

Post-return verification confirms all four commercial image hashes, Ubuntu default, no one-shot selection, unchanged firmware entries, retained manual HarmonyOS entry, unmounted LAB partition and disabled/inactive custom screen-off timer. Of 102 pre-existing EFI files, only the boot-managed random seed rotated; it was not restored. Numbered logs and JSON results remain unchanged.

Acceptance requires the original SceneBoard process and actual non-black desktop scanout, not package installation, a GPU submission, Ubuntu becoming reachable, or a successful shell exit alone. Earlier numbered logs and JSON evidence are preserved.
