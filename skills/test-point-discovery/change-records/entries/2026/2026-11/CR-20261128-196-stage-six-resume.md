# CR-20261128-196 - 阶段6接续复用当前模块的原决定

| Field | Value |
| --- | --- |
| Status | validated |
| Target Skill | test-point-discovery |
| Change Type | changed / validation |
| Scope | core-skill-md / references-and-assets / scripts-and-validation / safety-and-governance |
| Source | #196，父规格 #193，AC-004、005 |
| Baseline | 8a2a5bfb62a793e78f8ea39c0deb4a6216357447 |
| Author | Codex |
| Related Records | CR-20261128-194、CR-20261110-001 |

## Summary

指定阶段6时恢复原树、实际采用或确认答复，按本次范围重跑同一程序。阶段5的问题处置及覆盖仍须分别核实。

## Context And Problem

原阶段入口能恢复规划和澄清记录，大纲校验只在首次调用处明确要求。单一问答 MD 的多行原话还会因追加新轮次而无法用整文件哈希持续回查。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| SKILL.md / references/stage-entry.md | 阶段6接续 | 恢复原版本及范围，核对后续变化、当前结果和阶段3/5前提 |
| references/outline-gate.md / scripts/check_outline.py | 原件引用 | 可固定同一段的起止行，保留发言身份上下文 |
| tests/test-point-discovery/test_outline_gate.py | 命令回归 | 追加新轮次仍可接续，已固定的段内改写后阻断 |

## Decision And Alternatives

复用 #194 的请求、决定和命令。历史记录无需用户转换格式，执行者负责回读原件并核实上下文。固定连续行段可涵盖标题、署名与答复；旧整件或单行索引继续按原契约校验。

## Detailed Change

本次范围与决定错配时说明模块或版本。待确认时展示当前版本并等待实际答复。大纲有效时直接检查其他前提，回到原问题或原来源补齐缺口后接续。具体稿的人工评审继续使用阶段7。

## Impact Analysis

阶段6沿用唯一问答 MD。明确采用于历史问答的树可以恢复，随后修订或撤回仍须依据当前记录处理。复用大纲时不会跳过问题处置与覆盖复核。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| RED → GREEN | 实际 CLI，向包含多行归属和原答复的问答追加一轮 | 修复前 block；修复后 allow；改写段内来源后再次 block | test_resume_uses_original_multiline_qa_after_later_rounds_are_appended |
| 命令回归 | python -B -m unittest discover -s tests/test-point-discovery | 本票分支 20 项通过 | 17 个大纲测试、3 个已有 XMind 测试 |
| 包及记录 | validate_create_skill.py skills/test-point-discovery --require-change-records | validated-candidate，P0=0、P1=0、P2=1 | 既有 description 的英文触发措辞提醒 |
| 实际 Skill 入口模拟 | 主持发送明确指定、收到待确认答复后另发确认；执行者读取 Skill、问答、原资料和同一 CLI 返回，并分别在聊天和文件执行 | 下表 | 本票实现者执行，主持身份为模拟用户 |

八个演练快照均使用虚构借阅材料。大纲 V1 指纹为 `2fec0208`，各场景沿同一个固定命令进入。

| 阶段6请求及历史记录 | 程序结果 | 实际聊天或文件结果 |
| --- | --- | --- |
| V1 已展示，无用户答复，要求聊天出稿 | block / exit 1，等待采用或确认 | 聊天指出 V1 与两个分支并等待，未给正文 |
| 相同停点，要求文件出稿 | block / exit 1 | 无新稿，原文件前后 SHA-256 均以 `93979b12` 开头 |
| 用借阅记录写预约 | block / exit 1，模块或版本不符 | 指明借阅与预约错配，未出稿 |
| V2 新增分支，仍提供 V1 决定 | block / exit 1，模块或版本不符 | V2 指纹为 `7af1b78e`，原文件前后均为 `93979b12` |
| 原树已明确采用，规划及阶段5覆盖就绪 | allow / adopt / exit 0 | 未重问；实际写入并回读含两个分支的 V1 待评审稿，文件 SHA-256 为 `c27baa7b185f60c0fb9cb4a402d745967ee519e6b95c0439c2cfec1b6db03afe` |
| 大纲已采用，阶段5缺少来源覆盖 | allow / adopt / exit 0 | 回阶段5读原资料，发现依赖的附录缺失，未出稿 |
| 大纲已采用，Q3 尚未处置 | allow / adopt / exit 0 | 回阶段4承接 Q3，未出稿 |
| 主持针对先前展示的 V1 明确答复 | allow / confirm / exit 0 | 重新核对问题、覆盖与资料；聊天给出登记和柜台归还两项并等待具体稿评审 |

## Safety And Privacy

公开材料仅含虚构场景、短指纹和程序验证结论。已检查本票变更，未发现凭据、私有资料、原会话路径或业务原文。

## Risks And Follow-up

实际入口演练验证当前 Skill 的代理工作流。程序核实引用及其字节，原话的业务含义及后续决定由执行者回读判断。未测试宿主全局拦截、应用运行或设备。整批最终版本的独立成稿与核对归 #199。
