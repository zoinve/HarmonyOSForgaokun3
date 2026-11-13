# Genuine manager reply metadata 046

This test returns to the already allowed, original-SDK-compatible PING contract. It does not repeat the rejected List/Check authorization query or change the observer identity. After the actual BR_REPLY, the same Binder fd is queried using the original 40-byte GET_SENDER_INFO ABI (`_IOWR('b',32,...)`). Token, first token, PID, reserved fields, and transaction UID are observations, never replacements or inputs to a token setter.

The generated C passed strict host compilation and actual non-PID1 refusal before preparation. Prepared ARM64 init: 784,720 bytes, SHA-256 `845e9238266037ac7d42d5bc7992f814a0b668c1dfd9ae76210ddc87b2c48819`; generated source SHA-256 `6b4baba9d9d6649ea4126c95a4790973c7511f600fd359573978e6ff722328fb`.

The new bounded run retains the unchanged kernel, original SDK-selected policy with explicit enforcing, read-only original system/vendor/sys_prod, and only a fresh private scratch filesystem writable. No original userdata, network, GPU, physical reboot, or Ubuntu changes are involved. A metadata denial or absent token is recorded as failure, not bypassed. The separately extracted production-policy reference is not injected into this original-init boot.

## Actual result

The bounded run observed a successful genuine manager PING. On the same Binder fd, GET_SENDER_INFO returned 0 / errno 0: token `000000002806886c`, first token zero, PID 83, UID 5555, both reserved fields zero. The original SDK's nonzero-token classification gives native type 1. The observer remained in the init domain, with enforcing 1 before and after the reply. No identities were modified, and no List/Check query was sent.

Independent verification passed: prepared files/source, actual kernel, all three whole original images, retained private scratch image, byte-identical local/WSL results and serial evidence, and the unchanged read-only hardware/fstab contract. See `baremetal-sdk-original-init-qemu-046/independent-verification.json`; serial SHA-256 `32c44d2b41bc32596f312bb38b6ac8fc5a2d7655745147b85dafc79c8e46ba14`. There were 35 registration log records, no token-lock or token-initialization failure records, and no observer failure.

The 60-second external timeout remains a bounded observation, not full boot verification. This verifies genuine reply identity delivery from an SDK-initialized native service, not authorization of the zero-token observer to privileged SA queries, a complete service graph, native-board userspace, or a HarmonyOS desktop. The SDK-selected developer policy remains distinct from the separate production-policy tests.
