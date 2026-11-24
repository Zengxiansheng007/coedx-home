# CR-20261117-116 - coverage 准确父源上下文

| Field | Value |
|---|---|
| Status | applied |
| Target Skill | test-case-authoring |
| Change Type | fixed |
| Scope | scripts-and-validation / references-and-assets |
| Source | fresh 生成发现的 coverage 失配及独立公开 API/QA 回放实证 |
| Baseline | 425c5f2536627d5964401cdd69b5eeb75932058b；tree b3cc483951671fe29e5dff6816fa3dea0ef128a9 |
| Author | Codex |
| Related Records | CR-20261117-113, CR-20261117-115 |

## Summary

render_extension 的正文与对话已传准确父源，但 _coverage 独立 preflight 丢失 source_catalog。
同一实际 QA 回放候选 LOW/HIGH ready、无 blockers，coverage 却虚报公共操作适用范围待核。
本次只贯通准确上下文，保持 LOW 的 display 未知与真实权限 GAP，不改变候选、资格、标志或父源。

## Context And Problem

本轮先读 CONTEXT、plan、REQ/AC矩阵、原 stage-delivery REQ-016/017、AC-019/020/021/034、
common-operations 完整生成要求、RTA02 QA/aggregation/scoped/restoration 公开契约与真实失败证据。
通过现有 prepared/opening_payload、start_record/advance_record/read_record 实证，既有来源不改。
复用标准库与原 preflight/QA/反馈恢复；无需新依赖、SDK或外部平台事实，未调用网络或模型。

## Sections Changed

| File | Section | Change Summary |
|---|---|---|
| scripts/extension.py | _coverage/render_extension/build_extension | 同一调用方准确完整父源传给 coverage 与初次渲染 |
| scripts/test_authoring_preparation_scope.py | 公开渲染与范围故障 | 准确/缺失/漂移/局部来源及非法 coverage 链接 |
| scripts/test_projection_full_lifecycle.py | 实际同一 QA 串联 | 生成评审→真实文件反馈复评→checkpoint/resume→新进程后覆盖同义 |
| references/extension-contract.md | Same-version review | 明确重生成准确父源与 partial/gap 保留 |
| change-records 与 .agents 镜像 | 可追溯交付 | 同字节同步本次准确写集 |

## Decision And Alternatives

仅传递现有 source_catalog 参数；不缓存父源、不新增独立状态、流程或 schema。
不以强制 complete、改变 coverage 链接、改 sourceCatalog 或绕过 preflight 解决表现。
build_extension 已拥有经过 P0 资格核对的 catalog，首次渲染同步使用它，核实活动整步引用。
检索全部 _coverage 消费者，仅 render_extension；QA/反馈/恢复已有准确父源参数，无需改业务状态机。

## Detailed Change

coverage 与正文及对话基于同一个准确完整父源恢复动作、数据、预期和断言。
未变 QA、候选及父源原字节保持；无法还原者仍不计覆盖。LOW save 覆盖/display未知为 partial，
HIGH save 为 complete，权限未知 GAP 保持 gap。缺失/漂移父源为局部 blockers，非法链接仍拒绝。

## Impact Analysis

影响 P1/P2 公开渲染与初次 build_extension 返回结果。已有 QA 事件、反馈和恢复不添加新动作；
测试验证当前回放后再次调用公开渲染一致。原 P0、旧 trial、新业务 candidate/QA、Root plan 均未修改。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| 独立实证 | prepared + actual QA replay + preflight/render_extension | ready LOW/HIGH 无阻塞，但原 coverage 三项 gap | run/evidence/rta06-coverage-context/reproduction.json |
| 行为 RED | unittest QA lifecycle 与 authoring scope | 精确期待 partial/complete/gap，原源码却 gap/gap/gap | red-exact-baseline.log |
| 受影响 GREEN | 九模块 unittest | 最终结果见本轮外部验证记录 | green-targeted-final.log |
| 结构/记录/敏感扫描 | create-skill --require-change-records | 保留原负例，不修改扫描器；最终结果见扫描证据 | create-skill.json |
| 镜像/语法/写集 | 同字节、AST、git diff --check | 最终结果见 package-checks.json | package-checks.json |

首次测试因 governed runner 的 cwd 造成 import 失败，保留 red-harness.log 后修正显式工作目录，
恢复原生产字节再运行有效行为 RED；首次断言误将 LOW 当 complete，按原手工基线纠正为 partial。
所有原失败保留，不冒称其为产品回归。执行次数交 Root 累计，不建立第二账本；不重复无变化404整仓。

## Safety And Privacy

材料和答复明确合成。未执行 UI、模型、网络、全局安装、业务测试或发布；没有依赖安装。
保留原未知、资格与局部拒绝。仅隔离 worktree 和外部本轮 evidence 写入。

## Risks And Follow-up

applied candidate；Root 冻结后执行独立整票两轴复核与必要集成验证。
真实 fresh 生成与业务稿语义评审由 Root 推进，不能以本轮公开测试替代。XMind 客户端仍未验证。

Refs: REQ-016/017；AC-019/020/021/034；FULL-GEN-01；本轮 plan/CONTEXT/req-ac-matrix 与 RTA02 契约。
## Decision And Alternatives

不改变 sourceCatalog、scope 标志、适用批准或原手工 coverage 链接来制造通过。
_coverage 唯一消费者为 render_extension；build_extension 已有 catalog，直接传入。
QA/反馈/恢复保留既有 source_catalog 公开载荷与 source_catalog_path，无需新事件或 schema。

## Detailed Change

四处源码改动只传准确上下文，不改变 preflight、coverage 链接校验或资格门。
同一 QA 生命周期串联首次归属/评审、实际文件反馈和局部复评、checkpoint 与新进程恢复；
阶段均断言 LOW partial、HIGH complete、真实 GAP gap，其他用例/数据/批准仍保持原有断言。
缺失/漂移父源继续 gap；仅 LOW 归属漂移时 HIGH 保持 complete；未知用例和非法方面链接继续拒绝。

## Impact Analysis

canonical 与 .agents 分发镜像同步，仅扩展生成/重生成及其直接文档与测试。
没有改旧 trial、Root plan、QA/candidate、全局 Skill 或原 P0，没有网络/UI/模型/发布。
本次公开接口证据不代替实际 fresh 全流程、业务语义或 XMind 客户端验收。

## Validation Evidence

| Check | Command or Method | Result | Evidence |
|---|---|---|---|
| 独立原始实证 | prepared/opening_payload → 实际 QA 写入/回读 → preflight/render_extension | 同 batch 两例 ready，无 blockers，但 coverage 全 gap | reproduction.json、repro-qa.md |
| TDD RED | 原 425 源码 + 新 QA/范围公开断言 | LOW/HIGH 均虚报 gap；真实 GAP 保留 | red-exact-baseline.log |
| 当前定向公开回归 | unittest 九模块 | 50/50 通过，29.663s；包含新增负例及新进程 coverage | green-final-workspace-temp.log |
| 结构/变更记录/敏感扫描 | create-skill --require-change-records；对比CR115 | exit1，继承P0=3/P1=0/P2=0，rule/file完全一致，无新增 | create-skill.json、package-checks.json |
| 镜像/语法/写集 | 同字节、AST、git diff --check | 两包各176文件同字节、87 Python语法通过、diff检查通过 | package-checks.json |
| 最后两模块复核 | QA完整串联与新作者范围 | 4/4通过；移除冗余import后逻辑不变 | final-assertions.log |
| 原 QA 只读修复实证 | 同一历史 repro-qa.md 回放与准确父源重生成 | LOW partial、HIGH complete、GAP gap；QA SHA256不变 | public-fixed.json |
| 结构/记录/敏感扫描 | create-skill --require-change-records | P0=3/P1=0/P2=0；三个既有合成 secret-pattern 负例不改，无新增 | create-skill.json、package-checks.json |
| 镜像/语法/差异 | 字节对照、AST、git diff --check | 最终冻结前实际核对，结果见证据 | package-checks.json |

所有证据位于外部 run/evidence/rta06-coverage-context，次数交 Root 累计，不另立执行账本。
首个红启动器未设置工作目录导致 import 错误，原失败另存 red-harness.log；恢复原生产字节后取得真正行为红。
随后一个过强 complete 期望按原手工基线纠正为 partial，原失败保留，不改变生产 coverage 逻辑。
默认 sandbox Temp 的 WinError5 导致一次受影响回归失败，保留 targeted-default-temp-failure.log；
仅本次测试把 TEMP/TMP 设为授权工作目录后全部通过，未改全局环境、文件权限或生产源码。
一次并行测试临时目录使镜像清单瞬时不同，原失败保存 package-checks-transient-inventory-failure.log；
等待测试结束后对静止包重核176文件全部同字节通过，不调整包内容或忽略真实文件。

## Safety And Privacy

模拟问题/答复及用例均显式合成；既有运行时 C:/DevelopTool/Python311 复用，无安装/环境创建。
来源与候选保持单一权威；源码冻结交 Root merger 和两轴独立审查，不自授宿主 accepted。

## Risks And Follow-up

applied candidate，等待 Root 准确提交整票审查与后续实际 fresh 生成。
XMind 客户端、具体业务稿评审与真实业务执行未在本票运行；三个既有扫描负例不升级为扫描全绿。
建议合入后只跑上述九模块和包结构/镜像/差异检查；此前已通过的未受影响 404 全仓证据复用。

Refs: 本轮 CONTEXT/plan/req-ac-matrix；REQ-016/017、AC-019/020/021/034、FULL-GEN-01；RTA02 公开父源契约。
