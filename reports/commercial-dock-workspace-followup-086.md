# Original Dock workspace follow-up

No new operational boot or activation-state change was performed for this audit.

## Evidence

- External-path audit: eight default/PC-workspace candidates across system,
  sys_prod, chip_prod and chipset/vendor images were absent. These are standard
  policy roots; the audit does not establish runtime custom-policy roots.
- Defaults revision 3: 9 original records, 144 methods, 9201 instructions.
- Literal revision 4: 15 original preset object buffers, with exact offsets,
  extents and SHA256 values. Consecutive buffer ends match the next buffer start.
- The original PC preset contains AppGallery, including its original ability
  name, independently of whether that package is installed. Runtime evidence
  still reports it missing. Preset presence is not installation proof.
- Application-center and recent-task function entries refer to SceneBoard's own
  bundle and module. Their icon paths and label resource objects are original.
  The manifest has module pc_sceneboard. Those internal entry names must not be
  confused with exported abilities or represented as newly installed bundles.
- Browser runtime evidence is stronger: native SceneBoard logs at 13:47:41 show
  bundle com.huawei.hmos.browser, module entry, ability MainAbility, appStatus 0,
  followed by native BMS resource retrieval and successful icon-cache population
  at 13:47:42.458. This supports a genuine candidate app, not desktop completion.

## Configuration limits

Original workspace conversion selects container == -101, sorts by column and
copies typeId, bundleName, abilityName, moduleName, column, intent and optional
nested layoutInfo into new DockItemInfo objects. It does not simply preserve
every property of a PresetDockItem object. The default function icon/label
objects therefore cannot be copied wholesale into external JSON with an
assumption that they survive this conversion.

SmartDockLayoutConfig only replaces its current defaults when conversion yields
a nonempty list. An empty file/layout does not remove problematic default items.

Further work should establish a valid nonempty product-workspace candidate
using authenticated installed applications and explicitly check the behavior of
function entries. Do not patch signed HAP/ABC, invent application metadata,
disable lifecycle handling, or fabricate provisioning state. A deployment also
needs a measured payload-space plan: the existing ESP guard margin is 413696
bytes and is insufficient for casually adding two rebuilt static executables.

These findings narrow a legitimate board-adaptation option but do not prove
that workspace configuration resolves OOBE callback timing or activation.
