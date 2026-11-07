# 通知任务准确测试点 v7（SIMULATION）

## 跨模块流程

### 【待产品确认】

- 无。

### 创建通知到审核通知

- 对符合修改后标题规则及其他已明确配置的通知送审，审核端收到同一编号待审核任务，按编号核对标题与本次提交一致，并核对通知维度。
- 衔接仍止于审核端收到，后续审核按独立模块既有范围。

## 【创建通知】

### 【待产品确认】

- Q9。三通知维度按有效手机号定向时，若该手机号匹配多个userid，应选择哪些目标用户、怎样去重，何种条件需要拒绝及拒绝结果是什么？
  - 虚构样例A同时匹配MOCK-U01和MOCK-U02，正确处理规则尚未给出。
  - 影响个人用户目标的一对多目标组成，以及保存后同任务编号列表、重新打开详情中的目标内容核对。
  - 第5轮主持明确后续问产品，仅暂留，未提供正确预期。
  - 对应正文路径为个人用户目标→手机号多匹配、保存→一对多目标结果。

### 【通知维度】

- 站内信
- 短信
- 推送

### 【标题】

- 必填，仅空字符串视为空，未填时拒绝保存和送审，适用全部通知维度。
- 中英文、数字、普通符号和空格每个计1，纯空格仍计数，适用全部通知维度。
- 特殊表情📨每个计2，适用全部通知维度。
- 长度上限
  - 站内信、推送30字符。
  - 短信
    - 最多12字符。
- 允许完整输入，超过所属维度上限时拒绝保存或送审，保留完整输入、不截断，提示该维度对应长度上限。

### 【内容】

- 站内信、推送
  - 自由文本，60字符以内。
  - 中英文、数字、普通符号和空格各计1，📨每个计2。
  - 允许完整输入，超过60时保存和送审均拒绝，完整输入保留不截断，提示内容上限60字符。
- 短信
  - 内容固定，只有验证码可修改。

### 个人用户目标

- 按个人用户定向，适用全部通知维度。
  - 有效手机号对应单一明确用户时，添加对应用户。
  - 有效手机号同时匹配多个userid时，目标处理结果待产品确认，见Q9。
  - 有效userid可添加对应用户。
- 从个人用户定向切换到全量个人用户，清空原定向选择，目标为全量个人用户。

### 保存

- 适用全部通知维度，标题满足既有计数、必填及所属上限，其他已明确配置成立时，保存本次编辑内容，在列表及重新打开详情中按同一任务编号核对已保存标题、内容、通知维度及已明确目标。
- 站内信、推送还须满足【内容】中已明确的计数口径及60字符上限。
- 手机号一对多的目标组成与保存目标结果待产品确认，见Q9。

### 取消

- 返回通知列表，不新增任务。

### 送审

- 适用全部通知维度，标题满足既有计数、必填及所属上限，其他已明确配置成立时，送审检查到审核端收到同编号待审核任务，核对本次提交标题与通知维度。
- 站内信、推送还须满足【内容】中已明确的计数口径及60字符上限。

## 【审核通知】

### 【待产品确认】

- Q8。对收到的待审核任务执行通过、驳回时，审核意见是否分别必填，意见为空是否允许各自动作完成？
  - 通过侧影响必要意见条件、空意见能否完成通过并达到已通过状态。
  - 驳回侧影响必要意见条件、空意见能否完成驳回并达到已驳回状态。
  - 第5轮主持明确后续问产品，未提供正确预期，第6轮要求继续保留。
  - 对应正文路径为通过→意见条件、驳回→意见条件。

### 查看

- 审核列表列出收到的待审核任务，任务编号与创建端一致。
- 对按修改后标题规则送审并收到的待审核任务，按同一编号查看标题与通知维度，核对本次提交对应一致。

### 【标题】

- 只读展示，不在审核端编辑。

### 通过

- 对收到的待审核任务完成通过后，同一编号任务状态为已通过。
- 审核意见必要条件及空意见通过结果待产品确认，见Q8。

### 驳回

- 对收到的待审核任务完成驳回后，同一编号任务状态为已驳回。
- 审核意见必要条件及空意见驳回结果待产品确认，见Q8。

## 资料与Agent交接说明

- 模拟开发验证。准确v7仅更新第15轮实际A选择的文档交接状态、范围和用途，具体检查正文完整沿用已评审准确v6，不改业务规则。短信12及其层级和公共继承、站内信/推送标题30、内容60、原三维度操作、取消、目标/独立切全量、跨模块及审核内容、Q8/Q9完整事项与短引全部保留。唯一准确路径为本文件，历史候选与过程材料保持原身份。
- 已评审来源为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-02-candidate.md` v0.2的“创建通知到审核通知”两条。批准原文见 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-03-input.md`，明确只通过此范围，批准创建本准确MD，创建模块正文未批准。
- 原始资料 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/inputs/final-shared-fields.md` v1。A3送审进入审核流程、A4审核收到待审核任务/同编号/标题与维度，结合第2轮Q5实际终点决定，映射到本文件两条跨模块衔接。第2轮实际答复原文 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-02-input.md`。
- 新增批准来源为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-05-candidate.md` v0.5全部创建正文，第6轮实际批准原文见同目录 `round-06-input.md`。其中Q9的批准是完整问题及暂留表达通过，业务处理仍未知。
- 审核批准来源为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-06-candidate.md` v0.6，第7轮实际具体评审原文见同目录 `round-07-input.md`。通过范围为查看同编号任务及提交标题/维度、标题只读、通过后同编号已通过、驳回后同编号已驳回、Q8完整产品事项及两处短引用。该批准不提供意见必填或空值允许答案。
- 本轮业务修改依据为同目录 `round-08-input.md`，具体部分评审原文为 `round-09-input.md`，实际展示为 `round-08-candidate.md` v0.8及 `round-08-display.md`。第9轮通过30/10规则及正向保存/送审和接收查看关联，明确不纳入候选保存下“标题未填或超所属上限时…不能把…”及送审下“标题未填或超所属上限时…不将…”两条重复，故不合入这两句，不作为待补业务检查。
- 内容修改依据为编辑回传 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/client/markdown-feedback-v4.md`，第10轮实际读取时SHA256 `3C936C10181E527BFF6337255518A3268CE8BB6B9DFD5EAC29ADA75E7E4185E8`，身份为回传输入，非准确文件。第11轮 `round-11-input.md` Q10确认取消仅省略，Q11/Q12给出内容计数/超限规则，未新增内容必填或短信60限制。第12轮 `round-12-input.md` 具体通过 `round-11-candidate.md` v0.11，批准内容与操作联动，不允许以局部稿替换短信原操作检查。
- 原生反馈业务批准来源为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-13-candidate.md` v0.13及 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-14-input.md` 第14轮实际评审。仅短信10→12与父子层级及相关继承/操作/接收通过。v0.13的“同目录”歧义引用没有作为通过引用沿用，原v0.13文件保留历史原件，以下使用准确绝对路径。
- 原生导入源为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/client/accurate-v3-client-input.md`，历史v3快照SHA256 `37B987BE36FCDC33EB2C89F0AE7A7C98DE7288AE0F685E7AA924734CA82B5A30`。原件 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/client/imported-original.xmind`，SHA256 `cf70c6d4936afcd4013dc60cd93ede46449738157330fdff695b509fa2d79e9d`，597112字节。回传 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/client/returned-edited.xmind`，SHA256 `4ff720c8f19c3a4716f5caaab3cf8a9c5b6d082fbf5037b66516b74aac8a2698`，597564字节。
- 本角色实际读取证据分别为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-13-input.md`、`C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-13-original-read.json`、`C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-13-returned-read.json`、`C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-13-structural-comparison.json`。两次真实helper读取均exit0/status=read_for_agent_review，74→75主题，无删除。新增短信父题，原短信上限子题变为最多12字符并移入其下，其余主题保持。当前v5期间聊天/MD有效决定叠加保留，不按旧v3原生内容回滚。
- 已实际读取并在第15轮引用回读时核对客户端执行记录 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/client/roundtrip.md` 的实际追加内容。据Root记录，About运行版本26.04.01327，客户端操作覆盖历史v3导入、保存原件、另存副本、短信文字/层级编辑与保存，原件hash保持。追加的“Completed native feedback cycle”记录本角色实际双原生读取、第14轮具体批准、同MD准确v6更新回读及Root对30/12标题、内容60、操作适用、取消和两产品问题的检查，并记录第15轮实际A选择。该证据按各自阶段/版本保留，本角色未亲见UI。记录中最终交接MD精确版本客户端导入与盲接收者恢复仍待完成，后续结果以该路径实际追加记录为准，本MD不预填尚未执行结果。
- A1→创建通知维度、标题必填和原20/10上限，第2轮Q3曾裁决当时推送20。第8/9轮限定替代站内信/推送20为30，第13/14轮原生反馈与具体评审替代短信10为12及对应层级，当前为30/12。第3轮Q1→中英文数字普通符号空格各1、纯空格仍计数、📨各2、其他emoji排除，Q2→未填/超限保存送审拒绝、完整输入保留不截断、提示对应维度上限，均继续有效，短信移位仍继承这些共用规则。B1旧30仍是历史观察，当前30依据为第8/9轮，不是旧页面。
- A2→内容原差异、有效手机号/userid定向、定向切全量独立场景。编辑回传及第11轮Q11/Q12、第12轮评审→站内信/推送内容60、中英文数字普通符号空格各1、📨各2、超限保存送审均拒绝/完整保留不截断/提示60。短信固定仅验证码可改，60及该内容超限规则只适用两个自由文本维度，其他emoji仍排除，未新增内容必填。映射实际输入 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/inputs/final-target-map-mock-v1.json` 版本`mock-target-map-v1`，样例手机号对应MOCK-U01与MOCK-U02，是虚构输入、非数据库结果，未给处理规则。第5轮Q9后续问产品→创建顶部完整问题、个人目标及保存短引，不推定选择、去重、加入或拒绝。
- A3→取消返回列表不新增、保存当前编辑内容、送审进入流程。第2轮Q4→保存列表/重开详情、同编号核对标题/内容/维度/目标，不另加状态名称，一对多具体目标等待Q9。Q5→送审止于审核端收到并核对提交标题/维度，其后审核独立查看、通过、驳回，止于PRD对应状态，不延到送达。终点自v2已纳入，本v4补入按30/10标题规则成立的正向前提与对应保存/接收回显，契约终点未延长。
- A4→审核查看同编号待审核任务/标题/通知维度、通过后已通过、驳回后已驳回；A5→审核标题只读，均由v0.6实际展示并在第7轮通过后纳入本v3。第5轮Q8后续问产品→审核顶部完整问题与通过/驳回各自短引用，意见必要条件、空意见动作结果仍未知，不据已知状态推断允许或拒绝。Q8不影响已通过接收终点或创建其他检查。
- 默认共用三创建维度相同标题、计数、超限和目标规则，上限/内容真实差异在字段下保留。第2轮Q7决定各模块分别表达、不跨模块提公共规则，审核只读不继承创建输入规则。A5创建实际控件是否共用仍未知，下游现场核实必要验证范围，共用表达不能推断只验证一次。纯技术定位与控件事实交下游，若证据改变业务含义则回澄清及具体评审。
- C1排除附件、设备推送、性能压测、最终送达，第2轮Q6排除两人同时修改，第3轮Q1排除本轮其他emoji，持续有效。Q8/Q9是暂留而非排除，已知规则和未知影响分别保留。
- 同一过程实际路径 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/process.md` 的“永久来源与决定”“永久问答 round-02/round-03/round-05/round-06/round-07/round-08/round-09/round-10/round-11/round-12/round-13/round-14/round-15”“round-15交接决定与回读”保存问答、来源、批准范围、引用纠正、交接选择及收尾历史。原文在该准确文件所在目录的逐轮input材料，历史候选不代替本准确文件。
- 已逐项核对A1—D1、新映射及实际答复，规则差异、特殊计数、空字符串/纯空格、独立切全量、操作终点、审核已知结果与两项产品事项均有去向。文档具体评审不证明Q8/Q9规则已明确或真实业务验收。下游负责完整用例、整轮P0范围/报告/证据及缺口核对，处理必要未决后由用户手动启动P1/P2。本次交接不表示数据已准备、P0已通过，或已获执行、合并、自动启动授权。通用MD程序直导未验证，本阶段为阅读文档交接边界。
- 第15轮实际交接决定为Q13选择A，先交明确分支，供后续人员编写完整测试用例。原文为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-15-input.md`，其指向的第14轮建议范围为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/final-main/round-14-display.md`。本次交付载体为本唯一准确MD及实际引用，不新建第二份准确文件，不调用下游。
- 本次已决定可交范围为创建标题30/12及公共计数/空值/超限规则，内容60及短信固定内容差异，有效userid或手机号单一明确用户目标，以明确用户选择为前提的定向切全量，取消，明确目标条件下保存列表/重开详情核对与送审到同编号待审核接收，审核列表/按编号查看标题维度/标题只读。依据分别为正文对应路径及来源A1—A5、实际规则答复和第3/6/7/9/12/14轮具体评审，这些分支可避开Q8/Q9未知条件独立设计。
- 本次保留未交范围为Q9一对多手机号目标选择/去重或拒绝、目标组成及其保存/送审依赖；Q8审核意见必填性、空意见动作结果及通过/驳回完整操作前提相关分支。已知动作成功后状态仅为已有规则，不能据此猜测意见前提。完整Q8/Q9与所有未交分支继续保存在相应模块顶部/正文/短引，未删除、未视为已答、未永久排除。用户选择只决定当前文档范围，未知规则仍待后续澄清。
- 第14轮的A/B/C建议是历史建议，第15轮实际A选择替代当时未选择状态。控件实现和必要验证次数继续留给下游现场核实，共用表达不代表只测一次，技术定位/控件观察保持实际证据身份；若影响业务含义、范围或预期，则返回本流程澄清及具体重审。当前完成所选文档范围的记录与回读后结束等待，没有下游工具调用或业务执行。
