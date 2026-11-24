# UI-Test 用例编写与发布依赖

此目录提供 TCA 依赖的 Source Case v2 编译、构建校验、发布与产品目录聚合入口。公开测试使用合成用例和隔离临时目录。

```text
Source Case + 分支 Test Data
  → compile_case_v2
  → prepare_sync_plan / verify_release
  → render_product_aggregate_v2
```

运行环境依赖见 `requirements.lock`。在此目录运行 `python -B -m pytest -q tests` 核对编译、发布恢复和聚合。
