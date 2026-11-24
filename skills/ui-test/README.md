# UI-Test 用例编写与发布依赖

此目录提供 TCA 依赖的 Source Case v2 编译、构建校验、发布与产品目录聚合入口。公开测试使用合成用例和隔离临时目录。

```text
Source Case + 分支 Test Data
  → compile_case_v2
  → prepare_sync_plan / verify_release
  → render_product_aggregate_v2
```

运行环境依赖见 `requirements.lock`。在此目录运行 `python -B -m pytest -q tests` 核对编译、发布恢复和聚合。

## 正式 Human View 与 XMind 用例图

TCA 生成正式 Human View 后，编译器根据用例、分支、数据和构建标识校验交接产物。发布通过后，`export_product_case_maps` 读取已激活分支，生成总图 Markdown 和模块分图 Markdown。总图提供模块分图及单例 Human View 的文件入口。使用 XMind 时，由评审者手动导入 Markdown。

刷新索引独立保存，按总图摘要查找。更新前校验已生成的分图，内容未变的模块沿用原文件。
