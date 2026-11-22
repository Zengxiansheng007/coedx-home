# Writer v0.3 回归

从仓库根目录运行。单元测试使用 Python 3.10 或更高版本；仓库 CI 使用 Python 3.13。

```shell
python -B -m unittest discover -s tests/jmeter-tps-writer -v
```

以下 Windows 端到端测试需要 JMeter 5.6.3、Java，以及 PATH 中的 jmeter.bat。测试在回环地址启动临时 HTTP 服务，使用虚构会话。verify_167.py 核对请求字节、账号身份、三轮 JTL 与最终 Dashboard。

```powershell
python -B -X utf8 tests/jmeter-tps-writer/verify_167.py
```

verify_162 至 verify_166 分别覆盖原生导入、GUI 编辑、账号与访客混跑、定向诊断、最终报告及重建。线上验收的脱敏记录见[验收证据](../../evidence/jmeter-tps-writer/README.md)。
