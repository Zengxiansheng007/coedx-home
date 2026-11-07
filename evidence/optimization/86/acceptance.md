# #86 实现者逐AC核验

核验日期2026-11-07。所有业务材料、答复、具体批准均为SIMULATION开发输入。Root逐轮真实发送，隔离actor实际处理，当前文件实际读回。本记录是实现者核验，独立整票审查由Root另派。

## 同版身份

- 产品源码冻结提交 `4031335e97124c230ffb586b0d01b9e7ece62dbb`。其后 `f64cb2a3f68712f75f21c162342616ffaaf352d3` 仅新增source-freeze.md，未改产品。
- 本次完整回读green/的10轮实际输入、5份实际候选、round-06-questions.md、round-09-xmind-read.json及current.md，亦回读controller-inputs/的两份源快照、MD反馈和两份origin JSON。
- `git diff --exit-code 4031335... -- skills tests/test-point-discovery` 实际退出0，记录frozen-runtime-diff.log为空。GREEN使用同一冻结运行内容。
- 对原integration基线 `0fbe08efcb34f42c5b6a72c4c9129018620d95c6` 的保护路径检查实际退出0，protected-diff.log为空。覆盖工程/下游Skill、tools、reader目录、reader测试、旧反馈/XMind保真脚本和feedback/xmind/roles/workflow/progress历史运行目录。完整提交差异清单也未出现其他历史材料改动。

## AC1 三入口版本、范围及含义

限定模拟通过。green/round-01-candidate.md与round-02-candidate.md先分别展示表单/列表，Root第2/3轮实际批准后才创建同一current.md v1/v2。round-04-input.md固定聊天反馈、原展示及准确v2/hash，round-05-input.md才批准标题/保存修订。round-06-input.md固定MD反馈、准确v3、实际反馈hash，接收文件先提出问题。round-09-input.md记录XMind、旧v2源稿/hash与现行v4/hash，核对期间决定后形成候选，round-10-input.md才具体批准。三类接收或业务答复均保留未批准身份。

## AC2 聚焦展示及完整影响

限定模拟通过。RED第4轮重印正文必填和取消全文，真实失败保留在red/。GREEN的round-04-candidate.md聚焦完整标题适用规则与保存联动，未重印正文、取消或列表全文，说明三个渠道上限/提示/保存依赖及独立列表不受影响理由。round-07-candidate.md聚焦正文及保存，明确标题与正文不同计数口径。round-09-candidate.md聚焦标题及保存，短信12字与站内信/推送30字真实差异、正文60字保存前提均可恢复，说明取消/渠道/列表沿用。规则完整性通过逐条阅读判断，未用字串或节点数评分。

## AC3 省略保留及歧义删除

限定模拟通过。Root回传controller-inputs/returned-form-v3.md在原表单范围内缺失取消检查。round-06-questions.md实际问Q1删除或省略，未先删除。round-07-input.md实际回答“只是没放进回传文件”，后续候选只记录保留而不重印全文。实际回读current.md v5，取消原检查、三个渠道选项与列表两条检查均仍在，列表未纳入局部回传不视为删除。明确删除处理的静态契约同步保留，本次没有另模拟一个明确删除全流程。

## AC4 未知规则局部澄清

限定模拟通过。MD新增正文60字未定义计数和超限处理，round-06-questions.md实际提出Q2/Q3，指出标题口径不能作为正文答案，准确v3保持。Root第7轮实际回答正文Unicode计数、不trim、空格计入、仅空字符串为空、超限完整保留/阻止保存/提示60/不截断，round-07-candidate.md据此恢复正文和保存条件。其余标题30/10、取消及列表继续沿用，不因文件已改就推定规则全闭合，亦未将未答直接放产品区。第7轮答疑尚未批准，直到第8轮具体通过才写入v4。

## AC5 同一准确MD更新及读回

限定模拟通过。Root实际具体批准输入为第2、3、5、8、10轮，范围分别为表单、列表、标题/保存、正文/保存、短信标题/保存，对应同一green/current.md的v1→v5。第4、6、7、9轮记录候选前准确hash且明确保持，未把业务答疑当批准。独立物化v2/v3源快照与这些hash一致，最终v5实际读回标题30/12、正文60完整规则、保存同对象结果、取消与列表原文及历史说明。候选和合成XMind各保留过程/输入身份，期间决定未回滚。

最终current.md的实际SHA256为 `4F158778A6AABF81B530DEC80F293ED5EE79AD792A57662B10C2405DA81A763F`。正文与说明现行规则一致，20/10等旧值仅按其历史来源及替代范围叙述。

## AC6 三入口与XMind边界

三入口模拟及受支持格式解析通过，真实客户端往返未验证。round-09-xmind-read.json包含33个有序主题、原生ID及完整路径，status为read_for_agent_review；其来源hash与实际文件、native-feedback-origin.json相同。此为Root制作的合成单sheet文本树，原生格式可读不证明XMind客户端导入、编辑及保存。最终#88同版主流程补客户端证据，当前不声明该项已完成。真实业务和下游执行不在本次范围。

## 输入身份独立复核

| 物化输入 | 实际SHA256 | 核对 |
| --- | --- | --- |
| controller-inputs/accurate-v2-source.md | 74409871D6AB377625423C9768E45D999589C827BF8FFF2C31F18987CDC1FDEB | 与第4轮准确v2及native origin一致 |
| controller-inputs/accurate-v3-source.md | BE97C135AE0FDCC9DBB24B77AF3A77278298DB468E424271D8E46FDCAF815BBA | 与第6轮准确v3及MD origin一致 |
| controller-inputs/returned-form-v3.md | 0683C33824E7C1538DCEBF19A958C9A7585F5F6C7116ECF6357B598191FB29FB | 与第6轮反馈及MD origin一致 |
| controller-inputs/synthetic-title-feedback-v2.xmind | B03BD8727669AE2DAC1916E4748D9A33EF93C91895B5FEB441B208130619DD4B | 与实际reader输出及native origin一致 |

Root的taskroot/make86_feedback.py已只读核查，作用仅是按实际批准v3制作本例局部MD、按已保存v2制作明确标合成的固定文本树，并保留来源/hash。该任务外输入准备脚本未进入产品或本仓库，不生成反馈处理结果，不是通用MD导入器。实际反馈结果来自actor后续真实入口交互。

## 检查与限制

既有格式校验、reader3/3、历史feedback保真通过，沿用已冻结日志，不重复静态。旧check_xmind_outputs.py完整运行失败，StopIteration源于隔离目录缺原拥有根context/issues/75.md，原失败与日志保持，不改历史脚本或材料造通过。独立审查及Root最终统一checks.py尚待执行，不能称所有检查通过。
