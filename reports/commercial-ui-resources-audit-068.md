# Original UI Resource Input Audit

Read-only debugfs cat extracted four exact source-image HAPs. The files and
full metadata are preserved in commercial-ui-resources-audit-068/result.json.
All four pass ZIP CRC checks; no HAP cryptographic validity is inferred.

- SystemResources.hap: SHA256 c15a7f2d64e71e99cf6515e10e4d4b06c8ec55db203e68acf495ddfdcc59cf40.
- SystemResourcesExt.hap: SHA256 919c32b468f035450d3261985bab6dd1bf39116fe6891d8ecf7ee5b22bf71ed8.
- HwStartupGuide.hap: SHA256 392566ac1deefe9a269db3ebe45513038ed773f210e628f0ca55ce73ed34a1a7.
- SceneBoard_EngineService.hap: SHA256 2f5b647876f41c335a9972e24eb0c679b7faade7afb45fb8d42894d1163a9dc4.

The SystemResources indexes identify Restool 6.0.0.001; StartupGuide and
EngineService indexes identify Restool 5.1.0.008. Mixed producer versions alone
do not establish incompatibility or justify rewriting resource indexes.

Original StartupGuide contains resources/rawfile/welcome_land_one.mp4 and
welcome_land_two.mp4. Both are ZIP_STORED, not deflated; sizes 160153 and
687594 respectively. It also contains all five previously successful Lottie
JSON names. The exact basic_statement_cn.json name is absent from this HAP;
basic_service_statements.json exists. This is not a complete search of every
possible runtime resource provider or a statement that those files are aliases.

067 logs report Get rawFile error 9001005 for welcome_land_one.mp4 and
welcome_land_two.mp4 at 50.887/50.888 seconds despite the verified archive
members. This points to a resource resolution/read boundary worth observing,
not proof of a path fix. The same log reports SystemResources AddResource
failure at 17.876 seconds although the original file exists and its ZIP CRC
is valid. CRC validity does not prove resource-manager semantic acceptance.

No original image, HAP, signature, namespace path, product identity or original
resource-manager function was modified by this audit. The operational 068
candidate contains only full-resolution observation additions described in
its admission test. Do not silently adopt L410 private-symbol interposition.
