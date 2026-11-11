# 标签测试点准确文件 v5

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

- 身份为SIMULATION模拟开发验证准确测试点，当前文档版本v5。88第2轮记录文档交接范围，第3轮补充两个名称输入框的转述技术观察与下游核实职责。具体检查继续适用原87准确v3及其有效评审，交接范围沿用88第2轮实际选择。保留原87第5/7轮有效批准的M1内容，原87第9轮合入R08-v1通过的M1工作10/个人12及超限/保存联动、Q008完整产品问题和M2类别、精确匹配、同ID字段对应及手动指定快照收录后的筛选条件。emoji计数仍待产品，真实业务未执行或验证。
- 本接续文件为本轮唯一准确路径 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/green/accurate.md`，业务规则适用v3。只读来源为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/accurate.md` v3。原87第5轮首次创建v1，第7轮原路径更新v2，第9轮原路径更新v3并首次纳入M2。这些历史更新均发生在原87路径。
- 历史具体展示源为原87过程目录 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/` 中的 `round-02-review.md` R02-v1，实际评审原文为原87过程目录 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/` 中的 `round-05-input.md`，来源为主持第5轮实际模拟答复，仅批准当时M1已明确名称、保存与取消。第7轮实际评审原文为原87过程目录 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/` 中的 `round-07-input.md`，通过原87过程目录 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/` 中的 `round-06-display.md` R06-v1的M1变化及Q003产品事项，并明确此前名称和取消继续有效。业务答疑与具体评审分别保留，第6轮规则答复原文为原87过程目录 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/` 中的 `round-06-input.md`。
- 当前具体展示源为原87过程目录 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/` 中的 `round-08-display.md` R08-v1，实际评审原文为原87过程目录 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/` 中的 `round-09-input.md`，来源为主持第9轮实际模拟答复。原文明确“通过其中M1差异上限、超限、保存联动及Q008完整产品问题，通过其中M2类别、精确匹配、同ID字段对应和手动指定快照收录后的筛选条件”。第8轮业务答复原87过程目录 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/` 中的 `round-08-input.md`，只提供规则和材料，具体通过来自第9轮。
- v1→v2历史替代范围为原保存分支对跨类同名的排除条件，以及说明区跨类/用途仍未答的当时状态。跨类允许、用途空值拒绝且保留输入已有第6轮答复与第7轮具体评审。原Q003从未答经第6轮明确暂留、第7轮通过具体呈现，在v2中按当时共同12字上限保存，其计数预期仍未知。
- 本次v2→v3仅将原工作上限12改10、超限和保存按工作10/个人12分别判断、产品事项由Q003关联为Q008并更新10/12影响。个人12字、名称必填、已知计数、重复规则、用途差异/空值处理、同一ID列表详情结果及取消继续沿用有效规则和评审。Q003原历史可从永久过程回读，当前事项位于M1顶部Q008。
- S1实际路径为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/request.md`，标题「SIMULATION 普通入口请求」，无独立版本号。S2实际路径为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/input.md`，标题「SIMULATION 标签小工具 PRD v0.1」。P1对应顺序与排除，P2名称对应「M1/新建/名称」，类别/用途字段差异对应「M1/新建/用途」，保存结果对应「M1/新建/保存」，取消对应「M1/新建/取消」。P3重名与计数疑点由第2、6轮答复分别明确，emoji剩余问题按实际决定暂留。P4及第6轮答复对应「M2/筛选」「M2/新建后筛选」，指定快照资料由S3补充为限定模拟文件事实。
- S3实际路径为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/inputs/label-index-mock-v1.json`，第8轮补交并已实际读取，第9轮复核。identity为“SIMULATION development fixture, not a real index or execution result”，version为mock-index-v1，generation为“manual fixture supplied by the simulated user”。三条文件记录为mock-work-01/工作/周报/用途例会、mock-personal-02/个人/周报/无purpose字段、mock-work-03/工作/周报总结/用途归档。版本和ID仅为虚构输入文件事实，真实生成时间、索引任务成功、新建来源和真实收录均未证明。第9轮明确快照是模拟资料输入。
- 永久过程实际路径为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/process.md`。「永久依据与范围」及「复核、评审及恢复位置」D001—D008保留原资料与第2轮答复，「第6轮规则答复、影响与聚焦候选」D009/D010/D011分别对应跨类允许、完整emoji产品问题与影响、工作用途规则，D012—D014对应M2依据。「第7轮具体通过、准确v2与收尾」保存该轮实际评审与更新范围。原问题、选项、推荐、假设、实际答复与历史均在该文件永久区恢复。历史临时覆盖由同一过程文件维护，当前收尾进度见其第9轮永久记录。
- 同一永久过程「第8轮新材料、差异上限与限定重开」D015对应10/12名称上限及超限/保存影响，D016对应S3实际文件事实，Q008对应当前完整emoji问题。「第9轮具体通过、准确v3与最终收尾」保存当前评审与合入映射及收尾进度。过程文件承载永久证据和本轮收尾状态，准确测试点身份仅属于本文件。
- 本次覆盖复核已核对P2—P4、第2/6/8轮规则答复及第5/7/9轮具体评审和S3文件事实。M1名称、用途、保存、取消及M2类别、精确匹配、同ID字段对应和手动快照收录后的筛选条件均有现行规则及对应具体通过。emoji问题完整且有实际暂留决定，计数预期仍未知，相关保存仅覆盖非emoji已明确分支。
- 名称已知规则适用工作、个人两类，共用表达基于相同业务要求。用途保留工作显示且必填、个人无字段的真实差异。没有组件共用实现证据，下游仍须结合现场控件确定必要验证。未跨模块提取公共规则。
- M2原R05-v1/R06-v1在第5—8轮未获具体通过，当前按第9轮对R08-v1的实际批准纳入上述正文。D012—D014业务规则继续有效。S3可支持模拟数据字段对应的来源说明，真实索引生成及业务筛选未执行或验证。没有把mock记录视作本轮实际新建结果，也没有从保存成功推断自动/实时收录。未按新建名称上限推定查询输入长度上限。
- 本轮批准范围以R08-v1具体规则及第9轮原文为限。类别与名称组合逻辑、空条件/无结果样式及大小写/空白等额外匹配语义没有额外规则决定，未据常识扩展。模拟资料推导的示例保留在R08-v1与永久过程，仍为静态候选分析，无运行结果身份。
- 第6轮限定本轮索引检查为用户手动生成，自动/实时更新及计时继续排除。当前完成的是本地SIMULATION已选择范围的测试点具体评审、同文件更新与相应记录收尾，emoji继续待产品，业务运行与真实收录证据仍未验证。
- 批量导入、权限、删除、在本Skill生成完整测试用例沿用排除。原87结束时尚未文档交接，88第2轮的现行文档交接决定见下文。下游仍负责完整用例、P0条件核对与人工启动，业务系统、下游、XMind客户端未执行或验证。

### 88第1轮接续身份与建议历史

- 本文件依据主持本轮实际请求建立接续副本。原87准确v3及其所有引用只读，当前业务正文、有效具体评审、Q008及排除保持原来源身份。复制仅转移本轮可写准确路径，业务版本仍v3，不构成新的具体评审或交接决定。后续本轮更新仅在本路径进行。
- 原87的“本轮”“第N轮”均指87原历史轮次。历史相对引用以原87过程目录 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/87/evidence/optimization/87/green/` 为基准，S1/S2/S3及永久过程保留原可读绝对路径，未迁移历史过程文件。
- 本轮输入 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/green/round-01-input.md` 请求先建议、下一轮答复决定范围。当前建议展示 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/green/round-01-display.md`，版本H88-R01-v1。实际交接选择尚未回复，尚未交接，当前全部测试点与Q008仍保留。
- 本轮过程为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/green/process.md`，只承载88接续过程与实际答复，原87永久过程仍为历史来源。建议纳入M1非emoji明确检查、M2类别/精确匹配/同ID字段检查和带指定手动快照成功及收录ID前提的新建后筛选规则，Q008保持待产品。此处仅记录建议，最终交接范围等待实际选择。

### 88第2轮现行文档交接决定

- 现行唯一准确路径仍为本文件。文档v3→v4只记录本轮实际交接选择、用途、保留范围与下游边界，业务正文、Q008完整问题及其原具体评审适用范围继续沿用原87准确v3。上节第1轮尚未交接状态保留为历史。
- 实际决定来源为主持第2轮实际模拟答复，原文可读引用为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/green/round-02-input.md`。决定针对 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/green/round-01-display.md` H88-R01-v1的A选项。关键原文为“按A先交M1非emoji已明确规则、保存与取消，及M2基础筛选和带完整指定快照前提的新建后筛选，供后续人员编写完整用例。emoji确定预期不在本次可执行交接范围，完整Q008和影响继续保留。mock仅资料输入事实，真实执行前提仍需核实。本次只是文档交接范围，无业务或下游执行。”
- 已选择的文档交接分支为M1非emoji名称必填、中英文与特殊符号计1、工作10/个人12差异上限及超限拒绝保留输入、同类重名拒绝与提示、跨类允许、工作用途字段必填及空值拒绝保留、个人无用途字段、满足上述必要条件的保存及同一ID列表/详情结果、取消回列表且无新增。名称共用规则及类别上限/用途真实差异均保留，供下游分别恢复工作与个人完整适用检查。
- 同时交接M2类别筛选、名称精确匹配和返回ID/名称/类别对应指定来源快照同一ID的基础检查，以及M1新建后筛选的完整条件链。先保存产生标签ID，再由用户手动生成指定本地快照，只有该快照成功且收录同一新建ID，按该标签满足的筛选条件才要求返回该ID及已保存名称、类别。该分支的场景纳入、已明确规则与实际前提是否成立分别保留。
- 本次用途是文档交接给后续人员编写完整用例。M1非emoji分支可按已明确规则编写，M2及联动按指定来源、手动快照成功和同一ID收录等完整前提编写。真实生成成功、真实新建来源、同一ID收录及现场筛选结果目前仍未验证。S3 `mock-index-v1`及其三个ID仅为模拟资料输入事实，不能用其替代这些真实执行前提或把保存成功推为自动/实时可筛出。
- Q008完整问题及其10/12差异影响继续保留在M1顶部及名称短引用。emoji确定计数、长度边界、超限及相应保存预期未交作本次可执行检查，等待产品后续口径。该部分仍属原测试点保留内容，未交不构成删除或永久排除。明确口径后返回受影响具体检查的澄清与评审。
- 本轮没有新增类别与名称组合、空条件/无结果样式、大小写/空白等额外匹配语义。批量导入、权限、删除、自动/实时更新及计时沿用原范围。完整用例由下游编写，本Skill本轮交接不生成完整用例。
- 下游按实际控件核实定位、独立控件映射与必要技术验证。两类名称当前没有共用组件实现证据。纯技术定位或控件拆分反馈保存实际对象、反馈来源与证据状态，沿用已有业务规则、评审和交接范围。业务规则、范围或预期变化返回来源核对、必要澄清及受影响具体测试点重审，现场表现只承载观察身份。
- 下游自行核对整轮P0范围、实际报告、必要证据、缺口与未决，随后P1/P2仍由用户手动启动。本次文档交接范围没有业务、下游程序或系统执行。本MD直接程序导入、接收者恢复、真实业务、真实索引生成/收录及XMind客户端均未验证。
- 本轮状态展示为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/green/round-02-display.md` H88-R02-v1。实际选择及本轮读回核对位置保存于同目录 `process.md` 第2轮永久记录，等待后续实际反馈。

### 88第3轮名称输入框技术反馈

- 本轮承接对象为本准确文件文档v4及其第2轮文档交接范围，反馈原文为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/green/round-03-input.md`。来源为主持第3轮实际模拟反馈，转述后续编写人员的观察。文档v4→v5仅补充本技术说明，具体业务检查与有效评审继续适用原87准确v3，第2轮交接范围继续有效。
- 转述内容为工作标签名称与个人标签名称是两个独立输入框，定位方式不同，后续编写人员准备分别对应这两个控件。涉及对象仅为「M1/新建/名称」下工作标签名称输入框和个人标签名称输入框。当前没有现场独立验证、可核实定位字符串或定位成功证据，记录身份为待下游核实的转述观察。
- 下游分别核实这两个名称输入框的现场身份、定位及与用例步骤的映射，并据实际证据分别处理必要技术验证。名称的已评审共用业务规则仍适用两类，工作10/个人12的上限差异及相关超限、保存条件按既有规则恢复。控件独立和定位不同没有提供新的业务规则、确定预期或具体测试点评审。
- 本反馈适用性仅到上述两个名称输入框。用途字段、保存按钮、取消按钮、M2名称筛选输入等其他控件仍按各自现场证据判断，不由本条推定其独立或共用关系。没有补造定位字符串或将转述升级为现场验证。
- Q008及影响、M2指定手动快照成功且收录同一新建ID的前提、mock资料身份和下游/P0/P1/P2边界继续按前文处理。技术反馈由下游核实和处理，后续如出现业务规则、范围或预期变化，则返回必要澄清和受影响具体测试点重审。
- 本轮展示为 `C:/Users/lenovo/Documents/ChatGPT/ui-test/work/test-point-discovery-optimization-20261107/workers/88/evidence/optimization/88/green/round-03-display.md` H88-R03-v1。本轮完成技术信息记录后等待实际反馈，真实页面、业务、下游和客户端均未执行。

