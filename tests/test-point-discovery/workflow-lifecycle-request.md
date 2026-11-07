# #72 公开入口请求（模拟开发验证）

读取 skills/test-point-discovery/SKILL.md，以 fixtures/procurement-prd.md 和 procurement-notes.md 为原始资料，从规划开始梳理测试点；按资料提出建议，先展示表及实际关联图供决定，再逐轮澄清和评审。每轮只处理已实际收到的模拟答复，保存展示版本、答复原文、模拟来源、范围和未决状态。输出放本票 tests/test-point-discovery/workflow-lifecycle/。不要预填后续答复或golden答案，不调用外部模型/真实业务/下游。

采购限定流程完成后，独立读取 fixtures/lifecycle-prd.md 梳理优惠券测试点；不要把采购规则带入优惠券。XMind客户端验证未执行时明确未验证。
