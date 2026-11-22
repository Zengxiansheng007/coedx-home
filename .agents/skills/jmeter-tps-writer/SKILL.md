---
name: jmeter-tps-writer
description: Generate an editable Chinese JMeter plan from pasted browser cURL and verify guest or signed-in queries on Windows. Use when a tester wants to check request fidelity, validate account coverage, diagnose business failures or deliver the final native Dashboard.
---

从技能目录运行。将带原标题的浏览器 cURL 存为 UTF-8 文本，保留完整的 Windows cmd 或 Bash 引号和换行。按接口负责人说明标明哪些目标需要登录、哪些允许访客查询。身份要求不清楚时，在发送前集中核实。[输入格式与预检](references/input.md)

需登录时准备一个本机 UTF-8 单列 TSV 文件。表头写 cookie，第一条数据为账号 1，每行一份完整 Cookie。三阶段运行期间保持文件内容、行序稳定。抓包中的会话决定原样阶段的账号，--pilot-account 指定整理后的单账号试跑账号。

```powershell
python scripts/writer.py --requests C:\local\requests.txt --accounts C:\local\accounts.tsv --pilot-account 2 --out C:\local\result-set
```

Windows 需要可运行 JMeter 5.6.3 的 Java 环境。用 --jmeter 指定 jmeter.bat；缺省从 PATH 查找。省略 --out 时输出到当前用户实际桌面的 jmeter 目录。已使用的目录会分配新的运行位置，使用入口打印的路径查看本次结果。

## Validation

1. 通过 JMeter 的 cURL 导入组件建立原样稿，以抓包身份对每个去重目标实发一次。在 result/raw.jtl 核对身份、业务判定和实际次数。原样通过后再整理。
2. 打开 plan.jmx，在 HTTP 请求默认值中调整共用地址，在相应的中文请求下修改查询、正文、请求头或已确认的断言。保存改动后重新验证。单账号试跑只执行需登录的目标，纯访客计划跳过此阶段。
3. 最终轮逐对核对账号与登录目标，另核访客目标各一次。交付实际执行的 plan.jmx、整个 report 目录与 result 中分阶段的 JTL。用 report/index.html 查看最终业务样本，用 report/statistics.json 对照同轮 JTL 的样本数和错误数。正式施压由使用者启动 Runner。

重建 Dashboard 时只读取最终 JTL，指定新的输出目录。

```powershell
python scripts/writer.py --rebuild-report C:\local\result-set\result\full.jtl --out C:\local\rebuilt
```

HTTP 或业务失败、超时、中断时按目标向用户解释阶段、实测、预期和待确认事项。[失败诊断与复验](references/diagnostics.md)

## Safety

原始请求、真实账号、查询令牌文件和私有引擎日志留在本机。仅在指定环境使用可信的本地 JMX，JMX 可执行脚本。核对报告中的业务标题、参数及响应分类后再分享。对明确要求跟随的跳转仅跟随同源地址，跨源时停止并记录失败。
