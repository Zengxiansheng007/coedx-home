# coedx-home
家用电脑编写的skills

## Codex 开发流程技能

这里保存 develop-system 调度器、ask-matt 导航员及定制开发技能。相关引用、脚本、调用策略和许可证随目录保存。

仓库另有独立的 [test-case-authoring](.agents/skills/test-case-authoring/README.md) 与 ask-test。开发套件及调研、验证、技能维护等配套工具的跨机同步范围见 38 项[同步清单](docs/development/skill-sync-list.json)。

- 导航：ask-matt。只推荐流程与技能。
- 准备：setup-matt-pocock-skills。
- 需求与设计：triage、grill-with-docs、grilling、research、domain-modeling、wayfinder、prototype、codebase-design、improve-codebase-architecture、to-spec、to-tickets。
- 开发与测试：implement、implement-spec、tdd、diagnosing-bugs、code-review。
- 交付与复盘：pr、wizard、retro。
- 配套辅助：writing-for-agents、wait-what、handoff。

### 安装与调用

本仓库克隆后，`.agents/skills/` 是项目技能目录。跨项目使用时，按同步清单从同一个 Git 提交复制完整技能目录到 `~/.agents/skills`，保留目录的同级关系。先检查该位置与原有 Codex 技能目录的同名项，备份本机定制，避免重复加载。涉及外部服务或工具的技能需要在目标电脑按用途完成单独配置。

使用 `$ask-matt` 获取导航建议；使用 `$develop-system` 启动/恢复流程。它只调度，专业技能执行实现、测试与评审，完成后回流调度器。没有后台唤醒或宿主完成钩子。

直接调用 grill-with-docs：澄清 → 保存需求文档 → 用户确认当前版本 → 展示 to-spec / implement → 等待用户选择。受管根访谈回流后，由 develop-system 按明确条件自动选路。

在具体开发项目首次使用时，调用 `$setup-matt-pocock-skills` 配置该项目；GitHub 凭据保留在用户本机或连接器中。

### 检查

```shell
python -m pip install -r requirements-checks.txt
python -B tools/checks.py
```

也可运行 `npm run check`。验证用户级副本时，可以运行 `python -B tools/checks.py --installed ~/.agents/skills`，并将参数替换为目标电脑的实际绝对路径。统一入口检查工作流、验证工具、技能格式、注册表和副本一致性，并保留退出码与原始输出。Windows 和 Linux 的 GitHub Actions 使用同一入口。使用细节见 [验证说明](docs/development/verification.md)。

### 来源与许可

工程技能基于 Matt Pocock 的技能，保留各目录原始 LICENSE 与已有 source.json。develop-system、ask-matt 和 grill-with-docs 包含当前定制；调用策略以各技能 agents/openai.yaml 为准。不是 Matt 官方原仓库的完整镜像；导航地图提及的其他未安装技能不包含在这次发布中。
