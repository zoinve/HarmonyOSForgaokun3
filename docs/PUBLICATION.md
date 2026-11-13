# 源码发布与清理规则

## 本次清理范围

整理 Git 的内容而不是删除实验资料：顶层源码、服务配置、Markdown 文档进入仓库；原始 ISO/镜像、内核/initrd/DTB、编译产物、原始日志、截图、运行目录、第三方参考工作树和本机 agent 配置留在本地，不上传。旧 README 已保存在本地未跟踪的 `reports/source-publication-001/original-README.md`，当前 README 已更新为裸机路线。

`next-experiment/` 只收录顶层源码；其下自动生成的 `payload-*`、`run-*`、`official-*` 目录不发布。`reports/` 只发布顶层 Markdown，JSON、tar、原始日志和二进制证据不发布。历史 Markdown 中的链接可能指向这些本地证据；这不是可下载镜像的承诺。

不把脚本搬进新的目录，以免破坏相对路径和 `runpy` 依赖。通过当前文档索引区分有效入口与历史实验，不批量重跑旧操作。

## 防止误传镜像

`.gitignore` 使用发布白名单，并额外排除常见镜像、压缩包和编译产物；即使强制 `git add -f`，`tools/verify_source_tree.py` 也会拒绝白名单之外的路径、二进制内容和超限文件。检查的是 Git 索引中的真实 blob，不是可能与暂存区不同的工作树。

提交或推送前执行：

```sh
git diff --cached --stat
python -m unittest discover -s tools -p 'test_*.py'
python tools/verify_source_tree.py
```

不要使用 Git LFS 或 GitHub Release 绕过“不传镜像”的要求。任何以后发布构建产物的决定应单独确认，不属于此次源码上传。

## 可复现性与隐私

保留构建脚本的精确条件、历史版本和已知限制；不捏造 clean-room 构建已经通过。源码中仍有实验路径、SSH 别名和设备标识，应审阅并替换为自己的环境。不要提交口令、私钥、访问令牌、个人账户导出、设备证书或原始故障转储。自动凭据扫描只是辅助，不保证找出所有敏感信息。
