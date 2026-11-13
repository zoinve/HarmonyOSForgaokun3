# 909: allocator backend dependency path confirmed

The allocator service (UID/EUID/GID/EGID 3041) has the correct GBM backend environment and no software-driver overrides. Its explicit backend load fails:

`Error loading shared library libdrm.so.2: No such file or directory (needed by /system/lib64/lab-softpipe-167/gbm/dri_gbm.so)`

The real backend DSO retains build-time RUNPATH `/system/lib64/lab-virgl883`, while the readonly RAM deployment uses `/system/lib64/lab-softpipe-167`. The service's own library path does not include that private directory. This explains why the independent root probe works but service allocations fail; it is not evidence of a required permission bypass.

Fresh payload 910 corrects RUNPATH only in copies of newly built private driver libraries. Original product libraries, the SDK C++ runtime, service identities, configuration, protections and all executable `.text` sections are unchanged. Needed-library lists and `.text` SHA-256 were checked before and after every edited DSO; details are in `next-experiment/payload-910/rpath-changes.json`.

The path test failed on the actual old backend, then passed on the new backend and Gallium. Actual archive executable checks also passed. Payload SHA-256: `d07390e8f457ac8d93433e4100243050b2b2bb21b364baf98df4402325b8b223`.

No genuine desktop has been observed. 909 was gracefully quit; final integrity verification is recorded separately.
