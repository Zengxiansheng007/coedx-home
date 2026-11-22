# 模块资料与Agent交接说明

步骤技术说明始终绑定分组、组内序号与中文操作，即使未提供来源或行号也可定位。仅在相同适用范围内去重；不同步骤的相同策略分别保留定位，不合并为无归属说明。

按完整模块路径，仅为有直属用例的模块生成一个同级说明分支。父模块无直属用例时不生成空分支，不扩展范围或创建画布。

来源种类、数字行定位、候选版本映射和详细评审/合并/执行状态集中在说明分区。原始来源、内部身份和完整约束仍保留于同版本候选。旧版非结构化技术原文不直接显示，使用明确读取义务指向当前候选；不能以指针宣称满足执行约束。

Agent按语义把通用治理说明放入用例或步骤的 `technical_handoff` 对象，例如 `{"reuse_policy": "每次重新核对授权", "invalidation_action": "失效后重新澄清"}`。原有业务字段保守保留：当日有效、业务复用限制、角色、初始状态、输入与预期留正文，不能凭字段名自动迁移。暂定/未决规则及产品核实要求仍可见。分类不清继续已有澄清流程。

human-view和XMind读取同一候选并分区输出；说明不写入动作和参数。说明节点无可写业务绑定，原样返回无变化，修改说明需明确聊天解释。历史回传只重建已知旧版布局并核对版本与身份。native测试仅验证受支持content.json格式，不等于真实客户端验收。

Referenced steps resolve through the checked shared-step resolver before extracting source locations and technical instructions. The current referencing case, group and ordinal own the projected note.
