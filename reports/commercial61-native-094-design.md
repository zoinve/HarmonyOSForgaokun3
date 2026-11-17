# Experiment 094: original-init hardware input, corrected private CLI handling

Use 093's reviewed hardware-input design and exact early wrapper without
altering original init, identity algorithm, modules, permissions or images.
Inherited EARLY093 and HARDWARE091 labels remain authentic in this new run.
The built full archive is based on 092, not on an installed 093 dependency.

093 was installed but not booted. Pre-boot primary-source inspection of the
original param CLI shows whitespace/CRLF around its value; 093 privacy parsing
did not cover that format. Keep 093 build/install/test history unchanged. 094
only normalizes whitespace inside the private pipeline before validating and
hashing the original parameter value. Add an actual-format fixture, alongside
twenty hardware-input and six exact export-guard cases. Hashing the original
UDID for privacy is not calculating or supplying a replacement identity.

Before replacing the candidate, require the exact unchanged 092 Ubuntu boot ID,
no one-shot entry, current/default Ubuntu and active screen-off timer. Archive
only our new unbooted 093 entry and unique early093.img, verify their hashes,
prove every other retained entry does not reference that path, then remove
those two owned files. All other EFI files/firmware must match. Do not remove
any shared payload or rewrite numbered build/install history. Save a separate
withdrawal manifest. This is not a repeated numbered operational boot.

Install the measured one-cluster overlay at the distinct unique path
`/commercial61-native-092/early094.img`, preserving the original 092 initrd.
Require two allocation clusters above 32 MiB and final free space >= 32 MiB.
Retain final entries 092/094, Ubuntu default/manual entry and shared chain.
Boot once only, retrieve under physical-serial/original-UDID privacy guards,
then verify preservation serially. Original UDID availability, collaboration
stall behavior, OOBE/activation and desktop/interaction remain separate runtime
questions; a valid identity does not complete the full desktop goal.
