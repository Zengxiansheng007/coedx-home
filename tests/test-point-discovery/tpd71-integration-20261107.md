# #71 合入 #70 后的冻结说明

本轮仅整合入口。旧冻结：0ccbaabe0f10662350ef442c5f1783cb6d229d7f；合入分支codex/test-point-discovery-20261107，准确incoming HEAD：91de44a8f968c9b011366a70a2214fbdf96fb789。使用git merge --no-commit --no-ff，未reset/rebase，保留两父提交及旧证据。新冻结为包含本说明的merge提交；最终实际hash另回传Root，避免在自身提交内伪造自引用hash。

Root通知旧#71两轴独立审查0发现、4AC在限定模拟中通过；该结论仅沿用原样例范围，原验证/案例/引用文件未改写。这不是新行为整轮验收。

## 本轮写集与冲突处理

- skills/test-point-discovery/SKILL.md：仅description产生冲突，合并聊天/Markdown触发与看板、信息维护、计算三种已交付范围；其余采用Git自动合入。保留#71步骤1非看板不再停止、步骤2两类参考路由与步骤3混合裁剪，保留#70步骤10反馈重审及其完成检查。未声称全部七类完成。
- 原样引入#70产品参考：references/feedback-review.md；references/review-and-progress.md与writing-review.md的反馈跳转。没有修改其定义。
- 原样引入#70测试/证据：check_feedback_outputs.py、feedback-red.md、feedback-request.md、feedback-rubric.md、feedback-validation.md及feedback-run/六文件。
- 新增本说明。agents/openai.yaml保留#71三类简介和原通用default_prompt，不回滚为仅看板。
- #71五份方法/组织参考、yaml与原测试/案例共17文件，与旧冻结Git blob逐一相同；#70除共享入口之外14文件，与incoming逐一相同。未重新生成案例、改旧证据或运行客户端。

## 实际入口定向核对

已实际回读合并后的SKILL及feedback-review、review-and-progress、writing-review。

1. 新信息维护PRD：步骤1接受已交付类别，步骤2→information-maintenance，步骤3仅实际操作/补充条件；未知字段或边界先澄清；新规划仍步骤5调用archify并等待表图确认，不跳过门。
2. 费用计算PRD：步骤2→rule-calculation→按需三方法，步骤3选条件主线；步骤8写具体点，步骤9具体评审后同一准确MD更新，叠加未知不确定结果。#71原已确认规划接续假设保持其模拟边界。
3. 对已评审部门/费用收到聊天/局部MD反馈：入口步骤10直接→feedback-review，不重复规划。已有准确文件、原副本/范围和反馈先固定；歧义删除先问，范围外完整保留；完整受影响分支重审后才回步骤9更新。#71未知历史名称问题不会因收到反馈自动清除。
4. 普通当前草稿评审：步骤9→review-and-progress，具体通过才更新；涉及影响再读feedback-review。#70写点和评审参考的新增跳转保持可达，没有旧“该能力未实现”停止语句残留在这两参考。

这是变更入口的定向语义路由核对，不冒充新的完整模拟、真实业务、XMind或下游验证。

## 定向检查与复用依据

- Git blob身份逐一核对：旧#71除SKILL的17文件不变，有序“路径 空格 blob”清单SHA256为264590ad71fadd56f786c0e3e10a2d6d0bbb8d774a076efbde134dd821ccb41b；incoming #70除SKILL的14文件不变，清单SHA256为e035b10a1f24a1dd7f3f6d4739bde238573d49126841e0e000002bd0220962b4。旧父共同基线63738af用于选出各票写集，按git diff --name-only顺序计算；blob经git hash-object --path过滤核对，避免CRLF影响。
- UTF8 quick_validate：Skill is valid，exit0。
- 仅运行check-maintenance-calculation.py的ArtifactChecks.test_skill_local_references_resolve：1 check，OK，exit0，覆盖新共享入口及参考的本地链接；未重跑全部样例或客户端。
- 入口diff逐行回读，git diff --check无空白错误。冲突resolved后提交前再核无未合并路径、cached diff --check。

旧模拟行为适用：五份#71组织/方法参考及全部样例字节身份保持，原4AC结论复用；#70引用和反馈案例同incoming来源保持。只对新增共享路由作本次核对，Root将独立复核入口差异再决定集成。保持旧限制：不证明新规划archify流程、真实XMind、真实用户业务确认、下游或P0执行。未全局安装、调用外部模型、运行真实业务或push，也未合并进integration；本轮不处理#74。
