# Commercial desktop 023 — restore original mapper visibility

## Cause and bounded correction

022 successfully created the original SceneBoard process but its required mapper loader looped and actual scanouts remained black. The 022 bind of `/system/lib64` over SceneBoard's `/vendor/lib64/passthrough` hid the original vendor mapper services.

023 restores that existing vendor mount source without altering destinations, required mount checks, sandbox switches, groups, identities, authentication or seccomp. Before mounting the vendor RAM overlay read-only, it copies the four existing commercial-runtime-built MateBook providers (`libEGL_impl.so`, `libGLESv1_impl.so`, `libGLESv2_impl.so`, `libGLESv3_impl.so`) into that overlay's passthrough directory. These regular files shadow the original Mali symlinks while leaving original mapper services available. No SDK userland or fabricated mapper implementation is added. The four original commercial images remain read-only.

The normal reference `aa start` command and original SceneBoard packages are unchanged. All three reference projects remain reconciled as recorded in `reference-three-projects-001.md`; Kirin-only GPU providers are not copied to the MateBook.

## Screen-off and verification

On 2026-11-14 the user reauthorized Ubuntu screen-off. The existing helper/timer were restored without reinstalling them: enabled/active, local GNOME display state read back as off. New 023 deployment and preservation guards check this state; earlier numbered disabled-timer evidence is unchanged. Per-command SSH retains the trusted `192.168.10.128` host key and address. Ubuntu default, manual entry, 32 MiB EFI reserve, memory admission and original-image hash guards remain.

Eight scoped offline regressions passed, including actual saved configuration transformation, exact vendor-helper delta, deployment screen-off policy, reference CLI arguments, bounded child cleanup, scanout decoding and the existing display helper. Tests are not runtime desktop proof. Ordered initramfs final-state bytes/modes and parent hierarchy match the full build. Chain: commercial 001 → 017 → 016 → 023. Final overlay: 704,444 bytes, SHA256 `fe6828222ae314c26fe40d6f33a4d9935daff027cdeee7a99c268cf584854716`.

## Runtime status

Installation succeeded using the audited deployment host. Both non-PID1 execution guards refused with exit 77; all 110 pre-existing EFI files were unchanged. EFI free space after installation was 226,390,016 bytes. The standard Ubuntu default, manual entry and enabled timer were retained; installation itself neither selected a one-shot entry nor rebooted. A single controlled diagnostic has now been launched; runtime evidence is pending and no desktop success is claimed.

The diagnostic retains 8 GiB volatile data, a 90-second target budget, 210-second outer software deadline and 15-second bounded cleanup. A kernel/device hang is outside a software return guarantee. Acceptance requires original service/SceneBoard integration and genuine desktop pixels, not merely mapper loading, a process or an accepted CLI request.

## Deployment host audit

The first installation was safely refused before its journal or EFI writes: the current Ubuntu entry was `ego-s4diag-20261113.conf`, not the standard entry expected by the old guard. Its logs and empty staging directory remain unchanged. Read-only inspection confirmed Ubuntu 26.04 on the same root UUID, with the standard Ubuntu entry still the persistent default.

The resumed installer pins this exact audited boot ID, diagnostic kernel release, root UUID, Ubuntu OS identity and BLS entry SHA256. It still rejects one-shot selections or a changed default. It uses a fresh `commercial61-native-023-deploy-002` staging directory and separate logs. No existing diagnostic entry or global default is changed. The post-test return guard still requires standard Ubuntu. The new host-guard regression passes, including rejection of changes to each audited field.

## Closed runtime result

The single attempt ran 2026-11-13 16:16:10–16:18:36 UTC (local November 14), returning to standard Ubuntu, boot ID `63dd1f69-4e2c-415c-8088-dcd024c90401`. All 59 retrieved files matched their remote hashes. Retrieval used read-only `noload` mounting and subsequently unmounted the evidence partition. The configured target termination was observed.

The missing mapper/IMapper loader loop disappeared. Original SceneBoard PID 3366 registered its root scene and reported successful initialization. However, all three genuine 160×256 scanout samples remained black. **The real desktop is not verified.** Later SceneBoard EGL calls report invalid display / `EGL_BAD_DISPLAY`; RenderService's successful FD690 rendering does not establish that SceneBoard's separate EGL path works.

Independent preservation verification passed: all four original image hashes, standard Ubuntu current/default, firmware, manual entry, unmounted evidence partition and enabled/active screen-off timer. Of 110 prior EFI files, 109 remained identical; only the legitimate boot-managed random seed rotated. Original runtime evidence remains unchanged.
