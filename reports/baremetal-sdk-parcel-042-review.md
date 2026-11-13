# Original SDK SA-list encoding — 042

The unchanged original SDK encoder produced the actual ListSystemAbilities request: transaction 5, dump flags 15, descriptor **`ohos.samgr.accessToken`**, 64 bytes. The familiar `OHOS.ISystemAbilityManager` string in the same binary was not the descriptor used by this method.

The original proxy SHA-256 is `9b916b2ac342e98da58aded0c71e8da9c98179d0e0ff3933d5a3506c4278d320`. Original CAPI parcel functions encoded the request. The test read the initialized descriptor of this exact proxy build; this inspection adapter is not a portable SDK API.

041 failed a test-harness assumption that the descriptor must reside inside the proxy mapping. Its legitimate C++ string storage was on the heap. 042 replaces that assumption with a bounded read of the process's own memory; no DSO or foreign process memory was changed. The failed run is retained.

042 also retained the actual raw Binder and unchanged SDK nested callback/identity-restoration regressions. This diskless codec test used the earlier console kernel without active SELinux; it did **not** query a service manager or establish service readiness.

Independent verification checked all 30 prepared ELF/init artifacts against sizes and hashes, local/WSL result and serial equality, actual kernel hash, and exact request length. Serial SHA-256: `4d629bdd825324fedd19c59150ae96fa0d954f08c180c88af7caf3fda5103a86`.

043 separately boots genuine SDK init with enforcing SELinux, three original read-only images and a fresh disposable data filesystem, then sends these captured bytes to the genuine manager. Its transport observation and strict reply decoding are separate checks; no success is presumed.
