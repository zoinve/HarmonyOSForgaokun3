# 构建环境与外部依赖

## 先理解发布边界

此仓库只发布源文件和 Markdown。**无法仅靠一次 clone 重现完整启动镜像。** 历史脚本使用了先前独立构建目录、原始系统分区、精确哈希、厂商工具链与本机配置；这些材料没有随仓库提供。不能把构建脚本存在视作独立、通用、干净环境的一键构建已经验证。

## 已使用的环境

- 管理端：Windows + Python + Git，WSL Debian 承担源码检查和交叉构建。
- 目标：MateBook E Go / gaokun3，ARM64 Ubuntu；原始 HarmonyOS 在隔离的目标挂载/PID 环境启动。
- Linux 内核：匹配 gaokun3 的 ARM64 源码、配置与模块；031 内核 release `7.1.0-rc3-gaokun3-el2`。
- C 测试与静态 bootstrap：`aarch64-linux-gnu-gcc`；部分真实 GPU 诊断使用 Clang 与私有解压的 ARM64 C++ 头文件。
- 原始服务 VDI：匹配平台的 OHOS C++ 工具链，不能直接用 Ubuntu glibc C++ 库代替。
- 图形：libdrm、EGL、GBM、GLES3、匹配的 Freedreno Mesa、真实 MSM/Adreno 驱动及固件。
- 需自行取得的材料：有合法使用权的 HarmonyOS 镜像/SDK、匹配 kernel/device tree、板级配置及第三方参考源码。

## 路径与依赖链

脚本中的 `/home/zoinve/harmony-virgl-883`、`/mnt/d/lab/HarmonyOSForMatebookego`、Windows 临时目录及 SSH `matebook` 是原实验环境，不是通用默认值。应先逐个审阅并建立自己的独立目录、配置和可信 SSH，再修改副本。仓库没有保存 SSH 私钥或密码。

`build-native-render-041.py` 读取既有 034 构建结果，补丁式生成自己的 composer 源文件，链接匹配的 `drm_device.o`、libdrm 与参考头文件。它不会从零下载所有依赖。`build-native-original-graphics-boot-*` 通过 `runpy` 继承前序脚本，构造 initramfs 并替换特定成员；原始镜像保持不变。

请先阅读 [源码入口](STATUS.md) 和 [引用工程](REFERENCES.md)，再追踪所选构建脚本中的 `root`、`work`、`parent`、`runpy` 与 manifest。不要为了让脚本继续而移除哈希/排他目录/设备检查。

## 手动版本的构成

当前安装组合不是把 041 自动测试标题改为“手动”：

```text
031 kernel + DTB
032 initramfs（原始无自动退出 /init）
manual-gpu-overlay.img（只覆盖 041 composer）
```

`build-manual-gpu-041-cleanup-001.py` 检查覆盖归档的成员集合及合成结果，确认 `/init` 完全不变。`test-manual-gpu-041-cleanup-001.py` 还需要本地既有产物；不是纯 clone 后就能运行的测试。

## 禁止盲目部署

安装器硬编码检查特定 ESP、PARTUUID、已有启动项和精确哈希。它们会写 EFI/归档菜单；runner 可能设置一次性启动并重启。没有等价硬件、恢复手段与已审查配置时，不要执行。源码仓库不提供任何官方镜像下载、签名、设备认证或授权绕过。
