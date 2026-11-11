# #75限定验收记录

本票基于1095f59准备；冻结前ff到e291e86，保留流程/生命周期与异步的六类入口及#70共享反馈。恢复本票改动时description发生冲突，已合并六类与XMind触发；未改其他票内容，未安装全局/下游或运行真实业务。

实际输入/输出链位于xmind-run：D1/S1—S5→D2完整具体评审→同一accurate.md v1；聊天清空恢复→D3完整候选/评审→v2；编辑局部MD无匹配为空→D4完整候选/评审→v3；真实XMind回传→D5完整候选→Root实际读全文后模拟具体评审→同一路径v4。答复和过程见conversation.md；v1/v2/v3快照只是历史证据，当前只有accurate.md准确。模拟答复不代表真实业务确认。

真实客户端由Root操作，版本26.4.1327.202606142039。外部开发证据根为C:/Users/lenovo/Documents/ChatGPT/ui-test/.scratch/tpd-development-20261107/evidence：tpd68-client保存逐字节import-source.md和原生原件；tpd75-client保存实际观察、另存后的真实编辑回传及UI后补充校验。原生hash与支持范围见accurate.md v4及original-native-read.json/returned-native-read.json；新reader实际读取两份41主题，中文、条件、问题和说明区保留，只有预期文字与层级两处变化。合成ZIP只证明解析，不替代该往返。

candidate-receipt.json记录D5展示时准确v3前后同hash4e4fc9...，D5原字节hash804c67...保留。Root随后明确具体评审才更新v4。告警全文、档案三项及历史评审、U1/P1均保留；原生旧D1说明未覆盖准确版本。D5局部历史链接按展示时worktree解析，checker在集成目录从开发证据根定位同一输入；v4外部证据采用本机绝对位置，业务fixture/请求/答复仍为同文可定位相对链接。未承诺跨机器可移植开发证据。

xmind-run/.gitattributes固定本轮已绑定hash的过程证据原始字节（Python在本机实际保存CRLF），避免core.autocrlf改变候选/历史快照；仅此目录指定cr-at-eol识别，保留普通尾随空格检查，不修改仓库或全局Git设置。首次加入-byte-preserving属性后的cached检查把CR判为尾随空白，按原始CRLF证据补该属性再检查，未改写历史字节。

已实际执行并退出0：
- python -X utf8 -B tests/test-point-discovery/test_xmind_reader.py（3项；先缺reader红，再通过；格式行为不判业务语义）。
- python -X utf8 -B tests/test-point-discovery/check_xmind_outputs.py（同MD、v3候选门、保留、文字/层级、引用/UTF8）。
- python -X utf8 -B C:/Users/lenovo/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/test-point-discovery（Skill is valid）。
- git diff --check与cached --check（无输出、exit0）。

未知/歧义删除与无法定位反馈按实际模拟提问保留，未答不改；原生未支持格式返回pending。仅保证单content.json单sheet文本attached树和已验证客户端范围；笔记/自由主题等需核实，不承诺任意版本。helper只有格式读取和来源身份，语义仍由Agent决定。下游交接/完整用例/P0/业务执行未开展。

本地执行的一次过长内联命令在runner启动前失败，没有更新文档；改为开发证据目录内短路径脚本后完成，PS失败记录PS-INC-20261107-003。stash恢复的description冲突已解决；预留stash 4553e189a02a3e6c59f30ae9f993089c868ee327保留给Root清理，无额外产品更改。未推送或合入integration。
