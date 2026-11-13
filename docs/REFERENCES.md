# 参考工程与外部材料

本仓库没有打包以下工作树、第三方 SDK、系统镜像、内核输出或二进制依赖。请从各自维护者处获取，并遵守其许可证和使用条款。

| 工程 | 已参考的版本 | 用途 |
| --- | --- | --- |
| [L410-HarmonyOS-Adaptations](https://gitlab.void-tech.cn/voidtechpublic/L410-HarmonyOS-Adaptations) | `205ad35e322f50993783f6bae48641abfa0dcf62` | HDI/VDI、队列和原始服务整合边界 |
| [L410-Linux-Compatibility-Platform](https://gitlab.void-tech.cn/voidtechpublic/L410-Linux-Compatibility-Platform) | `d95fbcecbf780e4086aa90f0c7ad052577121f11` | Linux 应用兼容平台架构，不是 MateBook 裸机启动替代品 |
| HarmonyMac | `f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad` | 原始 RenderService、平台工具链、EGL/allocator/composer 集成参考 |

HarmonyMac 的来源地址没有在当前已核对的本地记录中统一给出，本页不编造链接。其本地路径和参考入口见 [来源核对报告](../reports/reference-three-projects-001.md)。

L410 的 Mali/ION/framebuffer 和 HarmonyMac 的 Apple/llvmpipe 后端不能直接替代 gaokun3 的 MSM/Adreno/DSI 驱动；应复用已核对的接口与生命周期，而非照搬部署脚本。

本项目没有为第三方代码重新授予许可证，也不代表官方 HarmonyOS、华为或高通发布的产品。仓库内保留的源码来源标注和第三方权利继续有效；所需官方材料由使用者自行合法取得。发布源码不意味着所有外部材料可以再分发。
