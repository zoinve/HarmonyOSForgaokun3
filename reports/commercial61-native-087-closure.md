# Original product workspace 087 closure

The full stable interactive desktop goal is not achieved and remains active.
Exactly one operational 087 boot was performed; do not repeat it or overwrite
its evidence. This report closes the experiment, not the goal.

## Run and implementation

- Run commercial61-native-087-66b7a5b6-33e9-401b-97ef-d357fdb0f685.
- Started 2026-11-15T06:22:45.585749Z; observed Ubuntu return
  2026-11-15T06:26:32.878741Z, boot ID a682d2b2-97f9-4c4d-8db0-d9ff4ad8119f.
- Native target PID 409 ended on the inherited bounded timeout, status 9.
- Only init changed in the archived payload. The hash-verified own bootstrap
  sidecar loaded from read-only/noload Ubuntu into target RAM successfully.
- Sidecar SHA256 37dc8382e6d3c12b3b3b72bf203c39c6dfc794403d2af823453bcf468930962d.
- ESP overlay: 358744 bytes, SHA256
  a0a785e82cb9542b160570f63247221eafc6a4c56368b2a306da3aed4b9a12ad.
  Free space after installation was 33603584 bytes, before entry retention.
  The existing 32 MiB guard was not lowered. Future payloads need a measured
  storage plan; another ordinary static-executable overlay does not fit.
- All three own executables refused normal execution with exit 77.
- 68 helper, decoder and evidence-flow regression tests passed. The separate
  087 admission checked the exact archive delta and added bootstrap source.
- Initial local build omitted baremetal-diagnostic-core.c and failed linking.
  It was not deployed. Both failed build directories were retained as
  commercial61-native-087-build-attempt-1 before the corrected build.

## Authoritative outcome

131 files were retrieved and matched remote sizes and SHA256 values. The
workspace creation marker has the exact expected byte count and hash. However,
original GetLayoutInfoFromConfig reported cfgFiles is empty, final layout length
0, and converted Dock list length 0. ResidentLayoutCacheMgr then used 12 preset
items, not the browser-only candidate. Creation is not consumption.

SceneBoard emitted logs under PIDs 4165, 8325 and 10416 and restarted. Original
logs still report missing AppGallery and Settings; the final instance emitted
EVENT_SMARTDOCK_INIT_FINISHED. No stable desktop follows from that event alone.
Two complete original freeze logs were recovered:

- 3S: 277163 bytes, SHA256
  18ae7bab2d8e7cf834918351f43c260fbf31d5f4f4d2bb6861459a156bee665e.
- 6S: 277948 bytes, SHA256
  e1604c2ef944b64392e6e8dfa4b9f456452f5526a2405bb7a2daf77e4761937f.

Both retain the main-thread synchronous BundleMgr launcher-info query under
ResidentLayoutCacheMgr.createDockAppInfo/init. Their byte counts, EOF and errno
checks passed. They do not establish a server-side root cause independently.

Genuine WPA, native DHCP and default-network selection succeeded. Original
HTTPS curl returned 204, exit 0 and TLS verification result 0. The independent
HTTP probe instead exited 28; do not claim both probes succeeded in 087. Original
guide logs show two actual validation-timeout events despite network availability.

Both complete 120s/140s source/output frames passed byte/record/export checks,
source 2560x1600, output 1600x2560, zero rotation differences. Both are mostly or
fully nonblack. No direct visual inspection was available, and neither pixels
nor actual desktop interaction are qualified. Original uitest still failed
accessibility permission checks; no bypass or successful layout is claimed.

## Follow-up and analysis corrections

Original module metadata now resolves GetLayoutInfoFromConfig import x6074 to
ConfigParseUtil. Its getAllConfig delegates directly to original
@ohos:configPolicy.getCfgFiles. See commercial-config-wrapper-audit-087 for
7 records, 121 methods, 8068 instructions and the resolved import tables.

Historical commercial 007 actually read const.cust.config_dir_layer as
/usr/system:/usr/system/variant/pc/base:/usr/system/variant/pc/china:/sys_prod:/chip_prod.
This is historical evidence, not a current 087 parameter observation. It makes
the distinction between canonical /usr/system and the /system RAM overlay a
specific next hypothesis. The earlier eight-path audit checked standard roots,
not all canonical/variant roots. Do not treat it as exhaustive runtime discovery.
Next diagnostics must establish the parameter and exact file visibility in the
real SceneBoard sandbox without changing its identity, permissions or policy.

The first workspace runtime analysis missed timeout wording with a space;
revision 2 selected timeout mentions too broadly. Revision 3 selects the exact
original validation-timeout event. Earlier analysis files remain unchanged.
The first secrecy-audit invocation used Linux ssh with a Windows key path and
failed transport; rerunning the read-only audit with Windows Python succeeded.

## Preservation

Retrieval completed before preservation verification. Ubuntu current/default,
timer enabled/active, original firmware/four images, manual entry and LAB
unmounted state all passed. Verification matched 148 prior EFI files, except
the boot-managed random seed and the authorized archived 085 entry removal.
Latest experimental entries are 086/087; shared dependencies remain present.

The successful secrecy audit scanned 131 files / 430880333 bytes and 911681
unique overlapping candidate digests. No private PSK was found in retrieved
evidence; the credential was not exported. Original HAP/ABC, application metadata,
provisioning state, service permissions and network helpers remain unchanged.
