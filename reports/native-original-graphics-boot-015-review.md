# Native original-service trial 015

Exactly one physical boot completed and returned automatically to Ubuntu, boot ID `34b991e6-7cde-4acd-a34e-6e406e179d30`.

The sole functional change creates `/usr/system -> /system` inside both original service sandbox roots, preserving the original customization parameter, service profiles, identities and sandbox implementation. A disposable chroot test at UID 5555 reproduced ENOENT before the alias and successful real profile reading afterward.

Native evidence confirms samgr discovered the original installs profile, dynamically launched the unchanged installs service, and registered SA 511 (`Publish SA:511 result:0`). Original application unpacking now runs, but records actual ENOSPC/errno 28 in the 512 MiB RAM data filesystem. No desktop success is claimed.

Independent verification checked all 49 raw snapshot hashes, original RenderService/Foundation/composer/allocator identities, 12 permissive SELinux samples, stable original-init root, three unchanged original images and 81 unchanged static EFI files. Default Ubuntu, automatic screen-off and read-only LAB mounting remain intact. The obsolete unreferenced EFI copy of trial004's initrd was removed only after matching its retained original staged copy; all numbered evidence and original staged files remain.

Next: expand only the fresh RAM data image, using genuine ext4 online resize and preserving the 180-second outer return guard. Never attach original userdata or rerun completed trial015.
