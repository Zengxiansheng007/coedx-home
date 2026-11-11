# AT04 实现验证

基线b98d07758a8289f2650295ef85ceff718bdecb4f，task/at04；#103；CR-20261111-004。

先写隔离请求、fixture和独立rubric。Root真实基线第1场正确识别模拟身份、两条范围及v3/d2/build-17，指出完整正文/环境/权限缺失，安全提供复制请求。Root评判正式脚本职责未明确为partial，不记整体RED。实施补专项按需契约；其余分支待冻结后真实验证。

实际运行：C:/DevelopTool/Python311/python.exe -X utf8 -B C:/Users/lenovo/.codex/skills/create-skill/scripts/validate_create_skill.py <at04>/.agents/skills/ask-test --require-change-records。

exit0；P0=0/P1=0/P2=1。已有description的“Use only when”未命中validator惯用措辞，保留手动语义。原输出在实际工具记录。引用检查通过。新增参考、模拟材料和记录人工审查无真实敏感资料、凭据、私有URL或外部调用；无新增脚本，无脚本单测。最终git diff --check另行检查。

本轮只读来源为本机实际TCA正文及p0-evidence-contract、ui-test正文及workflow-contract，已读内容并核SHA256。实现不固定本机来源，运行时仍读取实际适用规则。正式跨Skill报告映射及生产链待联合验证，模拟成功不解除限制。

Root提交冻结后从真实入口逐场实测，保存实际输入、答复、来源、动作和材料前后状态，再独立评审。本记录保持applied候选，不自报行为GREEN。宿主实际调用未验证。

失败保留：functions编码尝试btoa不存在，shell未运行，改PowerShell Convert编码后worktree成功。补分类记录时apply_patch因表格空格上下文不符失败，核实际格式后修正；未改历史证据。无安装、全局修改、模型外发或远端发布。
