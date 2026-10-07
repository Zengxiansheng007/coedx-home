# coedx-home
家用电脑编写的skills

## Codex 开发流程技能

这里保存当前定制版本：develop-system 调度器、20 个注册执行技能，以及 ask-matt、writing-for-agents、wait-what、handoff，合计 25 个技能目录。相关引用、脚本、调用策略和许可证随目录保存。

- 导航：ask-matt。只推荐流程与技能。
- 准备：setup-matt-pocock-skills。
- 需求与设计：triage、grill-with-docs、grilling、research、domain-modeling、wayfinder、prototype、codebase-design、improve-codebase-architecture、to-spec、to-tickets。
- 开发与测试：implement、implement-spec、tdd、diagnosing-bugs、code-review。
- 交付与复盘：pr、wizard、retro。
- 配套辅助：writing-for-agents、wait-what、handoff。

### 安装与调用

本仓库克隆后，`.agents/skills/` 是项目技能目录。全局使用时，将需要的完整技能目录复制到 `$CODEX_HOME/skills`（默认 `~/.codex/skills`），保留同级目录关系；建议整套安装以满足相互引用，已有定制目录先备份再更新。

使用 `$ask-matt` 获取导航建议；使用 `$develop-system` 启动/恢复流程。它只调度，专业技能执行实现、测试与评审，完成后回流调度器。没有后台唤醒或宿主完成钩子。

直接调用 grill-with-docs：澄清 → 保存需求文档 → 用户确认当前版本 → 展示 to-spec / implement → 等待用户选择。受管根访谈回流后，由 develop-system 按明确条件自动选路。

在具体开发项目首次使用时，调用 `$setup-matt-pocock-skills` 配置该项目；GitHub 凭据保留在用户本机或连接器中。

### 检查

```shell
python -m pip install -r requirements-checks.txt
python -B tools/checks.py
```

也可 `npm run check`；额外检查全局副本用 `npm run check:local`。统一入口包含 67 项状态/路由测试及 8 项检查工具回归、核心技能格式、注册表和副本一致性，所有命令产生实际退出码与原始输出记录。Windows/Linux GitHub Actions 使用同一入口；使用细节见 [验证说明](docs/development/verification.md)。

### 来源与许可

工程技能基于 Matt Pocock 的技能，保留各目录原始 LICENSE 与已有 source.json。develop-system、ask-matt 和 grill-with-docs 包含当前定制；调用策略以各技能 agents/openai.yaml 为准。不是 Matt 官方原仓库的完整镜像；导航地图提及的其他未安装技能不包含在这次发布中。
