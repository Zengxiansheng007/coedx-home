# Source semantics before presentation

Read this when interpreting inputs, designing extensions, repairing candidates or
preparing scoped review. The agent authors meaning; renderers project supplied
meaning and never infer missing actions from natural-language data. Structural
checks alone do not establish this review. Keep original inputs unchanged.

## Work from the verification goal

1. State the case's goal and endpoint against its source. Map every necessary
   action, preparation and result to a step or an evidenced initial condition.
   Correct the candidate before generating either view.
2. Bind type selection only to its type data and observable result. Ordinary
   related entry with no independent trigger or intermediate check may form one
   step: name its fields, reference individually named values and make each result
   checkable. Separately locate independent validation, switching, preview and
   submission. Granularity follows evidence, not field or mouse-click counts.
3. A title-empty blur check ends at that check. Include other fields/submission
   only when evidence requires them for this goal; do not inherit the entire
   successful-save template for a negative case.
4. Reference only values actually entered, selected, queried or compared in this
   step. Split a baseline record when consumers differ. Words such as “click” may
   be literal input text; inspect intent and evidence rather than matching verbs.
5. Write required lookup/preparation as an action plus observable result. An
   already-satisfied condition needs a source and checking method. “Search for
   duplicates before execution” is not proof that no duplicate exists. Clarify
   unknown duplicate-found behavior; do not invent deletion or replacement.
6. Resolve the single effective scenario value before binding references. A
   boundary target replaces its field's baseline; retain the override rationale
   without binding two competing values. Preserve title formulas/length limits,
   body-to-title references, date offsets, object bindings and version applicability.
7. Keep execution permits, sequence allocation controls, technical preview rules
   and build metadata as source-traced `technical_handoff` claims on the case.
   Candidate JSON and scoped baselines retain these outside both business views.
   Keep authorized roles, initial state, environment, valid version values and
   required no-record outcomes in business conditions/checks. Relocation never
   removes constraints or grants execution authority.

## Unknown behavior requires an actual question

Read current sources and effective decisions first. A missing trigger, actor or
conflicting rule that changes an action/result remains unresolved: identify the
affected cases and use the existing clarification workflow to ask and await an
actual reply before choosing behavior. For “clear the start time”, explain how
system clearing versus tester clearing changes the concrete steps. Correct known
data ownership meanwhile; retain pending affected cases, do not invent a reply.

## Self-check before presenting either view

- Compare necessary source actions/checks against candidate steps: omissions,
  wrongly attached data, unsupported additions and unresolved business behavior.
- Check every combined step names its fields/values and independently checkable
  outcomes; every independent checkpoint still has a clear location.
- Check one effective target value and all dynamic rules/references; verify
  relocated technical constraints remain locatable after conversion.
- Generate both views from one candidate version through the public entries.
  Compare preparation, action order, data and outcomes against that candidate;
  neither view may invent an action or lose a business rule. Submit concrete
  cases and remaining business questions for user review.

Synthetic example, only when the source establishes title blur as the trigger:

| 操作 | 参数/数据 | 预期结果 |
| --- | --- | --- |
| 选择类型 | 类型：普通通知 | 类型显示为普通通知 |
| 清空标题并移开焦点 | 标题：空 | 显示标题必填提示 |

This does not define a real application's rule. For a separately evidenced save
goal, “填写标题和正文” can reference their named values and check both together;
required duplicate lookup, preview and submission retain separate checkpoints.
This workflow is not a runtime semantic classifier or execution approval.
