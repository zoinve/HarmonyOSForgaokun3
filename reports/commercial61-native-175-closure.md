# Protected USB diagnostic 175: early refusal

## Outcome

One operational boot ran on November16,2026 at09:25:12UTC and returned to Ubuntu
at09:27:13UTC. Run d8e6833f-db76-4669-acad-51db7b57cc6e. Do not repeat this boot.

The USB guard selected a candidate but refused in its identity/size/read-only
protection operations. The exact failing syscall was not recorded. There is no
USB175_PROTECTED marker, original-init launch, original handoff or persistent
prepare marker. This is not a Settings repair or native USB file-access success.

The sanitized early-return inspection hashes100 immutable remote phase logs;
latest phase100 is185794 bytes, SHA256
6c69abb964f062883ce2b491edf3704098cde506c727343e873d3b0e0f8e7edc.
It records usb_storage,uas,exfat module-load results0 and SCSI disk-attach text.
It does not prove that sd_mod is missing. No raw kernel lines or USB serials were
exported by the new inspection. Full retrieval refused because the expected
late desktop snapshot does not exist; that privacy check was not weakened.

## Storage and preservation

The prior173 desktop marker remains7ef326c6-671e-4607-97c0-cadeca7c9697.
Read-only offline fsck returns0; the filesystem is clean, SceneBoard directory,
archived diagnostic objects and data usage3626029056 bytes are retained. The
result explicitly sets original_init_handoff_verified and native acceptance
false for175. LAB is unmounted after verification.

Ubuntu is current/default; automatic screen-off remains enabled/active. All four
original image hashes pass. Prior EFI files remain unchanged except the normal
random seed and authorized removal of168.173/175 are the two retained experimental
entries; no shared payload was removed.

Firmware equality does NOT pass: Boot0000 with a USB device path appeared and
BootOrder changed0001 to0001,0000. Existing Boot0001 remains first. No firmware
write operation was requested by these scripts. Association with the inserted
bootable USB is an inference, not proof of who or what changed the variables.
The new entry is preserved; do not silently delete it or claim firmware unchanged.

## Installation history

Initial175 ARM64 compilation failed maybe-uninitialized warnings. A separate
175-compile-fix-1 build passes20 focused suites, reproducible binaries/guard tests
and exact reconstruction of the29-archive chain. Runtime173 remains byte-identical.

Initial installation stopped after copying the overlay: estimated command length
1809 exceeded the existing1800 guard. Original failure logs and payload remain.
The guarded completion copied the same381180-byte overlay to usb175.img, SHA256
896d92d713895009180453ebf17188db90cd3717f5d78351eb6801dd97200179.
The actual final chain uses that hash-identical short path; estimated length1785.
No guard limit was increased. The working173 entry and Ubuntu default remain.

## Physical USB status and next action

Preboot records confirm346d:5678,61849600 sectors, removable1; NTFS main partition
and1MiB FAT partition. Ubuntu mounted both after the first observation. Both were
normally unmounted, without force/lazy flags, and preboot-ready confirms neither
was mounted. No fsck, formatting or filesystem mount was requested on the USB.

Postboot collection at09:37:03UTC sees no346d:5678 USB device and no USB block disk.
This is absence of current enumeration, not proof that the user physically removed
it or that a particular driver is broken. Do not run another native USB test until
the real disk is visible again and unmounted.

176 adds operation-specific numeric guard tracing while reusing the same175
selection/write-protection logic. It is a local diagnostic source/test only;
not installed or booted. Do not infer that it fixes the underlying failure.

Settings remains separately blocked by the original package/signature/install
failure documented in155 and current absent-bundle evidence in173. No security
check, app identity or user database was bypassed to conceal that failure.
