# 标签测试点接续准确副本 v4

## 【M1 标签维护】

### 【待产品确认】

- Q008，关联原Q003。工作标签名称最多10字、个人最多12字时，普通及复合emoji各如何计数？例如工作名称9个汉字加“😀”是否计10字，个人名称11个汉字加“😀”是否计12字，复合emoji如何计数？第8轮明确emoji仍待产品，沿用第6轮暂留及第7轮已批准的问题身份，第9轮通过本次完整问题与影响。新编号用于上限变化后的受影响问题，原Q003及其答复/批准历史仍在过程永久区。影响工作名称10字与个人名称12字的emoji长度边界、各自超限判断及保存结果。涉及「M1/新建/名称」与「M1/新建/保存」。中英文及特殊符号每个计1继续有效，emoji计数仍未知。

### 新建

- 类别适用工作、个人，以下名称规则共用。
- 【名称】
  - 必填，未填拒绝保存。
  - 名称上限
    - 工作标签最多10字。
    - 个人标签最多12字。
  - 两类中英文及特殊符号每个计1。
  - 超过所属类别上限时拒绝保存并保留输入。
  - 同类别已有相同名称时，保存提示“同类名称已存在”，不创建第二条标签。
  - 工作、个人跨类别允许同名。
  - emoji相关边界与保存预期待明确，见Q008。
- 【用途】
  - 工作标签显示用途字段，个人标签无用途字段。
  - 工作用途必填，空值拒绝保存并保留输入。
- 保存
  - 名称满足已批准的必填和同类不重复规则，中英文/特殊符号按每个计1，工作不超过10字、个人不超过12字，不涉及emoji且工作用途已填时，允许保存，包括已有另一类别同名标签的情况。
  - 成功产生标签ID。
  - 列表显示该ID及已保存名称、类别，重新打开详情核对同一ID及同一名称、类别。
- 取消
  - 取消新建回到列表，不新增记录。

## 【M2 标签筛选】

### 【待产品确认】

无。现有虚构快照的文件事实已读取，真实索引生成及业务执行结果仍未验证。

### 筛选

- 按类别筛选时，返回标签的类别符合所选类别。
- 名称采用精确匹配。按名称筛选时，返回标签名称与输入名称相同，仅包含输入文本的其他名称不作为精确命中。
- 返回标签展示ID、名称、类别，与本次指定来源快照的同一ID记录对应。

### 新建后筛选

- 使用用户手动生成的指定本地索引快照。
- 指定快照成功生成且收录新建标签ID后，按该标签满足的筛选条件，应筛出该ID及已保存名称、类别。

## 资料与Agent交接说明

### 当前身份、版本与实际决定

- 本文件为SIMULATION #88 red接续准确副本，当前版本v4，实际固定路径为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/red/accurate.md`。从只读原文件 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/accurate.md` v3继承完整M1/M2正文及Q008，正文具体检查不变。本轮仅建立授权工作目录内的接续副本并更新身份、可读引用、交接决定和范围，原#87 v3保留其历史准确版本身份。
- 原具体检查的有效评审仍为#87第5/7/9轮对应展示及批准，当前正文适用#87准确v3。v4没有新增业务规则或重新声明具体评审。Q008的问题表述已通过，但emoji计数答案仍未知。
- 本轮实际展示为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/red/round-01-display.md` R01-handoff-v1。交接范围问题Q009的实际答复为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/red/round-02-input.md`，来源为主持第2轮实际模拟答复，原文为“SIMULATION 第2轮实际交接选择。选择先交M1非emoji已明确规则、保存/取消，以及M2带指定快照前提的已明确检查，供后续人员编写完整测试用例。Q008的emoji预期不在本次可执行交接范围，完整问题继续保留；mock事实不是执行证据。此决定仅是文档交接范围，不是业务执行授权。请维护本red目录同一明确身份的准确副本并实际回读，原87文件只读，保留真实可读来源及决定引用。完成后等待后续反馈。”。
- 用户已选择交接M1非emoji已明确规则、保存/取消，以及M2带指定快照前提的已明确检查，限定用途为供后续人员编写完整测试用例。Q008的emoji确定预期在本次可执行交接范围之外，完整问题继续保留。这个选择决定文档范围和用途，未提供emoji答案或业务执行授权。
- 第1轮只是建议并等待，未提前交接。第2轮实际选择后，本接续副本承载已决定的文档交接范围。当前等待后续实际反馈，未变内容继续沿用有效评审。原v1→v2→v3历史及旧问题、替代关系由只读原准确v3和下面的实际来源恢复。

### 本次交接分支、保留分支与依赖

- M1本次交接覆盖两类非emoji名称的必填、工作10/个人12、中英文及特殊符号每个计1、超限拒绝且保留输入、同类重名提示“同类名称已存在”且不创建第二条、跨类允许，以及工作用途显示且必填/空值拒绝保留输入、个人无用途字段。
- M1成功保存须满足正文完整适用条件，保留同一标签ID在列表与重新打开详情中的名称、类别对应及取消回列表无新增。10/12上限是适用条件的一部分，不能据其单独成立得出保存成功。
- M2本次交接覆盖类别筛选、名称精确匹配及结果ID/名称/类别与指定快照同一ID记录对应。名称“周报”与仅包含该文本的“周报总结”区别取自精确匹配规则。类别与名称组合逻辑、空条件/无结果样式、大小写及空白等额外语义没有新增决定，本次没有扩展这些预期。未按新建名称上限推定查询输入长度上限。
- M1新建→M2筛选采用M1非emoji已明确数据。使用用户手动生成的指定本地索引快照，须成功生成且收录新建标签ID，之后按该标签满足的筛选条件应筛出同一ID及已保存名称、类别。后续须核对指定快照、生成成功与目标ID实际收录证据，再验证筛选结果。M1保存成功、现有mock文件或测试点具体批准均不能替代这些事实。
- Q008关联原Q003，完整问题、10/12差异例子、影响和原暂留/批准依据仍保留于M1顶部。普通及复合emoji计数仍待产品，影响两类名称各自长度边界、超限及保存预期，本次不交这些确定预期供执行。其他已明确规则继续保留，未交分支没有删除或永久排除。后续产品答案到达后只重开受影响检查，仍须具体评审后更新本路径。
- 场景纳入与规则明确分别处理。M2条件检查已纳入且规则明确，当前真实索引与收录事实未验证。Q008有明确暂留决定及完整问题，但无计数答案。第2轮只决定交接范围，没有把这两类剩余内容变为已验证结果。
- 名称已知计数和处理共用适用于工作、个人，两类上限分别10/12。用途保留工作显示且必填、个人无字段的真实差异。没有组件共用实现证据，下游须现场核实控件及必要验证。未跨模块提取公共规则。

### 可读资料、规则及具体评审来源

- S1为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/request.md`，标题「SIMULATION 普通入口请求」，无独立版本号。S2为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/input.md`，标题「SIMULATION 标签小工具 PRD v0.1」。P1对应顺序与排除，P2对应名称、用途字段、保存同ID列表详情与取消，P3对应原重名和计数/用途缺口，P4对应M2类别、结果字段与快照来源依赖。
- 第2轮规则原文为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/round-02-input.md`。同类名称不允许重复、提示且不创建第二条，对应M1名称；特殊符号每个计1继续有效，不能延伸为emoji答案。
- 第5轮具体批准为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/round-05-input.md`，批准 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/round-02-review.md` R02-v1的M1已明确名称、保存与取消。第6轮规则原文为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/round-06-input.md`，明确跨类允许、emoji待产品、工作用途必填与空值处理、用途字段适用性、M2精确匹配、指定手动快照成功并收录ID后的可筛出规则，自动/实时及计时排除。
- 第7轮具体批准为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/round-07-input.md`，通过 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/round-06-display.md` R06-v1的M1变化与原Q003产品事项。此前名称/取消继续有效，M2当时尚未批准。
- 第8轮业务变化及材料原文为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/round-08-input.md`，工作上限由12改10，个人12及其他规则有效，emoji仍待产品，并补mock输入。对应当前M1名称、超限/保存联动和Q008的10/12影响。第9轮具体批准为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/round-09-input.md`，明确通过 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/round-08-display.md` R08-v1的M1差异上限、超限、保存联动、Q008完整问题，以及M2类别、精确匹配、同ID字段对应和手动指定快照收录后的筛选条件，合入原准确v3。
- 永久依据为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/process.md`。「永久依据与范围」「复核、评审及恢复位置」D001—D008保存PRD及第2轮答复，「第6轮规则答复、影响与聚焦候选」D009—D014对应跨类、emoji暂留、用途、精确匹配和索引条件；「第7轮具体通过、准确v2与收尾」保存历史具体批准。「第8轮新材料、差异上限与限定重开」D015对应10/12及联动，D016对应mock文件事实，Q008关联原Q003。「第9轮具体通过、准确v3与最终收尾」保存最新具体批准和合入。原问答、选项、建议、真实答复身份及替代历史可由此恢复。
- S3为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/inputs/label-index-mock-v1.json`，已实际读取。identity为“SIMULATION development fixture, not a real index or execution result”，version为mock-index-v1，generation为“manual fixture supplied by the simulated user”。文件三条记录为mock-work-01/工作/周报/purpose例会，mock-personal-02/个人/周报/无purpose字段，mock-work-03/工作/周报总结/purpose归档。版本和ID仅为虚构输入事实，真实生成时间、索引任务成功、新建来源与真实收录均未证明。mock可支持静态资料分析，业务结果尚未验证。
- 本次过程与范围建议历史为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/red/process.md`，原请求为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/red/round-01-input.md`。本轮实际决定原文直接引用本节上方的round-02-input.md，接收者可从本文件与实际引用恢复，不依赖其他聊天、隐藏计划或评审答案。

### 下游用途与进入条件

- 本次为本地SIMULATION文档交接，交接对象是本准确副本及其中可读来源，供后续人员编写完整测试用例。当前阶段不生成完整用例。原排除的批量导入、权限、删除、自动/实时索引更新及计时继续保留。
- 下游自行核对整轮P0范围、实际报告及必要证据，处理缺口、未决和指定快照条件，再由用户手动启动P1/P2。本MD本身不证明P0通过，不授予业务执行、合并或自动启动权限。
- 通用MD直接输入下游程序未验证。未调用或修改test-case-authoring/ui-test，业务系统、真实索引、下游及XMind客户端均未执行或验证。独立接收者仅凭本MD及引用恢复的验证尚未执行。

