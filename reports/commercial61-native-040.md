# Commercial 040 — actual HarmonyMac direct EGL/GLES route

The user explicitly requests following the reference implementation and continuing until a genuine original desktop is displayed. Direct reread of pinned HarmonyMac ports/tools/prepare-render-service-test.sh lines 60–67 and ports/tools/adapt-local-root.py lines 38–44 shows system libEGL.so symlinked directly to the own NativeWindow bridge and GLESv2/v3 symlinked directly to Mesa. Previous target candidates instead retained the commercial EGL/GLES wrapper layer. This is a concrete graphics integration difference, not a security or service-identity substitution.

040 follows those exact symlink semantics in the volatile system RAM overlay: libEGL.so → libEGL_impl.so and libGLESv2.so/libGLESv3.so → /system/lib64/lab-commercial013/libGLESv2.so.2. Original image files remain immutable. The original init, services, account/Ability Manager launch, appspawn, token/authentication, permissions, sandbox and SELinux policy loading remain. The real FD690 Mesa backend and own composer/allocator are unchanged. No Apple software-renderer or Kirin/Mali preload is introduced. L410's private provider namespace is retained; Linux Compatibility Platform's separate AnCo/Wayland runtime remains later work.

The first offline 040 build copied bytes into aliases; before deployment this was refined to the reference's symlinks to avoid independently loaded EGL/Mesa instances. Both offline builds/logs are preserved. **Only 040-r2 is the deployment candidate**: data/work directories commercial61-native-040-r2, actual boot entry commercial61-native-040.conf. No 040 target operation has been repeated. All 30 directly imported EGL/GLES symbols from the three original RS libraries are provided. Checks retain exact original account launch and the 150/270-second independent guards; full/archive equivalence passed. This is ABI/load admission, not desktop proof.

The retained historical diagnostic labels “commercial_frontend” in the unchanged 033 dispatch observer now denote the active /system/lib64 frontend, which is the port route in 040, not the original commercial wrapper. Ownership paths, source hashes and this distinction must govern interpretation. No commercial-wrapper observation is claimed from 040.

The user requests only two experimental boot entries. After installation, old 038 will be archived/removed, keeping 039/040 plus standard Ubuntu and original manual entry. Return verification accounts for exactly hash-matched user-authorized entry removals; every other EFI change remains rejected except the boot-managed random seed. Shared boot/image payloads and historical numbered evidence remain intact.

Runtime result pending below.

## Installation and single launch

The 040-r2 increment is 1,071,255 bytes, SHA256 610a632a5f95c34ca05bfd10a38e4d07cc2e4de54d1564ea58bc18bac7561f0b. Installation preserved all 101 pre-existing EFI files, non-PID1 guards refused with exit 77, free EFI was 211,992,576 bytes, and Ubuntu default/manual/screen-off guards passed. The original four image hashes were verified. Installation itself requested no reboot.

As requested, a separate archived retention operation then removed only the 038 entry. Exact latest experimental entries are now 039 and 040; Ubuntu default and original HarmonyOS manual entry remain. Other 102 EFI files were hash-identical. Cleanup evidence: reports/boot-entry-retention-20261114T032718407640Z/result.json. Shared image/kernel/initrd payloads remain.

A separate single guarded 040 launch is active; results will be appended only after return and raw hash-verified retrieval.

## Actual result (closed)

The single 040-r2 run 11:27:33–11:31:16 Asia/Shanghai returned to Ubuntu boot c3c98210-03db-469f-af51-3b047bda6294. All 63 original evidence files matched remote hashes and read-only noload retrieval left the partition unmounted. Configured target termination was observed. Original SceneBoard installed and ran; all seven PPM captures remain black. The first SceneBoard flush is 79.104 seconds; last real composer frame is 74.142605 seconds, with zero recorded post-flush frames. Therefore the reference direct EGL/GLES route alone did not repair missing desktop presentation. No success is claimed.

Post-return checks passed: Ubuntu current/default, all original image hashes, firmware, original manual entry and enabled/active screen-off timer remain unchanged. Exactly the user-authorized, hash-matched 038 entry deletion was accounted for; the only boot-managed change is loader/random-seed. Current experiment entries remain 039 and 040.

The next integration observation follows the actual public method path in the original application: reference PipelineContext::FlushMessages invokes window FlushTasks, which reaches RSUIDirector::SendMessages and original RSTransactionProxy/Handler::FlushImplicitTransaction. Transparent method forwarding will record this real boundary without reading private object layouts, inventing responses, or changing original security decisions. This is not a substitute renderer or standalone private-function test. Data remain in reports/commercial61-native-040-r2, including presentation-analysis.json.
