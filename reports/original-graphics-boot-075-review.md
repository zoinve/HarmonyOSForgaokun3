# Original graphics graph 075: actual virtual scanout, not a desktop

## Result

QMP captured the real virtual GPU scanout at approximately 120, 240 and 330
seconds. All captures are 1280×800. The first contains only 16 nonblack pixels;
the later two are entirely black. This is **not** a HarmonyOS desktop result.

`reports/original-graphics-boot-075-independent.json` independently checks local
and WSL artifact hashes, PNG CRCs, dimensions and exact PNG-to-PPM RGB equality.
The original guest initrd is identical to 074. All 12 provider files, real ashmem
module, virtual kernel, three full original SDK images and 378 previous native
raw files were independently verified. No physical GPU or host display was used.

## Evidence

- `reports/baremetal-sdk-original-init-qemu-075/frame-120.png`: 16 nonblack pixels,
  two colors; RGB SHA-256
  `167727feae24adc8491b63edb379680f8ff393e809e72c90b97a332657961703`.
- `frame-240.png` and `frame-330.png`: black; RGB SHA-256
  `76ed5c9c326ba62322d464a22d3fcf7b76c7352c6d33badc36ccea7a33325e97`.
- Real ashmem loading, original HDI connection and the actual reference hotplug
  callback remain verified. There was no Foundation critical fault or guest
  reboot during the bounded observation. Those facts do not establish UI readiness.

## Next boundary

Commit entry logs alone cannot establish successful scanout, and the previous
observer did not enumerate all application processes. 076 retains the original
services/credentials and adds only reversible, single-evaluation Commit return
logging plus bounded passive process snapshots. It also captures actual virtual
frames. This distinguishes reported composition failures from absent UI content
without launching a fake desktop, forging callbacks or altering permissions.

Provider 005 was compiled successfully from a traced copy of the unchanged full
HarmonyMac reference; its original return expressions and operations are retained.
076 is pending. Ubuntu boot/default/screen-off configuration was not touched;
this segment performed no new live host screen-state verification.
