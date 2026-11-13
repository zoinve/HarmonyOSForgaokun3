# Native original graphics 016 — real lock screen, not desktop

One native trial completed and automatically returned to Ubuntu. The only
functional change from 015 grew the fresh RAM ext4 data filesystem to 3 GiB,
using genuine online resize. No original userdata was attached.

Original SA511 published successfully, applications unpacked, and original
SceneBoard MainAbility started (PID 2257). Original RenderService 770,
Foundation 816, composer 1029 and allocator 1025 retained their original
UIDs and SELinux domains. All 12 target samples were permissive.

The real composer framebuffer capture, after successful physical commit,
produced two identical 160×256 RGB samples with 12,497 colors. Their PPM
SHA256 is `d7a930d8d38b04d070eff81c72c973e0a29b83f9d153aaee8cd6f7fb6e245abe`.
Visual review of `native-original-graphics-boot-016/scanout-sample-11.png`
shows the HarmonyOS lock screen, clock and avatar. This is **not** proof of
an unlocked desktop or working input. No fabricated image was used.

Independent verification checked all 49 snapshot hashes, real root/data,
3 original image hashes unchanged, 82 static EFI files unchanged, Ubuntu
default, cleared one-shot, active screen-off timer and unchanged Ubuntu LSM.
Normal boot random-seed rotation was recorded separately. The read-only
verifiers now accept an explicit RAM-data size (default remains 512 MiB);
the historical 003 verifier was rerun read-only and still passes.

Next 017 delivers one bounded ordinary swipe through the real Himax evdev
device, after checking its name and querying axis ranges. It does not alter
lock/authentication code, credentials, service identities or security policy.
If authentication is requested, this gesture does not bypass it.
