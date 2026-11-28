# CR-20261128-197 - 已采用范围的修订

| Field | Value |
| --- | --- |
| Status | validated |
| Target Skill | test-point-discovery |
| Change Type | changed / validation |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / safety-and-governance |
| Source | #197、父规格 #193 的 AC-006 |
| Baseline | d5c620590a9dc994ba6645ddf3efb2eebb953538 |
| Author | Codex |
| Related Records | CR-20261128-194、CR-20261128-195、CR-20261128-196 |

## Summary

对已采用的树，固定程序分别绑定本次写入与待删旧正文的完整叶路径。旧记录可继续支持未变分支，增删分支须展示实际差异，收到针对这版的明确答复后再改稿。

## Context And Problem

原来只匹配整个决定版本，修改任何分支都会连带阻断其他分支。请求的范围只能表示新版拟写正文，无法表达“在当前版本删除上一版的指定正文”。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md、references/outline-gate.md | 已采用模块的修订入口、范围变更请求 | 恢复当前有效决定，区分增删、移动、保留及叶内细化，明确聊天与文件的停点 |
| scripts/check_outline.py | 决定验证、版本及本次写删范围 | 校验新旧任务与模块、双方依据、具体差异及待删旧路径 |
| tests/test-point-discovery/test_outline_revision.py | 命令行回归 | 使用受控演练覆盖新旧决定与具体动作 |

## Decision And Alternatives

以完整叶路径作业务范围身份，移动或改名自然产生一增一删。保留原有问答与决定格式；展示的差异附两个版本缩写，完整版本保存在 CLI 结果。旧确认可以放行仍有效的叶，新增和待删正文只能使用针对本次展示的新确认。

## Detailed Change

请求用 `previous_decision` 指定旧记录、`scope` 表示本次写入、`remove_scope` 表示明确待删的旧正文。两版差异仅用于展示，实际改稿的上限为通过程序的两组路径。删除整支枚举旧叶。仅删除最后全部分支可传空树，程序仍要求显示差异和新版明确答复。重新开始写稿须有具体分支。

## Impact Analysis

首次调用和阶段 6 接续沿用同一个 CLI。原叶内细化保留原树。分支的语义和答复的业务含义由执行者结合实际资料、原上下文核实。阶段 5 来源与处置复核、阶段 7 具体稿评审继续独立生效。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| RED | 新回归经变更前的 CLI 及增量实现执行 | 捕获未变叶被拦、没有可确认的增删版本、空树删旧不能执行、改动波及未变兄弟、父节点被误当有效叶 | 修订用例逐项转绿 |
| GREEN | python -B -m unittest discover -s tests/test-point-discovery | 通过 | 含合成的同叶细化、整支删除、最后一支、父层移动、其他任务及模块 |
| 受控交互 | 实现代理运行实际 CLI；另一代理作模拟主持，分两轮看到展示再答复 | 新增、移除各由 1 变 0；细化直接 0 | 下表为本机文件 SHA-256 前 12 位 |
| 静态检查 | validate_create_skill.py skills/test-point-discovery --require-change-records；git diff --check | 包结构、索引及空白检查通过 | 包级现有中文触发措辞提示保留 |

| 受控演练步骤 | 旧稿与新稿 | 本次实际差异 |
| --- | --- | --- |
| 提议新增 → 模拟主持确认 | 99859a437949 → 0196b6f6644e | 等待时保留原稿。确认后只追加新分支章节 |
| 提议移除 → 模拟主持确认 | 0196b6f6644e → d487eba3e9be | 等待时稿件仍为 0196b6f6644e。确认后仅删对应章节 |
| 原叶内细化 | d487eba3e9be → 68f8cfbee7c6 | 原叶的一行预期限定到本次所选对象，其他章节保留 |

## Safety And Privacy

演练使用虚构资料和明确标注的代理模拟答复。新增源码、测试与公开记录只含合成输入与摘要，业务原件与真实用户原话均留在本机。

## Risks And Follow-up

本票验证 Skill 使用的命令行、两轮模拟范围确认和局部文件变化。宿主全局写入拦截、设备业务结果不在本票范围。交付版本的独立实际入口验收由 #199 绑定。
