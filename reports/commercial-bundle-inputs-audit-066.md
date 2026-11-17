# Original Bundle Input Audit 066 (Offline Only)

No operational 066 boot, device write, signature bypass, bundle substitution or
image modification was performed. Evidence is under commercial-bundle-inputs-audit-066.
The first extraction stopped on a CRC assertion; existing dumps were retained
and analyzed by analyze-commercial-bundle-inputs-066.py into result-revision2.json.
The SceneBoard comparison file was not extracted before that stop.

Settings/Settings.hap has valid ZIP entry CRCs and bundle name
com.huawei.hmos.settings, version 6.0.0.412. There are zero bytes between the
last local entry payload and the ZIP central directory. Camera/Camera.hap also
has valid CRCs and zero pre-central-directory bytes. Actual original HapVerify
logs report no HAP signing block for Settings at guest 20.796 seconds and reject
installation with 8519742. This supports a source-package problem rather than
an assumption that permissive SELinux should make the package installable.

PCSettings/PCSettings.hap has valid ZIP CRCs and 41029 pre-central-directory
bytes, but is com.huawei.hmos.pcsettings, version 6.0.0.101. This different bundle
does not satisfy startupguide's com.huawei.hmos.settings extension requests.
The gap is structural evidence only, not cryptographic signature verification.

AppGallery/@hw-ae-business+app-assist-4-developer.hsp fails ZIP CRC for
ets/modules.abc and contains invalid local header offsets recorded in JSON.
Its module.json identifies com.huawei.hmsapp.appgallery, version 6.5.1.300.
Original runtime installation also rejects this exact HSP. The whole AppGallery
bundle is subsequently unavailable to SceneBoard. Do not repair CRCs, strip
signatures, forge installed records or turn off verification to conceal this.

Original SceneBoard's frozen main stack and subsequent retry logs establish
the synchronous launcher bundle-query wait. They do not prove that repairing
these package inputs alone will fix the remaining RenderService/scanout path.
Authentic full desktop pixels and interaction remain unverified.

## Reference Comparison

The pinned three-project reconciliation remains reference-three-projects-001.md.
L410 Adaptations supplies platform composer, buffers and appspawn namespace
integration; its Mali paths are not MateBook Adreno fixes. Linux Compatibility
Platform supplies AnCo/Wayland application integration, not native desktop
startup. HarmonyMac wires original EGL/queues/RenderService/composer/KMS and
has a native-desktop-start.sh that force-stops startupguide. That workaround
is deliberately not adopted. Searches of the available reference source and
patches found no GetLauncherAbilityInfoSync/ResidentLayoutCacheMgr freeze fix
or package-signature recovery applicable to these exact commercial inputs.
Absence of search matches is not proof no other reference history contains one.

The proven 065 /chipset -> /vendor fix comes from the actual original image
and original init search-path disassembly, not a claim that the references
contained a ready-made solution. Original trust checks remain mandatory.
