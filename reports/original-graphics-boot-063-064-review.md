# Original graphics graph: observations 063–064

## Confirmed result

Trial064 ran the original init/HDF/RenderService graph with guest SELinux
permissive, the existing virtual-only DRM kernel, and coherent software Mesa.
Original RenderService PIDs674 and1160 (UID1003, original SELinux domain) really
returned success from `eglInitialize` and **`eglMakeCurrent`**, with non-null EGL
contexts. This is not a private stand-alone rendering probe. It does not prove
Skia context readiness, frame submission, scanout, an interactive desktop, or
native Adreno operation.

The reference bridge's actual make-current call runs once, with its original
arguments and return handling. Only reversible bounded tracing was added to a
compiled copy; original reference and SDK binaries were not patched. The six
Mesa libraries match the already-built software bundle; DRM and the distinct
private NDK runtime remain unchanged. Original platform `std::__h` libc++ remains
in use by the bridge and services.

## Trial and independent evidence

- `reports/baremetal-sdk-original-init-qemu-064/result.json`: 160.0267-second
  bounded observation, not a clean guest shutdown; no helper failure.
- `reports/original-graphics-boot-064-independent.json`: 17 actual permissive
  samples, original composer UID3036, allocator UID3041, and RenderService
  UID1003/domains; original RenderService bridge/Mesa/platform-runtime mappings.
- All12 injected files, initrd, virtual kernel, all three complete original SDK
  images, and all378 previous native raw files independently hash-verified.
- Serial SHA256 `4928935d07d49dd957923db6df6c78ed81a2da6c1a550675ab3bf18b935e2eb6`.
- Initrd SHA256 `2b6637aa49e6e5bdfdd2e4c8ffccef425aa66f868348fd6173e1ab7944bdb44b`.
- No Foundation critical fault or guest reboot observed within this bound.
  **Services/desktop are not declared ready.**

Trial064 changed the isolated guest from2CPU/2GiB to8CPU/4GiB (host had32 logical
CPUs and ~14.5GiB available), and added passive group/node observations plus actual
make-current tracing. It did not modify original service credentials or node
permissions. The bootstrap initially creates genuine kernel DRM nodes as0660,
root:graphics; later samples show0666, still root:graphics. Original allocator
has GID3041/no supplementary graphics group, while composer includes graphics.
Thus the proposed allocator DAC mismatch is **not established** and no permission
relaxation was applied. Some console-interleaved group records contain kernel
text; only intact numeric records support these group observations.

## Remaining failures and limitations

Original init reports RenderService674 exiting with code0 at87.47s and starts
PID1160. This is an init-reported status, not proof of stable or healthy exit.
Allocator1024 was reaped with signal9. The original targeted `hilog -x -P1160`
query reached the8-second alarm (wait status14), but closer serial inspection
shows it **did emit partial original logs**. Most messages could not resolve
their dictionary UUID (`OpenUuidFile fail, unknown log`); a few plaintext logs
survived, including original PID1160 setting `bootevent.renderservice.ready`
with ret0. This is a service-reported parameter write, not proof of full graphics
readiness. The earlier description of this query as producing no useful output
was too strong; raw logs and completed verification records remain unchanged.
Pbuffer creation still returns null, but real make-current succeeds; do not
patch that path merely on the assumption that a pbuffer is mandatory.

Original composer readiness writes are rejected by the original parameter
service (serial77.35s): caller UID/GID3036, configured label UID/GID0 mode0775.
Read-only inspection finds the **original** vendor
`/etc/param/composer_host.para.dac` already specifies
`bootevent.composer_host.ready = composer_host:composer_host:0775`.
The mismatch between original file and live selected label needs investigation;
no DAC file, identity, access check, or readiness value was changed or fabricated.

## Disposable-scratch forensic recovery

Earlier062 read-only debugfs inspection hit metadata checksum errors after the
bounded VM stop. For064 a fresh exclusive copy of the disposable guest scratch
was checked/recovered offline. `e2fsck -f -p` targeted **only that new clone**,
returned1 (corrections), and debugfs then listed an empty faultlogger directory.
This recovered view does not prove no crash occurred or establish exit cause.

- Evidence: `reports/original-graphics-crashes-064/`.
- Retained original scratch unchanged:
  `dd0455e5e44e65fb9139c9becaf94644d4fa301c25245f7ae472f1c2dc90c68a`.
- Recovery clone:
  `159c0dbb555ad7bfbcbdc9a9b961adb8617e1fc5a2123d42cfebc733a5abad0b`.
- No original SDK image or user data was repaired, mounted, or written.

All work in this interval stayed in local WSL and isolated QEMU. No MateBook SSH,
Ubuntu configuration change, host reboot, physical modeset, download, commit or
subagent was used. Three project references remain the architectural basis;
unrelated L410/Mali components and its Linux-compatibility layer were not copied
into this different hardware/backend.

Next: restore access to genuine logging dictionaries for original service/HDF
diagnostics and account for the parameter
label mismatch. Preserve authentication, original identities, watchdog behavior,
numbered evidence, permissive-mode labelling and original images.
