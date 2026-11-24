# CR-20261120-001 - XMind 总图索引外置

| Field | Value |
| --- | --- |
| Status | applied |
| Target Skill | ui-test |
| Change Type | fixed |
| Scope | references-and-assets, scripts-and-validation, downstream-and-handoff |
| Source | 用户确认的 #153 XMind 导入缺陷修复方案 |
| Baseline | `346cdbe87ce1aafb65bd4fa8cbc736ff5fefee9c` |
| Author | Codex |
| Related Records | CR-20261119-148, CR-20261119-153 |

## Summary

总图和分图 Markdown 用于 XMind 导入，刷新索引随输出保存在 `.case-map-index/`。

## Context And Problem

Windows XMind 导入时把总图末尾的内嵌 HTML 注释呈现在根主题。注释包含用例构建版本、分图路径与校验值。

## Sections Changed

| File | Section | Change Summary |
| --- | --- | --- |
| `scripts/ui_test_core/product_case_maps.py` | 刷新和发布 | 根据总图 SHA-256 定位刷新索引，继续读取旧内嵌索引 |
| `tests/test_product_case_maps_refresh.py` | 导入稿和刷新 | 覆盖纯 Markdown、兼容迁移、错绑索引及中断保留 |
| `references/case-preparation.md` | Refresh active maps | 说明索引保留及客户端验收 |
| `.github/workflows/check-skills.yml` | Check XMind Markdown and map refresh | 在原有 CI 中执行用例图定向回归 |

## Decision And Alternatives

以当前总图的字节摘要选择索引。更新总图路径前落盘新分图和新索引。旧总图可继续读取自己的索引。相同总图内容只需原子替换对应索引。

## Detailed Change

支持读取旧内嵌索引和无索引旧目录。迁移核对历史分图字节并保留有效文件。错绑索引拒绝刷新。总图根主题和模块结构沿用源数据。

## Impact Analysis

作用于 `export_product_case_maps` 生成及刷新。总图、分图和两条 Human View 仍由同一生效用例集合生成。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
| --- | --- | --- | --- |
| 缺陷回归 | pytest 单例 | 修复前因注释可见条件失败 | `153-map-repair-red.xml` |
| 直接回归 | 与 CI 相同的四个测试文件 | 10 项通过 | `153-map-repair-green.xml` |
| 集成回归 | 上一候选同组 UI-Test 测试文件 | 103 项通过 | `153-map-repair-integrated.xml` |
| 独立运行 | runtime-verify，精确总图文本和发布中断重试 | 两项通过 | `153-map-runtime-verified/result.json` |
| Skill 校验及敏感模式 | `validate_create_skill.py <ui-test> --require-change-records` | 保留基线 6 项 P0 模式发现和 1 项 P1 缺失引用，逐项比对相同 | `153-map-repair-create-skill.json` |

## Safety And Privacy

验证使用任务目录中的合成档案和本地故障注入。

## Risks And Follow-up

Windows XMind 实机查看与点击由用户完成。GitHub CI 可执行性由仓库推送后的工作流运行确认。
