# Installer009 guard refusal and conservative EFI archival

Installer009 refused at its free-space assertion before creating the backup directory, assets or013 entry. The independent read-only audit confirmed all three were absent, no reboot occurred, and the current Ubuntu boot ID was unchanged. Its original stdout/stderr are retained.

EFI had 90,669,056 bytes free, below the 118,432,113 bytes required for013 assets plus the existing64MiB reserve. The reserve was not reduced. Only the three original004 diagnostic assets, whose consumed configuration had already been archived and removed, were copied to `/mnt/harmony-lab/work/efi-assets-archive-001`, fsynced, and independently rehashed against the original installation manifest before unlinking those three EFI copies. All experiment bytes are retained, including the original lab sources and the new archival copy. No current loader configuration referenced them.

The archival operation verified all79 other EFI files unchanged, all boot configurations/default/firmware entries unchanged, no reboot, and 133,079,040 bytes now free. Recent working diagnostic assets remain on EFI. See `baremetal-efi-space-audit-001.json` and `baremetal-efi-assets-archive-001.json`. Old installed004 reports are historical records; restoring their old entry would also require restoring the archived assets.

Use fresh010 preflight/installation/trial records for013. Do not rerun installer009 or overwrite its failure evidence. The candidate archive, kernel, init, helper and Mesa launcher remain unchanged.
