# Commercial 045: authentic oneway caller PID

The next corrective candidate keeps the complete original commercial userland,
normal account/Ability Manager/SceneBoard launcher, graphics providers and 044
observers unchanged. Only evidence labels and the independent diagnostic kernel
selection change. The 150/270-second bounds remain unchanged.

044 proved actual code 17 and code 0 kernel consumption on the original
RenderService endpoint, while the service still reported no application agent
for SceneBoard. The exact commercial service uses GetCallingPid for registration
and unmarshalling; its original IPC library reads that from sender_pid, not from
the distinct realpid extension. Kernel 031 leaves this field zero for oneway.
The fixed original code-17 jump table, method disassemblies and source hashes
are pinned in commercial-oneway-audit-045. This is a concrete causal candidate,
not proof that the next runtime will render a desktop.

Kernel 045 is built in a separate copy. Under CONFIG_ACCESS_TOKENID, only actual
incoming oneway BR_TRANSACTION/BR_TRANSACTION_SEC_CTX uses the existing held
sender TGID reference translated into the receiver PID namespace. There is no
hardcoded PID, invented identity, user-supplied PID, token/UID/SID substitution,
permission bypass or original userland patch. Sync and reply behavior, tokens
and sender-reference lifetime remain unchanged. Ubuntu's kernel and kernel 031
are preserved. Tests compile the exact modified branch and constrain the diff.

The new kernel is added to a unique ESP directory with hash checks, unchanged
prior EFI contents, original default/current Ubuntu and no reboot selection.
The normal candidate installation then pins its hash. Original DTB and shared
initrds remain in place. Keep only the latest two experimental boot entries,
archiving old entry contents/hashes outside ESP before removal. Preserve all
original images and immutable numbered evidence, and require enabled/active
screen-off timer and post-return unmounted evidence partition.

SELinux remains supported in the authorized permissive target configuration,
not disabled. All three adaptation references remain applicable; no substitute
desktop, forced OOBE, root injection or identity shortcut is used. Acceptance
still requires genuine original desktop pixels and interaction. Runtime results
are pending and will be recorded separately without overwriting this statement.
