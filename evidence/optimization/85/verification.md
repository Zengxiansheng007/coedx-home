# #85 实现者逐AC核对

日期为2026-11-07。当前源码以已接受的 #84 集成 922493c2403b3fb8f11ab73e391df39c3915db41 为基线。产品写集只有入口 SKILL.md 与 references/writing-review.md。本票将写作中新缺口的局部往返集中为可执行步骤，沿用 #81 实际问答和 #84 逐操作业务结果契约。

## 行为证据与版本

Root 派出的fresh actor使用原 evidence/optimization/85/request.md 和 input.md，在本票冻源上执行三轮。已完整回读 green/ 的三版 candidate、response、conversation、sources，共12份实际文件。actor的 sources-v1.md 声明未读取 issue、plan、rubric、diff 或 RED。所有资料及答复均为SIMULATION，Root逐轮真实发送答复，演员未预填未来结果。

冻源 source-manifest.json SHA256为 bcb94e52aef38fbd5c46a3ce1da3d8ddd870d8a2a0bbd50cdd6eb36a5a53dbf5。post-green-identity.json 回核19份产品MD及2份原请求/输入全部一致，记录21份实际baseline/GREEN文档的物理SHA256与大小，未改旧actor稿。其身份是物理文件字节，不冒充Git原始blob身份。

## 逐AC结论

| #85 AC | 本样例结论 | 实际观察与定位 |
| --- | --- | --- |
| 1 写作新缺口真实回问并局部暂停 | 通过 | green/conversation-v1.md 记录写作自检发现重叠人数和编辑保存对象缺口。response-v1.md 实际提出Q1、Q2，提供选项、假设例、推荐及等待代价。candidate-v1.md 中未知留过程说明，没有自动产品化。人数仅暂停重叠口径，既有无交集人数、名称、选组、P3保存及P4取消继续。 |
| 2 明确部分继续保持候选身份 | 通过 | 三版candidate及对应response均为待评审，没有准确MD或交接。v1沿用D2继续明确部分。v2承接实际答复后继续新建保存、取消及已知人数。v3仍请求具体评审，第3轮规则答复没有被当作通过。 |
| 3 实际转产品后顶部完整问题与短引用 | 通过 | conversation-v2.md 保留Root明确“先待确认，后续问产品”及其他范围决定。candidate-v2.md 顶部Q1写完整计数问题、甲乙重叠条件、影响的【已选人数】路径及决定来源。正文人数及保存中的重叠人数预期只短引Q1，已知组选项保存仍明确保留。 |
| 4 顶部正文一致且未知未当确定预期 | 通过 | v2顶层Q1与正文短引用均指多选组同一人员的计算口径，说明区进一步列出两个引用路径。没有将提问中的3人/4人变成未知期间的结果。保存中已知的名称和组回显与未定人数分开，短引用保持预期待明身份。 |
| 5 后续答案只恢复受影响内容并保留问答 | 通过 | conversation-v3.md 是Root实际去重答复，candidate-v3.md 恢复唯一人员标识规则及甲乙2→3→2，保留甲丙2→4→2、字段规则、新建保存、取消及编辑保存排除。Q1退出当前产品区，原问题、暂留与新答复原文/来源仍可从同文说明及引用恢复，没有全量重问。 |

## 基线正向行为与真实偏差对照

baseline-review.md 已完整记录8369ca5上的三轮。基线首轮已能发现计数缺口，R2实际暂留后顶部/正文及局部继续正确，R3实际回答后恢复并保存历史。这些正向行为保持原通过身份，本票不将其包装为旧版失败。

基线三稿均在来源未明时给出“编辑已有草稿保存后按原编号定位”的确定检查。GREEN首轮则在Q2实际询问是否支持编辑保存，以及更新原编号或另存的对象结果，未提前给出确定检查。Root第2轮只将新建保存纳入、已有草稿保留取消、编辑保存排除，actor据此关闭本轮范围问题，同时明确实际业务是否支持编辑保存仍未知，没有把排除说成不支持。该差异是实际观察结果，前后源码还包含 #82/#83/#84 变化，不能据此单独证明 #85 是唯一原因。

后续恢复使用Root明确要求保留历史、沿用其他范围的实际答复，证明该限定接续行为，未另测省略这些措辞的任意简略答复。没有用未执行场景虚构失败或通过。

## 静态、复用与范围

static-checks.json 保存精确命令和结果。复用 C:/DevelopTool/Python311/python.exe，不安装依赖。受影响Skill格式exit0，73个本地Markdown引用无缺失，git diff --check exit0，.agents、skill-packages、native-reader脚本及既有 #80—84证据保护路径diff exit0。活跃fixtures/optimization-85-input.md与原input.md逐字节一致，没有预先补编辑保存答案。

同步了本票活跃普通请求及隔离rubric，既有writing-request.md/rubric.md仅添加当前局部往返入口与身份判据。#81问答参考和 #84 操作契约没有再次改写。Root最终统一执行tools/checks.py，本票不重复全仓验证。

## 执行限制及剩余边界

GREEN写入曾遇到Windows长Base64 payload启动前失败，任务根已记录PS-INC-20261107-013，失败未执行载荷。后续实际文件已由actor完成并完整回读，sources-v2/v3记录使用apply_patch，最终物理身份由post-green-identity.json保存。该运行故障保持独立于产品语义结论。

candidate-v1.md中来源使用“同目录input.md”简写，实际输入位于green上级；sources-v1.md给出完整仓库相对来源，manifest绑定准确路径。v2/v3仍使用input.md短名并由sources及同文问答引用恢复。本票没有修改actor原稿，单文件来源引用的进一步独立恢复属于 #88 同版闭环，不把当前候选当作已完成交接。

未执行真实业务、下游、全局安装、远程写入或XMind客户端。当前结论仅为本票限定三轮模拟行为与静态一致性，具体测试点仍待评审，准确基线与交接未发生，Root独立整票审查仍待完成。
