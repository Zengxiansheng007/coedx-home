# CR-20261117-112 - 业务分组反馈身份与空格保真

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / downstream-and-handoff |
| Source | RTA-01；真实 TodoMVC 固定候选无编辑及预期编辑回传失败 |
| Baseline | 2202ebc0c5a7b77d9ab02c62284e6dd744828a53 |
| Author | Codex |
| Related Records | CR-20261111-202, CR-20261117-106 |

## Summary

同版可信评审元数据在实际用例节点归一化，业务分组层数不再影响反馈身份；原始返回摘要先验证。新投影保留数据尾空格，历史生成稿按准确旧布局回读，完整候选值和原始文件不变。

## Context And Problem

修复前以 `extension-reviewed-before-feedback.json` 固定候选调用公开 `render_extension`、`prepare_feedback`，raw-current、materialized-current、materialized-preapproval 及旧 Persona 实际预期修改均拒绝 `Unknown Markdown identity or structure`。旧逻辑按 flat 的模块深度剥离评审文字，分组稿则多出业务层；完整用例身份形状因此不等价。原始返回摘要又在全局文字归一化后重算。另 `aggregation._parse` 使用 `strip`，生成和回传均丢尾空格。

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/aggregation.py | projection、expand_feedback | 保留真实尾空格；可信回调只在对应 case 节点归一化；旧布局仅重建 expected，不修剪 incoming |
| scripts/feedback.py | Markdown 布局选择与标量探针 | 当前布局优先；同版评审直属叶及合法次数准确核对；flat 比较与探针复用同一可信元数据规则 |
| scripts/test_feedback_grouped.py | 公开接口回归 | 真实 raw/物化已审未审文件、实际预期编辑、尾空格与冒号、旧稿、隐藏消费者及拒绝分支 |
| .agents/skills/test-case-authoring | 分发镜像 | 与 canonical 同字节同步本票修改 |

## Decision And Alternatives

不放宽整个子树身份，不按标题或序号猜测，不忽略业务字段。可信评审豁免仅适用于当前同版已通过评审记录的准确显示文字；额外重复或带子节点的评审内容仍参与结构核对。显式绑定先匹配未归一化的原始 digest、来源版本和真实答复，再逐个业务叶解释。旧尾空格布局只是历史 emitter 的准确 expected 投影；incoming、原数据及 raw digest 均不变。有明确绑定的真实尾空格修改优先进入当前精确布局，不被旧格式吞掉。

## Detailed Change

现有 scoped initial baseline、proposal、summary agreement、final review 和完整源影响检查保持唯一权威；没有新业务状态、第二答案文件或全局修改。只归一化同版可信 final_review/review_history 直属叶及 pending/approved 状态。来源中未选记录、data_refs 和历史评审字节不修改。

## Impact Analysis

范围为候选生成、Markdown/受支持原生反馈共用计算层及分发镜像。无变化回传为零业务变更；本例业务修改仅生成提议并等待既有确认。涉及隐藏消费者的共享数据提议仍在应用前拒绝，来源版本漂移、未知分组、伪造评审、旧摘要绑定和未知结构仍拒绝。未更改 data_projection 接口；后续可见空格编码由 RTA-02 负责。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| 固定旧材料原问题 | 本轮独立 rta01-probe.py red | 四类输入均复现原错误 | 本地验收证据 |
| 首条生成文件回归 | 先失败后修改生产代码 | 已审 raw/物化最初失败，修复后四组合零变更 | 本轮执行记录及 grouped-final.log |
| 尾空格与旧稿兼容 | 单条回归先红后绿 | 精确字符串修改及旧显示不丢源值 | legacy-whitespace-red.log、grouped-final.log |
| 完整回归 | 标准库 discover，固定本轮临时目录 | merge RTA-03 后299项通过；随后恢复原始摘要全局唯一性保护，24项完整反馈回归通过 | final-full.log、feedback-final.log |
| 固定旧材料最终结果 | rta01-probe.py final | 三类无编辑均0 changes/0 deletions；Persona只产生TODO-EXT-001的steps/1/expected/0/text变更 | final-probe.json |
| Skill结构、记录与敏感扫描 | create-skill --require-change-records | exit1，仅同3个继承synthetic负例，0新增发现；不冒称全绿 | create-skill-final.json；Root基线create-skill-baseline.json |
| 原试用保护 | 输入 SHA-256 修复前后比较 | 探针所读五个文件字节保持 | red-probe.json 与最终 probe |

初次反馈全套启动受到系统 sandbox TEMP 原子替换 WinError 5 限制；保留该失败，改用本轮 evidence/rta01/tmp 临时目录复跑，不修改生产原子写实现。初次测试发现调用目录与模块路径不符以及 fixture 缺模块层/未建输出目录，均先修测试准备而非放宽产品校验。

本票共14次测试启动（含3次准备失败及先红测试）、4次旧材料公开接口探针、1次create-skill校验。数值仅本票实际执行记录，不创建第二项目额度权威；项目计数由Root合并。本轮未使用外部API/SDK事实，依赖既有标准库、已核需求/规格及当前源码，不新增外部检索、依赖或环境。

## Safety And Privacy

仅本地模拟材料和旧文件只读探针；没有凭据、外部模型、远端写入、全局安装、真实用例或业务执行。旧来源、旧评审稿及 Persona 文件只读。敏感扫描沿 Root 基线比较；继承三个 synthetic secret-pattern 负例不作无关修复。

## Risks And Follow-up

状态为 applied candidate，等待独立审查及 RTA-04 完整重新生成；不把计算接口或模拟答复当用户具体稿批准。实际 XMind 客户端导入未执行。无绑定且与旧 emitter 完全相同的回传按旧稿解释；明确的业务尾空格编辑须有原始返回身份澄清绑定。无全局部署或发布。

Refs: RTA-01；REQ-016/017/018/021；AC-019/020/021/023/034；本轮 plan.json 与只读需求/规格。
