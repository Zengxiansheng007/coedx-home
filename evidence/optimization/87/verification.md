# #87 定向静态核查

正式基线为 `3cae1a783ddf43a0106d7ba6dc5e1072651693be`。本记录在 GREEN 入口执行前形成，静态结果不证明本票行为通过。

## 已执行

- 现有 `C:/DevelopTool/Python311/python.exe` 已从 Get-Command、Machine PATH 与 `C:/DevelopTool` 实际核对。没有安装依赖或创建环境。
- 受控 PowerShell runner 以 taskroot WorkspaceRoot 执行 Python `-X utf8 -B tools/verification/skill_format.py skills/test-point-discovery`，所有参数使用 worker87 绝对路径，退出0，实际输出为 `Skill is valid!`，保存于本目录 skill-format.log。
- `git -C <worker87> diff --check` 退出0。
- `git -C <worker87> diff --exit-code -- .agents skill-packages tools skills/test-point-discovery/scripts evidence/optimization/80 evidence/optimization/81 evidence/optimization/82 evidence/optimization/83 evidence/optimization/84 evidence/optimization/85 evidence/optimization/86` 退出0。没有改既有工程/分发 Skill、工具/helper或历史票据证据。
- 实际回读本轮全部产品 diff 与三个活跃测试材料。入口调用澄清覆盖及评审收尾，编写/恢复引用同一契约；新增本地 MD 引用实际存在。四份产品修改，三个活跃测试文件新增，不新增执行脚本、依赖或平台。

## 范围与后续

RED 五轮原件保留，已有正确未答/暂留/事实等待行为继续有效。当前实现集中补齐过程临时区、永久字段、逐轮与汇总复核、准确更新后的永久回读及限定清理、清理后新编号重开。

GREEN 尚未开始。Root 将派 fresh 真实入口 actor，主持逐轮实际答复、暂停恢复、具体评审、补交快照和后续变化。必须从真实文件写入/回读/清理取证。模拟通过不代表客户端或真实业务通过。没有重跑历史 owning-root checker，也没有改其断言或结果。全仓聚合由 Root 最后运行。

## GREEN 结束后的身份与定向复核

以上为冻源时记录，保留原阶段。当前九轮GREEN已经结束，具体语义与证据限制见acceptance.md。本次仅新增验收记录并追加本节，actor原件与产品源码未改。

- 实际回读全部GREEN输入/展示/具体稿、process.md、accurate.md v3、tool-sequence-receipt.md及任务inputs中的mock原文。原执行者事后工具摘要与最终原件分别核对，清理时序不冒充平台原始日志，完整中间快照及原始stdout未另保存。
- `git -C <worker87> diff --exit-code 2b3b610b07a7c55a0273855767a5fb922ddb5f4e -- skills tests` 退出0，四份物理产品SHA256逐项匹配source-freeze.md。冻结期间无产品/活跃测试变化，已通过的格式校验直接复用。
- `git -C <worker87> diff --exit-code HEAD -- evidence/optimization/87/red` 退出0，RED原件保留。`git diff --check`退出0。
- 当前integration实际HEAD为 `3cae1a783ddf43a0106d7ba6dc5e1072651693be`。受控runner对worker执行绝对路径 `git merge --ff-only 3cae1a783ddf43a0106d7ba6dc5e1072651693be` 退出0并返回`Already up to date.`。
- 准确v3、过程及mock资料的实际路径在准确说明区明确可读，S3仍位于任务根inputs，没有复制为业务状态或移入产品源码。

当前工作区物理文件SHA256如下，后续checkout若有LF/CRLF物化差异，应单列实际字节与精确归一映射，不改这些原运行身份。

| 文件 | SHA256 |
| --- | --- |
| green/accurate.md v3 | 356e09ffad2a773369bc8eec40821c4685dfa5faf4d38665ffd6846d66e334bf |
| green/process.md | b4100f042399a170d406ba26ec3bf0f5f9077a17794a4de212e935c6779d1ab7 |
| green/tool-sequence-receipt.md | 57e85e434e113d568e9c2cd64200244dbbe82c76ea96d6b152bf1a3227bf423e |
| TASK/inputs/label-index-mock-v1.json | 3ae97239b07376459ddf0348d6985087544d6016f74189f8c405223683040719 |

未重跑无变化的静态/历史checker，没有新增框架、依赖或全仓检查。全仓最终聚合、真实客户端和同版综合闭环保持原后续边界。本票没有真实业务结果。
