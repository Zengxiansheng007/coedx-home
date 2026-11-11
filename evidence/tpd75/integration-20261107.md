# #75与七类共享入口整合

原冻结：ac7359f43f0fb1cfd542aa7d57260030bd2efcb6。本次在原worktree合并最新integration 069f75668d7c82494e36cf538d01c9ff04420293，未合入integration、未推送。Root授权仅必要共享入口与本整合记录，不重演客户端/交互。

SKILL.md的description和当前能力段发生冲突，按七类组织及聊天/MD/XMind反馈并集解决：保留角色权益入口、默认模块→用户类型→功能规则、流程/生命周期、异步及已有看板/维护/计算路由；XMind步骤11回同一候选/具体评审/准确MD更新。接收#73移除的旧组织未交付表述，并将步骤6残留的“其他未交付组织方案”改为按实际证据报告范围。此时仅下游交接#76尚待，参考接通仍不代表全部规格验收通过。

本次自主写集只有skills/test-point-discovery/SKILL.md及本记录；#73文件按integration原样纳入。原#75其他22个已冻结文件（reader、反馈参考、测试与全部XMind证据等）逐一用git show对比索引blob，完全相同；另以git diff ac7359f检查这些路径无差异。准确v4 SHA256仍为77036c70215df1b75628aec5ff8c60eb25e88dee1f03a3eb965752742a395405，原生绑定及历史候选hash未变。

实际定向检查均退出0：

- python -X utf8 -B tests/test-point-discovery/check_xmind_outputs.py：v3候选门、同MD v4、告警/档案保留、文字层级、引用和UTF8通过。
- python -X utf8 -B C:/Users/lenovo/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/test-point-discovery：Skill is valid。
- 独立读取当前入口并检查七类参考路径、三入口触发、旧阶段表述不回退、无冲突标记/替换字符、全部入口链接可达；逐文件git blob对比及v4 SHA256通过。
- git diff --check及git diff --cached --check无输出、退出0。

不重复无变化的reader测试、原生解析、客户端编辑或模拟交互；既有证据保持原身份。没有修改下游/全局配置、调用外部模型或运行真实业务。Root后续做共同入口定向复核及merger，不由本记录替代独立验收。
