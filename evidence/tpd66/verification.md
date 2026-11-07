# TPD-01B 验证与范围

基础：integration 76fb002750ad25e61cd7bd69f4e0bcc921742429；独立分支 codex/tpd66-20261107。入口与行为材料在本次冻结提交中。实际 holdout 输入与旧输出保留在开发根 context/ 和 evidence/tpd65-holdout/，未改写。

## 实际执行

1. RED：tests/test-point-discovery/planning-red.md 记录旧入口停止于候选、无法完成绘图确认请求。没有把关键词断言当语义验证。
2. 实现后由实现 Agent 使用该入口约定，读取真实 holdout 规划及其 PRD、说明，完成 tests/test-point-discovery/planning-demo.md 两轮表图材料；第二轮只应用明确标为模拟的顺序调整。此为实现者行为演示，独立行为评审尚待 Root。
3. 原图与调整图均真实运行 archify finalize：validate、deliver、strict check、真实 Chrome browser-check 全部 pass，零诊断。随后各运行 visual-check，四个主题/视口捕获通过。目录：.archify/architecture-planning-20261107-020000/；两个 *.finalize-summary.json 和 visual-check/adjusted-visual 的 *.visual-check.json 为自动回执。
4. 实现 Agent 通过 view_image 实际查看两轮 1440×900 light PNG。主图、箭头、模块名称和三张注记均完整可读；第一轮M1→M3传渠道且平台/日期未知，M2没有虚构连线。第二轮M2明确第一组、M1第二组，接收端范围与全部未知项保留，与表一致。图片是视口截图，完整包含本轮主图及注记；不是 Viewer canonical PNG 导出。未声称检查暗色感知质量。
5. quick_validate.py 首次受系统默认 GBK 解码影响失败；仅该子进程设 PYTHONUTF8=1 后通过。git diff --check 通过。未改全局设置或安装依赖。

## AC 结果

| #66 AC | 已有证据与限制 |
| --- | --- |
| 1 | 技术通过：两轮真实HTML/PNG和回执；方向、传递内容、未知关系与表一致。 |
| 2 | 可用入口和同材料表图展示已交付；真实用户确认/修改尚未收到，保留未满足。模拟调整不冒充真实答复。 |
| 3 | 未确认停门已执行，没有模块澄清或正式测试点；模拟顺序调整后表图一致。真实确认及其准确下一模块记录尚待用户答复，保留未满足。 |
| 4 | 规划能力及图片实际查看完成，无正式测试点或下游评审声明；“已确认的规划”仍等待真实确认。 |

模拟“确认这版规划”分支目前只在行为请求中给出，未把其当作已收到答复。真实答复由Root实际展示后保存来源，再核对适用版本；不能以本记录或开发授权代替业务规划确认。

## 环境失败与边界

首次 finalize 在沙箱内发布硬链接回执时 EPERM，发生在 validate前；经已授权本地命令的 require_escalated 审核后，保持相同 candidate 和命令完成四门。自动事故保存在工作区 .codex/powershell-failures/，不把首次失败重写为通过。另一次只读目录误写 context/holdout，已改读实际存在的 context/holdout-dashboard-*.md，不重复探测环境。

仅执行本地绘图和浏览器捕获；子进程设 ARCHIFY_UPDATE_CHECK_DISABLED=1，无外部模型、安装、远程写入、真实业务、下游修改。无程序化MD直导或P0通过声明。

生成HTML保留Archify模板自身尾部空白，以保持交付hash和回执有效；staged全量diff检查因此报尾部空白，源码/手写材料检查单独通过，不清理历史生成字节。产物目录的 .gitattributes 使用 -text 保持 candidate/HTML/回执的确切字节，避免Windows checkout转换换行使证据hash失效；不改仓库全局换行规则。
