# Commercial desktop investigation: 005 harness failure

005 was a diagnostic attempt, not a desktop result. Its bootstrap aborted with `commercial observer copy open errno=2` before executing the commercial init or the new profile observer. The machine returned to Ubuntu automatically. Do not interpret its empty diagnostic stream as an application or SA 511 failure.

The new observer source paths incorrectly included `/native-target` after the parent had already entered that directory as its root. 006 corrects only those two copy paths; the compiled observer and original service credentials remain unchanged. 005 artifacts and the single failed operational attempt are retained rather than rebuilt or repeated.

The observer is our own small C executable, linked only against `libc.so`. It inspects the commercial image's own configuration-policy library under the actual samgr service credentials and then execs the original `/system/bin/samgr`. It does not change credentials, register system abilities, alter parameters, or disable checks. Compiler headers are not a replacement SDK userspace payload.

## Why this diagnostic is necessary

004 proves original HDF SA 5100 publication, but original samgr reports SA 511 unsupported. Original HSP extraction consequently fails; SceneBoard's Animatronix dependency is then unavailable despite the original package being present. The precise profile-discovery failure is not established by static inspection alone. The `profile/penglai` binary string belongs to an additional conditional search, not evidence that the normal profile path should be replaced.

There is also an independent hardware backend mismatch: the supplied L410 RenderService wrapper selects Kirin Mali Vulkan, not the MateBook's FD690. No commercial desktop has been verified.
