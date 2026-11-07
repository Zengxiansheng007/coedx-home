# #76 最终整合：继承已审查的历史字节属性修复

原票冻结f0a26357e6313d9dc04bc3bbcec4b605998fa581已经独立双轴0发现、四项AC通过；报告在开发根evidence/tpd76-{spec,standards}-review.md，当前记录不替代独立审查。原18文件全文、来源、模拟决定与交接均不修改。

合入最新integration 813c7b51da4b8cb78dcdb01c28a72b538cdad66a，得到整合提交64a57749297a44937d62ed5f81a94561bae22277；仅继承tests/test-point-discovery/roles-run/.gitattributes的一行 `v1-before-feedback.md -text`。原#73历史blob、脚本及期望值不变，Root已审查真实core.autocrlf检出probe，见开发根evidence/tpd73-eol-review.md。最新integration已为祖先。

旧工作区检出字节修复的实际过程：

- 合入前后旧检出仍为CRLF，rawSHA 9a86811642f365dc35560202bed801a7428beba9faf6a9fd08c873e9da5938f0，旧角色检查因此失败。verification.md原失败保持；首次git checkout-index -f退出0但现有路径未被重写，原角色断言再次失败。随后字节相等检查也失败，原18blob相等检查已先输出18个均未变。未隐藏这些失败或更换期望值。
- 当时属性查询确为text unset；index debug已有旧stat缓存，表现与跳过旧路径重写一致。已先按绝对LiteralPath将唯一CRLF旧检出保存至开发根evidence/tpd76-role-before-crlf.md（两端均在本开发根内）。其rawSHA仍9a86811642f365dc35560202bed801a7428beba9faf6a9fd08c873e9da5938f0，不作当前产品资产。
- 目标路径不存在后再执行真实 `git checkout-index -f -- tests/test-point-discovery/roles-run/v1-before-feedback.md`，退出0并实际取得原LF rawSHA 658bb64e723f2160474cc2386fc56168961ac5cec64187a35b1dae06434e59c5。HEAD与重检出hash-object同为7f930885a4ab5dda0153abd48ccf39ff431bfc34；仅git add该原路径刷新index状态，没有差异或新blob，工作区clean。
- 重检出后实际运行未改的 `python -B -X utf8 tests/test-point-discovery/check_roles_artifacts.py`退出0，历史身份、普通用户保留、VIP候选、决定、UTF8及引用检查通过。该结果补足原失败，不追溯把before改为通过；不重新证明角色语义/客户端。
- 本轮 `python -B -X utf8 tests/test-point-discovery/check_handoff_artifacts.py`退出0，v3/v4接收hash、D1检查/产品问题、来源/决定与状态一致性不变。原18提交blob相对f0a26357逐一相等；证据目录-text仍保护接收字节。没有重演模拟交互、receiver或客户端。

本次允许新增的整合记录仅此文件。除继承属性与本记录外，相对原冻结无新产品差异；模拟/真实业务、P0、程序直导边界继续保持。最终冻结由Root对未变源与新增属性定向复核后决定集成；此worktree不自行合integration或push。
