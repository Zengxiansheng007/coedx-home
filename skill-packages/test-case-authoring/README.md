# test-case-authoring

独立的用例编写技能，直接调用 `$test-case-authoring`。完整目录包含入口、按需契约与本地 Python 辅助工具；本仓库 `.agents/skills/` 为项目副本，`skill-packages/` 为同内容分发镜像。本技能不在 develop-system 注册执行器中。使用项目副本即可；本交付不安装全局技能。

## 开始一批编写

例如：`$test-case-authoring 根据这份合成录制和人工测试点编写 P0；先展示转译检查结果，再按批澄清。只编写，不执行。`

提供一条独立场景的 Playwright 录制文本，或完整手写 P0；PRD 可选。保留来源位置，凭据仅提供引用。扩展 P1/P2 需要人工测试点、相关 UI 资料，以及批准范围内全部 P0 的同版本完整报告和必要证据。示例和模拟答复应明确标记为合成材料，不能用于真实业务通过结论。

1. 技能读取源文本并形成解释，经公开转换入口生成候选、四列 human-view 和同版本 XMind Markdown；录制代码只读不运行。
2. 独立问题同轮提出，依赖问题后移。答复仅记录问答；汇总理解获确认后统一更新，再对完整当前版本单独作最终评审。
3. P0 评审后推荐用户另行启动 ui-test。正式脚本、完整执行和用户启动的 P0 正式合并由后续 ui-test 接口承担。
4. 用户手动请求 P1/P2 时，先读取全范围 P0 报告并检查疑似 P0 漏项，由用户裁决。暂定规则下通过仍需明确继续决定。
5. P1/P2 默认审阅本轮范围 Markdown 和覆盖说明，按需展开某案 human-view。边界分别成例，优先级与额外组合交用户决定。
6. 聊天、实际编辑 Markdown 或回传原生 XMind 均先对照初始副本核差异，再澄清、统一更新并最终评审。未展示案例不视为删除。
7. 用户明确启动并指定已评审范围后，仅向隔离全量目录增量合并 P1/P2。检查各案 applied/pending、原因和版本；保留未批准内容。然后推荐用户另行启动 ui-test。

执行条件、上下游完整引用、对象绑定和数据有效性写在用例中；不另建执行交接清单。评审、合并、执行分别记录，设计覆盖不代表执行通过。

## 本地辅助入口

使用 Python 3.10+，从本技能目录运行（输入为已授权、已脱敏文件；每次使用新输出目录）：

```text
python -B scripts/authoring.py --recording recording.ts --interpretation interpretation.json --output-dir candidate-output
```

解释 JSON 由技能结合实际材料生成；它不是任意 JavaScript 的自动解析器。手写入口、澄清、范围、报告、扩展、反馈与合并 API 均从 [SKILL.md](SKILL.md) 对应分支进入契约，不自行构造执行就绪资产。Markdown 可导入 XMind；原生反馈支持的客户端/格式范围见 [原生反馈契约](references/xmind-feedback-contract.md)，不识别的结构保留待核对。

## 当前能力边界

隔离结果明确返回 `formal_sync: pending_joint_validation` 和 `execution: not_started`。本包不启动浏览器、准备业务数据、生成/执行正式脚本或写入正式 ui-test 资产。候选 JSON 不是正式 Source Case v2。

后续正式接口依赖公开工单：[#58](https://github.com/Zengxiansheng007/coedx-home/issues/58) 接收已评审 P0、映射正式源并验证；[#59](https://github.com/Zengxiansheng007/coedx-home/issues/59) 验证后按用户指令正式合并 P0；[#60](https://github.com/Zengxiansheng007/coedx-home/issues/60) 未自动化 P1/P2 正式合并后再执行；[#61](https://github.com/Zengxiansheng007/coedx-home/issues/61) 跨模块前后置与数据关联的正式接入；[#62](https://github.com/Zengxiansheng007/coedx-home/issues/62) 为配套完成后的真实联合验收。本交付不启动这些工作。结构校验、合成隔离测试、实际 XMind 客户端观察和真实业务联合验收分别报告；前三者不能替代真实公告主链路验收。
