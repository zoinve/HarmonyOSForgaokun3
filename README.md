# HarmonyOS for MateBook E Go / gaokun3

面向华为 **MateBook E Go（gaokun3，Qualcomm SC8280XP / Adreno FD690）** 的 HarmonyOS 适配研究。主要路线是在真实硬件上保留原始 init、系统服务、RenderService 和桌面，通过适配内核、图形分配器、HDI/VDI composer 与输入链路实现运行。

**这是实验性源码仓库，不是一键安装包，也不是已完成验收的操作系统发行版。** 错误的 EFI、分区或驱动操作可能使设备无法启动。务必保留 Ubuntu 默认启动、恢复手段及原始数据备份。

## 当前状态

| 项目 | 已取得的证据 | 尚未完成的验收 |
| --- | --- | --- |
| 原始服务与图形 | FD690/Freedreno 真实 GPU；原始 composer 服务 UID 3036 下 GPU 管线实际工作 | 长时间桌面稳定性与交互性能 |
| 横屏显示 | 逻辑 2560×1600；物理 1600×2560 面板由合成器旋转 | 状态栏显示完整性仍待排查 |
| GPU 合成 | 两遍 shader：输入旋转至自有背景，再叠加光标至 GBM scanout | 稳定 120 FPS **未达到/未验收** |
| 触控板 | 实体设备事件到达 MMI/应用；补充软件光标，旋转、裁剪、隐藏及空闲重绘测试通过 | 实体移动、轻触、按压、滚动的最终人工验收 |
| Binder | 修复 ACCESS_TOKENID 扩展中发送方 PID 命名空间错误 | 设置/小艺输入法完整复测 |
| 启动 | 当前手动启动方案使用 032 的无期限 init + 041 GPU composer，无自动退出 | 新组合尚未单独启动验收 |

041 原始服务的受控启动实测中，合成器该阶段平均耗时由 034 的 **22.06 ms 降到 4.15 ms，约 5.3 倍**。这是限定采样窗口的阶段耗时，不是桌面 FPS；不能把它或面板 120 Hz 当作稳定 120 FPS。详见 [041 原始服务实测](reports/native-render-041.md)。

## 仓库内容

```text
next-experiment/   顶层 C/C++/Python 源码、构建/分析/验证脚本、服务配置
reports/*.md      历史研究与适配报告；原文保留，各自的结论仅适用于对应实验
docs/             当前状态、构建前提、架构、测试边界、发布与参考工程说明
tools/            源码发布检查及其独立单元测试
.github/workflows/ 仅检查源码策略和 Python 语法，不启动设备实验
```

**不上传镜像或二进制**：ISO、system/vendor/userdata、内核 Image、initrd、DTB、EFI、共享库、可执行程序、压缩包、截图、原始日志、私有 SDK 和第三方参考工程工作树均不在 Git 中。它们仍保留在本地实验环境；报告中的本机路径不是仓库内的下载地址。

## 阅读顺序

1. [当前状态与推荐源码入口](docs/STATUS.md)
2. [架构与数据流](docs/ARCHITECTURE.md)
3. [构建环境与外部依赖](docs/BUILD.md)
4. [测试与运行风险](docs/TESTING.md)
5. [第三方参考及授权边界](docs/REFERENCES.md)
6. [源码发布规则](docs/PUBLICATION.md)

历史 QEMU/KVM 实验与后续裸机实验使用不同编号空间；**不能按数字大小判断最新版本**。例如 `913` 是较早的 KVM 路线，不是比裸机 `041` 更新。043/044 的 KMS 诊断、045 的构建脚本也不等于已经通过验收的新发行版。

## 安全的本地检查

只使用 Python 与 Git、不连接设备、不需要任何镜像：

```sh
python -m unittest discover -s tools -p 'test_*.py'
python tools/verify_source_tree.py
```

第二条检查 Git 索引中的真实文本内容、文件白名单、常见凭据与全部已跟踪 Python 文件的语法。它**不代表**内核、原始服务、桌面或物理输入通过验收。

构建与运行脚本保留了实验机路径、SSH 别名、哈希和已使用编号的保护条件；它们是研究记录，不是可任意设备执行的安装器。不要批量运行 `run-*`、`install-*`、`cleanup-*`、`archive-*` 或 `test-*`：其中一些会访问真实设备、分区、EFI 或发起重启。

## 说明

- 当前 HarmonyOS 目标环境采用明确标注的 **SELinux permissive**，保留 SELinux 支持、策略和审计；不等于关闭 SELinux，也不授权修改 Ubuntu 的安全配置。
- 不伪造身份、设备认证或成功结果，不通过关闭无关权限检查掩盖适配问题。
- 本项目不附带 HarmonyOS 官方镜像、商业 SDK 或第三方二进制授权。自行取得所需材料并遵守其原始条款；引用工程的许可证不因本仓库而改变。
