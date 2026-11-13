# Original SDK composer ABI characterization001

## Fresh offline evidence

`composer-hdi-abi-001/result.json` records five commands and ten hashed raw
outputs. No target ELF was executed, no device was opened, and no MateBook state
was modified. All six original dependencies match the existing957 extraction
manifest, including service1.5 SHA256
`c5f7b2430aac4bee8edbeaea707805c0d9f33f6ee762a4a1f82452be01f92aab`.

- Public SDK headers reject the actual reference ABI header witness because
  `std::__h` is absent. The platform-header wrapper accepts the same witness,
  including Property40, Capability80/props-offset56, Mode16, LayerInfo20, Alpha5.
  This is a compile-time namespace/layout check, not a runtime ABI proof.
- The original service exports `InitCmdRequest`, `CmdRequest`, `DoCmdRequest`,
  `InitSMQInfo` and `GetCmdReply`, with platform shared_ptr/vector/FD types.
  It does not dynamically export a direct service `SetDisplayClientBuffer` method.
  It imports `DeviceCache::SetDisplayClientBuffer` and shared-queue synchronization.
  Full client-buffer integration must characterize the genuine SMQ/command/FD
  cache path; reusing the private C bridge cannot establish that contract.
- Historical957 serial evidence contains `ORIGINAL_COMPOSER_SERVICE_PASS` and
  child status0, but it ran under QEMU with virtio graphics. It is NOT a fresh
  native HDI result and is not rerun here.

## Safety finding and next boundary

The full reference `composer.cpp` must not be substituted into the current native
test unchanged: its capability/mode getters and hotplug/vblank registration call
`initialize()`, which opens primary DRM and allocates KMS scanout buffers. Merely
avoiding explicit InitDisplay/Commit is insufficient to preserve render-only.
No such native calls were made.

Next runtime design must preserve the real service/VDI method bodies and actual
platform libc++, restrict selected methods to verified non-initializing paths,
and retain primary-node absence and render-only namespaces. First obtain local
authoritative SMQ/command/FD definitions or characterize the matching binaries;
do not guess private container layouts, command IDs or serialize hand-made success
replies. The targeted local SDK/window-bridge search found no SMQ/composer command
headers. No downloads were made.

Still unverified: native service/container runtime ABI, SMQ/HDI serialization,
RenderService, policy-authorized graphics, physical scanout and interactive desktop.
