# Resource Compatibility Warning: Static Audit

The empty deviceType warning does not establish a missing board product type.
The original sys_prod parameter file already specifies const.product.devicetype=2in1.

Authoritative evidence is in commercial-resource-policy-locate-067-r3/result.json
and the adjacent original ELF disassembly. The owning original library is
/system/lib64/liblayered_parameters_manager.z.so, SHA256
96c1f1c3250c9b8af787a0af28c35468d85e7632a3d8f608dd77f75f78547b72.

calculateResourceType at VA 0x378c calls OH_NativeBundle_GetCompatibleDeviceType
at 0x37b8, not GetParameter or GetDeviceType. The empty-string branch at 0x389c
logs line 81 and returns without assigning the output reference. Only the
nonempty branch at 0x3900 assigns and lowercases the compatibility type.
The caller obtains an existing Configuration item before the call at 0x3448
and subsequently passes the retained string to Configuration::AddItem.

Consequently this diagnostic alone does not justify changing product identity
or prove that the configured resource type was erased. It also does not prove
that all resource loading succeeds. No original library, parameter, package
identity, signature check or provisioning state was changed by this audit.

067 is an offline audit number here, not a completed operational boot.
