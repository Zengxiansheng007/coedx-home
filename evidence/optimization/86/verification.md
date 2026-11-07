# #86 定向验证

## 实现冻结前

- `skill-format.log` 为现有 tools/verification/skill_format.py 对本票 Skill 的实际输出，退出0，格式有效。
- `reader-tests.log` 为既有 test_xmind_reader.py 实际运行，3/3通过，退出0。仅合成归档格式读取，不证明客户端或语义。
- `historical-feedback.log` 为既有 check_feedback_outputs.py，退出0。保留其历史用途，不当新反馈语义通过。
- `historical-xmind.log` 为既有 check_xmind_outputs.py，退出1，StopIteration位于旧拥有根查找 `context/issues/75.md`，隔离工作树祖先没有该旧上下文。此前固定hash及内容断言已执行，完整脚本仍报告未通过，不改变其根定位、断言或旧产物以造通过。治理事件PS-INC-20261107-015已自动留存。
- 定向扫描 Skill全部参考与活跃request/rubric，原整分支重印命令已在相关入口同步。扫描只辅助静态核对，未当业务语义验证。
- git diff --check退出0。修改集中在6份产品Markdown与4份活跃验收材料。新增本票fixture/request/rubric及证据。reader及旧保真脚本未改。
- 运行使用既有C:/DevelopTool/Python311/python.exe，核对Machine PATH与C:/DevelopTool，没有安装依赖。

RED及GREEN由Root主持的逐轮模拟另列，尚未把静态或解析成功认作三入口行为通过。真实XMind客户端往返本票未执行，最终#88同版流程另证。
