# Safety And Governance Change Ledger

## Purpose

追踪工作流决定依据和作用边界。

## Outline

| Date | Change ID | Section | Change Type | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| 2026-11-28 | CR-20261128-200 | 清空后恢复 | fixed | 恢复已确认的空历史仅支持比较，新增正文仍须本次答复 | validated |
| 2026-11-28 | CR-20261128-197 | 已采用范围的修订 | changed | 在两种出稿渠道的实际修订前绑定写入与删除各自的范围 | validated |
| 2026-11-28 | CR-20261128-196 | 复用采用决定的范围 | changed | 在聊天和文件出稿前核对原决定与后续变更，缺口回原阶段。 | validated |
| 2026-11-28 | CR-20261128-195 | 大纲展示与等待 | changed | 聊天与待评审文件共同等待当前版本的用户决定 | validated |
| 2026-11-28 | CR-20261128-194 | 模块大纲 | changed | 以原话和原范围核对决定，区分 Skill 流程和宿主权限 | validated |

## Detailed Records

### CR-20261128-200 - 清空后恢复

- Section changed / After：恢复已确认的空历史仅支持比较，新增正文仍须本次答复。
- Before / Why：已合法清空的模块无法展示随后新增的第一叶。
- Impact / Validation：[适用范围和回归结果](../entries/2026/2026-11/CR-20261128-200-reopen-retired-outline.md)。

### CR-20261128-197 - 已采用范围的修订

- Section changed / After：在两种出稿渠道的实际修订前绑定写入与删除各自的范围。
- Before / Why：整棵树的变更会连带阻断未变分支，原入口未绑定删除旧稿的动作。
- Impact / Validation：[变更详情与演练证据](../entries/2026/2026-11/CR-20261128-197-outline-revisions.md)。

### CR-20261128-196 - 复用采用决定的范围

- Section changed：复用采用决定的范围。
- Before：未专门说明接续中的过期、撤回与错配。
- After：在聊天和文件出稿前核对原决定与后续变更，缺口回原阶段。
- Why：#196 要求接续时复用仍有效的大纲。
- Impact：阶段6的原记录恢复、出稿和阻断。
- Validation / Detail record：[CR-20261128-196](../entries/2026/2026-11/CR-20261128-196-stage-six-resume.md)。

### CR-20261128-195 - 大纲展示与等待

- Section changed / After：聊天与待评审文件共同等待当前版本的用户决定。
- Before / Why：#195 要求把首次阻断接到实际资料和一轮具体的大纲决定。
- Impact / Validation：[测试结果及作用范围](../entries/2026/2026-11/CR-20261128-195-display-and-wait.md)。

### CR-20261128-194 - 模块大纲

- Section changed / After：以原话和原范围核对决定，区分 Skill 流程和宿主权限。
- Before：阶段入口依靠人工读取现有流程。
- Why / Impact：#194 要求按任务和模块核对用户原意与拟写范围。
- Validation / Detail record：[开发验证与边界](../entries/2026/2026-11/CR-20261128-194-module-outline-check.md)。
