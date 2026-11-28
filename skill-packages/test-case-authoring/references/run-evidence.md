# 按本次证据编写和核对判据

从同版完整单例逐步读取操作、输入、预期、独立验证及终点。给每项断言写明执行者在哪次调用后、到哪里、用什么标识、读取哪个实际对象，以及什么结果构成业务违例。环境地址可在仍有效时沿用；每例实跑都取新的运行标识。先保存本次实际输入和页面输出，再独立核对本例要求的后台观察。引用 P0 的评审状态、上次截图或调用参数只能提供背景。

若用例要求核对上传透传字段，从本例输入和接收端判据读出字段名、精确字面值和位置。把“用本例编号和本次 RUN_ID 定位请求”的方法写入公共说明，把“查同一文件所在 multipart 请求体的独立表单字段”或“查该条 HTTP 请求的实际头”写进具体用例，同时写出本例字段名和预期值。HTTP 头名忽略大小写，表单键名和值按原文核对。预期非空字符串时，完整集合中字段缺失、值为 null 或不相等都属于业务失败。请求体、客户端配置与响应中出现同名键，不能补作实收请求头证据。

执行时保留每步观测原文或脱敏证据位置、实际标识、期望与结论。接收记录无法打开、匹配多条且无法确定本条、缺关联信息或只看得到部分字段时，记录具体缺口，将受影响的断言标“待取证”。继续完成可独立执行的步骤。已有明确违例时整例失败，同时保留其它待取证项；所有适用断言已有当次通过证据才判整例通过，其余整例待取证。

## 核对已读取的本次观测

`scripts/run_evidence.py` 是本地纯函数，不连接接收器。对于采用 `用例编号-RUN_ID` 关联请求、且需要核实某个字符串字面值的完整用例，可调用：

```python
from run_evidence import check_received_field, summarize_case

field_result = check_received_field(case["id"], run_id, record, collection, field_name, expected_value)
observations[step["id"]][step["expected"][0]["text"]] = field_result
report = summarize_case(case, run_id, observations)
```

从本次原始记录读出 correlation 和 source_ref（可回看的原始证据位置）。仅当已确认找到同一条请求且相应完整集合可读时，传入其 headers 或 form 字典；完整空集合传 {}，未能读取时省去集合。form 必须取自与本次目标文件相同的请求体。不能把预期标识写成实收标识。记录不可定位时传 None。相同头名出现多个实收值应保留所有值，不能只取第一个值。

整例汇总仅接受同版已展开的 case。执行者核对每个适用的前置、业务和后置步骤；将本例每条 expected 和 verification 的原文分别作为该步 observations 的键，相同原文只记一次，无显式预期的操作记录完成情况。每项通过或失败包含 status、correlation、source_ref 和实际观测；待取证另附 gap。当页成功、文件非空、哈希一致是三个不同断言时，分别留存本次证据。先保存执行原始记录，再做汇总。使用其它关联机制的业务仍按本节前述原则核实实际记录。

通过或失败的每项记录都须有非空白 source_ref 和一个实收字段（observed 或 observed_values）。实际读到的 null、false、空数组均保留原值。省略这两个实收字段时，该项待取证。

依赖用例每调用一次，都要另取该次的前置、步骤、终点和后置观测。先用空 observations 调用汇总，返回的每项 step_path 标明调用位置。将对应原文和观测放入 scoped_observations，例如 `scoped_observations["/steps/call-2/steps/end"]["订单已保存"] = row`，再调用 `summarize_case(case, run_id, observations, scoped_observations=scoped_observations)`。各层按分组名和步骤编号定位，编号中的 ~ 和 / 分别转为 ~0 和 ~1。独立用例根层的唯一步骤编号仍可直接作为 observations 的键；其它位置使用 step_path。每次调用只使用与该位置相符的本次证据。
