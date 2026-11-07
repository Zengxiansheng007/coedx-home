# #87 GREEN 源码冻结

- 正式依赖基线为 `3cae1a783ddf43a0106d7ba6dc5e1072651693be`。
- 实现及 RED 原件提交为 `2b3b610b07a7c55a0273855767a5fb922ddb5f4e`，分支 `codex/tpd-opt-87`，提交后工作树干净。
- 本记录随后以文档提交保存。GREEN 期间产品/活跃测试内容保持该提交字节，若发生新源码修改须新一轮记录及重新验证。
- 产品范围为 SKILL.md、module-clarification.md、review-and-progress.md、writing-review.md 四份，均位于 skills/test-point-discovery。新增三个活跃请求/fixture/rubric。没有 helper/runtime/依赖变化。

## 冻结时工作区物理 SHA256

| 产品路径，相对 skills/test-point-discovery | SHA256 |
| --- | --- |
| SKILL.md | 305301a5af21c5b48a5a6d84cafd52480a5dfa3c57897a088f2c9c0d4f678674 |
| references/module-clarification.md | 1008a495de1c80f77982ef53565e1abb743095a3487902b100bc64263ec0a2a9 |
| references/review-and-progress.md | 6a62a3b8868d44f8eb1d772b66f4cce663271c3f444faf30d88aa9a42609065f |
| references/writing-review.md | da898759db26fdd2559be882d2113e1090bb4588ea6db5b081fde2b3e6b84898 |

## 待执行 GREEN

Root 派 fresh actor，选择本票普通 request/input 或新增 tests 入口与 fixture，明确其实际路径，输出到本目录独立 green/。actor 不接收本记录、plan 或 rubric。Root 逐轮发送实际答复/暂停恢复/具体评审，后续补交真实模拟快照并引入关联变化。

重点观察同一过程 MD 的临时覆盖与永久问答、未处置项保留、当前范围具体评审后同一路径准确更新、永久依据保存回读、真实限定清理与回读、清理后仅重开影响部分及新 B/Q。上述行为尚未执行，不登记通过。

定向静态结果见 verification.md。RED 原始输出不修改。真实客户端及业务均未验证，最终全仓聚合留给 Root。
