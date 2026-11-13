# Native original-service trial 003: scoped root-namespace repair

- Original 001/002 logs and artifacts are preserved; neither trial is rerun.
- Inner bootstrap, provider, Mesa, target configs, identities and original
  images are unchanged from 002. Bootstrap SHA256:
  `4ad51939ad903c9dc29f38ada56833fcdab102e51a2db67331a4e3f00befa19a`.
- Only outer root setup changes: `open_tree(OPEN_TREE_NAMESPACE | AT_RECURSIVE)`
  creates a namespace actually rooted at `/native-target`, then `setns` enters
  it. No chroot fallback is allowed. Unsupported API stops before original init.
- Isolated real-MateBook regression reproduced the old failure and passed the
  new form without launching target services or accessing GPU hardware.
- Static build with warnings-as-errors passed; all nine artifact hashes passed.
  Both binaries refused native non-PID1 invocation with exit 77.
- The installer removed only unused EFI kernel caches 008 and 014. Current
  kernel 015 remains; older 008's exact original build artifact was freshly
  rehashed in WSL and is retained. Installation journal precedes deletion.
  Other 80 EFI files remained unchanged; post-install free space: 83,927,040 B.
- Counted entry 003 retains Ubuntu persistent default and the 180-second
  outer automatic-return guard. Target SELinux permissive is authorized;
  Ubuntu security configuration is not changed.
- Exactly one 003 boot has been requested. Runtime root stability, services,
  RenderService and display output are not claimed by build or regression tests.
