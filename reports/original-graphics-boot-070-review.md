# Original graphics graph 070: observed Binder boundary

## Verified outcome

The isolated VM reached the 360-second observation bound. Original RenderService
PIDs 643/1145 had UID1003 and the original render_service SELinux domain, with
real Mesa EGL contexts and successful MakeCurrent. Composer1154 retained UID3036
and its original domain; allocator963/1151 retained UID3041 and its original domain.
All 43 captured SELinux samples were permissive. No Foundation critical fault or
guest reboot was observed within the bound. Desktop and physical display remain
unverified.

Guest-only debugfs mounted successfully. Fifteen read-only Binder diagnostic reads
succeeded. Composer1154 exported nodes8772/9029, referenced by HDF manager137 in
the sampled state. RenderService1145 did not hold references to those nodes in
these snapshots. This does not prove that it never connected, nor identify a
permission failure. The failure ring contains unrelated early logging failures;
they must not all be attributed to graphics.

The traced reference VDI recorded library_loaded in the verified composer process,
but no captured API entry, initialization or completed hotplug callback. Original
RenderService logs also report a failed auxiliary hwdisplay_interfaces_service
lookup. That auxiliary failure is not established as the main composer cause.

## Evidence integrity

`original-graphics-boot-070-independent.json` verifies all 12 injected ELF files,
the initrd/kernel, all three complete original SDK images and all 378 previous
native raw files. Ubuntu was not accessed or changed in this experiment.

The first verification refused an incomplete UID witness for observed composer965:
kernel output had interleaved its status line. A tested parser now reports that
PID explicitly as incomplete, while requiring complete original UID/domain
witnesses for verified PIDs and rejecting any complete wrong UID. The first
failure output is preserved; the successful verification has a separate output.
No VM was rerun and no raw evidence was rewritten.

## Read-only follow-up

The genuine original `libcomposer.z.so` was independently extracted without image
writes or target execution by `audit-original-composer-client-001.py`.
SHA256: c031105598312ed0d074ccf0742f985b22c701c905cac1bb679746112c582d6d.
Its HdiDeviceImpl::Init calls IDisplayComposerInterface::Get(true). The existing
original client implementation then obtains the remote composer through
IDisplayComposer::Get(false); the outer flag controls requester setup, not a
permission bypass or a reason to substitute passthrough mode.

Static original RS code connects RSScreenManager::Init through
RenderProcessManagerInit and RSScreenPreprocessor::Init to RegScreenHotplug and
HdiDevice::GetInstance. This is a static call path, not proof of which branch ran.
The next investigation must resolve that original startup/discovery gate rather
than changing working EGL, fabricating screens/callbacks, or relaxing identities.
