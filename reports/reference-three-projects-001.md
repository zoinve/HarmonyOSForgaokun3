# Three-reference reconciliation

## User requirement and provenance

Use all three references, not HarmonyMac instead of the two L410 repositories.
The user supplied the two GitLab URLs again and explicitly retained HarmonyMac.
The earlier statement that the second reference was unidentified is superseded
by this record; historical reports remain unchanged.

| Reference | Local source | Pinned commit |
|---|---|---|
| L410 HarmonyOS Adaptations | `references/L410-HarmonyOS-Adaptations` | `205ad35e322f50993783f6bae48641abfa0dcf62` |
| L410 Linux Compatibility Platform | `references/L410-Linux-Compatibility-Platform` | `d95fbcecbf780e4086aa90f0c7ad052577121f11` |
| HarmonyMac | `C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816` | `f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad` |

L410 origins are respectively
`https://gitlab.void-tech.cn/voidtechpublic/L410-HarmonyOS-Adaptations.git`
and `https://gitlab.void-tech.cn/voidtechpublic/L410-Linux-Compatibility-Platform.git`.
Both were shallow-cloned successfully. No reference script was executed.

## Findings from actual source

- L410 `display-composer/src/composer_vdi.production-no-audit.c:74-120`
  specifies the raw vector, capability, property and BufferHandle layouts.
  Lines 2408-2465 implement preparation and CLIENT composition fallback;
  lines 2468-2529 retain the client buffer by dup and clear it explicitly.
  This is a VDI replacement reference, not a requirement to reconstruct the
  original service's private SMQ implementation.
- L410 composer lines 2204-2248 and 2532 onward initialize the display from
  getters/callback registration/Commit. These are NOT render-only safe calls.
  Its Mali helper, framebuffer, ION and backlight paths are device-specific;
  they are not substitutes for MateBook MSM/Adreno/DSI drivers.
- L410 `graphics-namespace/l410-appspawn-r18-namespace-v1/appspawn_r18_namespace_exec.c:37-62`
  uses a private mount namespace and a private EGL provider mount, and removes
  LD_LIBRARY_PATH rather than exposing generic glibc directories to appspawn.
  Its hardcoded Mali preloads are not usable as MateBook graphics libraries.
- HarmonyMac `docs/architecture.md:23-29` documents the complete path:
  OHOS EGL/NativeWindow -> Mesa -> original queues -> allocator/composer -> KMS,
  with platform std::__h objects kept separate from SDK std::__n1.
  Its llvmpipe/Apple backend is a reference, not a mandate to discard the
  already verified MateBook native Adreno rendering.
- HarmonyMac `ports/tools/prepare-render-service-test.sh:31-59,76-99`
  identifies the real integration boundary: original RenderService/client
  dependency closures, composer driver/service, HDF configuration, parameter
  watcher and original-init service startup. This script expects service1.3;
  the current SDK's actual service1.5 must remain version-matched.
- HarmonyMac `ports/tools/build-composer.sh:12-17` names the replacement
  `libdisplay_composer_vdi_impl.z.so` and links it with the platform toolchain.
  This is consistent with its service probe already adapted in local
  `next-experiment/build-composer-service-957.py:61-69`.
  Experiment957 is existing QEMU service-loader evidence, NOT a new result to
  rerun or claim as native/full RenderService success.
- The Linux Compatibility Platform README describes Wayland/XWayland -> AnCo
  application integration and explicitly excludes startup/deployment scripts.
  Its `linux-compat/scripts/build-anco-linux-runtime.sh:15-25` depends on a
  separate Debian/Wayland/wlroots sysroot and AnCo sources. It is relevant to
  Linux application support after the original HarmonyOS service stack works,
  not a replacement boot path or evidence that our desktop already works.

## Route correction and safety boundaries

Stop expanding stand-alone private-SMQ tests as the main deliverable. Preserve
their existing results; use them only when an actual integration failure needs
them. The next integration target is the original service/HDF -> replacement
VDI -> RenderService chain, building on957 rather than repeating its loader test.
Inspect the matching SDK driver/configuration/dependency closure before creating
a new fixture. Distinguish loading, service registration, queue/pixel output and
desktop/interaction evidence at every stage.

Do not run reference deployment scripts verbatim. HarmonyMac
`ports/tools/adapt-local-root.py:75-77` writes SELinux permissive. The user
explicitly reiterated that permissive mode is used and authorized: the earlier
rejection of this configuration was incorrect and is superseded. Permissive
mode is allowed in the HarmonyOS test/target environment, without asking again;
enforcing is not an admission gate for further service/desktop integration.
Preserve policy/audit evidence and label the actual mode. This does not authorize
changing Ubuntu's host security configuration. Other reference service identity
and sandbox changes still require technical review rather than blind copying.
No identity forgery, OOBE completion or unsupported-success stubs are authorized.

Physical modesetting/InitDisplay/Commit remain outside the current render-only
native diagnostic. A future isolated virtual-display fixture must be labelled
as such; it cannot establish physical MateBook scanout. Preserve Ubuntu default,
automatic screen-off, original SDK images and all numbered evidence.

## Changes during this reconciliation

Only downloaded reference working trees and this report were added. No MateBook
connection, reboot, EFI modification, service deployment, source build or new
runtime validation was performed during this reconciliation. Existing native
composer-method and isolated queue results retain their original scope.
