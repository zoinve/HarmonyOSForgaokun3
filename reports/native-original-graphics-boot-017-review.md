# Native original graphics 017 — unlocked original desktop reached, incomplete layout

## Actual result

One physical trial on the MateBook E Go completed. This was not QEMU and
not a replacement desktop. The original SceneBoard application, original
RenderService, HDF composer/allocator and real native Freedreno pipeline ran.

At observer sample 8, a single ordinary upward swipe was written through the
real `Himax Capacitive TouchScreen` evdev node, after verifying its name and
querying its axes (0..1599, 0..2559). The original input/lock stack emitted
`usual.event.SCREEN_UNLOCKED`; original `SCBDesktop` gained focus and
`SystemUIView: onDeskTopChange: true` followed. Authentication and service
identities were not modified. This is software-driven real evdev input,
**not** a verified human finger test.

The original composer's actual framebuffer was sampled after successful
physical commits. `native-original-graphics-boot-017/scanout-sample-11.png`
shows the unlocked desktop wallpaper and bottom bar, rather than the clock
and avatar of 016's lock screen. Samples 9 and 11 have identical raw PPM
SHA256 `316ee2ad07175630dc86da1966257725ae2afd599ba65a58e5b18896a9e8e2be`
and 11,664 RGB colors. These are reconstructed real RGB bytes, not fabricated
screenshots or success flags.

## Important limitation

Reaching the original unlocked SceneBoard desktop does not make this a
complete usable port. Logs explicitly report desktop layout initialization
failure and missing desktop-file URI; normal application icons/layout are
not established. Network, audio, suspend, persistent data and ordinary user
interaction remain unverified. The screenshot is a 160×256 diagnostic
downsample of the 1600×2560 physical scanout. It is not proof of all pixels
or all frames being correct.

The original in-guest diagnostic footer still says `desktop_verified=0`:
that program deliberately never infers success. The independent verifier
uses actual unlock/focus records and captured pixel bytes; both facts are
retained without altering historical logs.

## Preservation and reproducibility

All 49 raw snapshot hashes, genuine 3-GiB RAM ext4 data, original process
UIDs/domains, native Mesa maps and 12 target SELinux permissive samples are
checked independently. Original system/vendor/sys_prod image hashes are
unchanged. Original userdata was never attached. The trial automatically
returned to Ubuntu boot ID `6f2729e7-1a53-4784-98cf-c59634313817`.
Ubuntu remains the persistent default, one-shot is cleared, automatic
screen-off is active, LAB is read-only/noload, and Ubuntu LSM is unchanged.
83 static EFI files were unchanged across this boot; boot seed rotation
was recorded separately.

Installer reclaimed only the unreferenced duplicate 006 EFI initrd after
matching its retained staged original hash. Numbered trial evidence and
original images remain. Cleanup 002 separately journals removal of spent
011..016 boot entry files, retaining current 017 and unrelated Ubuntu entries.

Current test remains a bounded transient adaptation environment, with a
180-second outer return deadline and fresh RAM data on every new candidate.
Do not rerun completed 017 or overwrite its logs. Persistent installation
and removal of the automatic return have not been performed.
