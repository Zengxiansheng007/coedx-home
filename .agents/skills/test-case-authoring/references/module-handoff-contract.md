# 模块 Agent 说明单处维护

业务稿顶部只有一个配套资料入口，直接链接必要说明。角色、初始状态、条件、动作、预期、独立验证与业务限制留正文。技术来源、版本映射和配置定位外置。不得生成独立索引、项目共用文件、逐批说明副本或 human-view 总文件。

用例或步骤 technical_handoff 是已有候选中的可选技术字段，不新增必需 JSON 包。已有权威材料使用 source_ref 直接引用，写入入口校验本地目标存在；不复制原文。新增技术文字使用原有对象字段。来源与数字定位保留适用用例、步骤组和序号。状态与历史只读原候选，不复制成第二权威。

write_artifacts(result, output) 是文件交付公共适配器；authoring、scoped_review、extension、dependencies CLI 均调用。output 是批次目录；同一项目各批次放在同一父目录，父目录 agent-notes 中按完整模块路径稳定定位一份 Markdown。不同批次更新相同文件及用例段落，未选用例不删除。纯 render/build 返回的是待保存视图，只有 write_artifacts 成功才可宣称链接文件已交付；恢复后重新读取原候选并调用同一适配器。无需新建配套索引或模块包。

跨模块确需新增共用内容时，先评审选择一份已存在说明的章节。当前用例 technical_handoff.shared_section 可携带 source_ref、section、content、review_reply；缺少真实评审依据或目标不存在拒绝写入。这里的 review_reply 是调用方提供的评审证据，程序不判断其真实性。它不是业务批准。模块差异仍留各自正文/说明，绝不默认首模块。其他模块通过 source_ref 引用该章节。

无必要技术内容不建说明。human-view 只在对话展示。Markdown / native content.json 回流核对同版本顶部入口与完整身份；技术说明的修改应由明确评审更新原材料，不经业务标量回写。native 格式测试不等于 XMind 客户端验收。

非同级输出目录恢复时，在该模块用例既有 technical_handoff.document_ref 指定原说明路径；同模块不允许不同目标。planned 是纯构建返回状态，write_artifacts 写入并回读后返回 materialized；此状态只描述文件交付，不授予业务验收。

For explicit, version-bound semantic partition of existing metadata and repeated governance, follow [source-assessed display](source-assessed-display.md). Original case/data values remain authoritative; no field-name deletion policy applies.

## 本地资料链接交付与移动

write_artifacts 在落盘时把顶部入口的本地模块说明、source_ref 和 shared_section 路径按 output 解析成经过百分号编码的绝对 file URI；空格、中文与括号不改变目标。已有远程来源沿原处理规则，来源可读性仍由 preflight 检查。纯 render/build 保留相对引用；候选、业务版本和说明所有权不因交付位置改变。使用落盘后的 xmind.md 导入客户端。

同模块说明仍只维护一份。移动单独的 XMind 回传文件不会重定位说明；移动整套资料后，应从原候选在新 output 重新执行同一交付入口，再导入新稿，不手工替换未知链接。跨机器分享前重新定位材料；本机绝对路径不得作为公开夹具提交。

客户端可能显示本地文件信任提示或要求用户选择打开方式。由用户处理，禁止自动抑制提示或替用户确认。文件存在与解析通过不等于实际打开成功；分别记录客户端本地识别、实际内容显示与反馈回传证据。

## 当前交付、生命周期与候选定位

Codex交付当前 xmind.md 与必要 Agent Markdown 说明；用户自行导入 XMind。原生 .xmind 仅作为既有历史客户端证据或用户实际回传输入保留。本轮文件检查和解析回归不宣称新客户端验收。

write_artifacts 先读取当前来源进行 preflight，仅对完整还原通过的当前选中用例维护生成段。该用例已无技术内容时移除其旧段；未选中、来源缺失/读取失败或 blocked 用例保持旧段及其原版本。最后一个生成段移除后，若只剩精确的生成标题则移除空文件；人工内容与其它用例段保持。

每段包含绝对 candidate.json 文件 URI、/cases/序号 JSON Pointer、原 content_version 与语义/数据版本。writer 保存完整原候选（包括 blocked 用例），已有等值候选保持原始字节；CLI复用同一保存入口。纯渲染仍是 planned，不宣称文件已存在。数据仍按候选 data 与步骤 data_refs 精确关联，不能把不存在的 data.json 或正式执行 typed refs 说成该入口的输出。

后续批次使用新的同级 output 目录，更新同一模块说明的当前用例段，保留其它段原候选位置与版本。若同目录覆盖会破坏保留段依赖的旧候选，写入前明确拒绝并保留所有旧文件；调用方改用新同级目录，不生成第二权威或逐批说明副本。读取段时必须核对候选版本、位置与用例身份；漂移回到来源核实，不按相似标题猜测。

中文显示只属于 Agent 说明：已知字段附原键，已知控制枚举附原值；未知键值与实际输入保持原文。映射基于字段位置，嵌套输入或 value 中的 add 不译为新增。共享业务投影、反馈协议与候选版本均保持；纯展示不新增投影评估记录。

## 已声明来源与审计职责

context claim、step/expected/verification 与 data 根的 source_ref 是已声明溯源位置，
在现有 Agent 说明中保留适用对象与定位，不作为业务角色、参数或预期。
data.value 和真实输入/产出中的同名键沿业务字面值保留；未知业务字段不按名字外置。
final_review、review_history 及 supplied_content_confirmation 属于已知审计契约，
说明优先链接实际 qa_ref/source_ref；无独立定位时指向该用例已链接候选内的精确字段路径，
原始文字仍在 QA/候选中。说明不复制长问答，也不把 user_rule 等真实或未知业务规则误当回执。
已知控制状态继续只读原候选；具体分级风险理由可在说明读取，真实业务条件及特殊项仍在正文。
