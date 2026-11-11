# Reviewed test points - v1 (simulated development only)

## 部门资料

### 【待确认】
- 无；范围按模拟S1/A1，仅新增、编号查询、改名及指定关联影响。

### 【待产品确认】
- P1：部门改名后历史费用单名称展示规则未定；已纳入必需覆盖，不能确定跟随新名或保留快照。金额计算不依赖名称，可独立继续。

### 新增
- 编号、名称分别为空时拒绝创建；其余字段有效时分别检查，避免相互遮蔽。
- 编号全库原样比较：已有A01时新增A01拒绝；a01按不同编号允许创建，前后含空格的编号拒绝。
- 名称按Unicode码点计数且不归一化：0、1、2、19、20、21个码点分别对应拒绝、允许、允许、允许、允许、拒绝；其余字段有效。
- 有效新编号与合法名称创建后，按该编号查询所得记录的编号、名称与输入一致。

### 按编号查询
- 查询精确匹配编号，仅返回对应部门；A01与a01分别匹配自己的记录。
- 不存在的编号查询显示无记录。
- 改名完成后以原编号查询，列表和同一编号详情呈现新名称。

### 修改名称
- 未被费用单使用的部门允许改名；保存后编号不变、列表和详情同一部门显示新名称，编号不可改。
- 已被费用单使用的部门改名被拒绝；不编造具体拒绝文案。
- 名称必填；其余条件合法时按Unicode码点、不归一化检查0、1、2、19、20、21分别拒绝、允许、允许、允许、允许、拒绝。
- 历史费用单中的部门名称展示核对保留P1，未知预期不填入通过标准。

## 资料与Agent交接说明

- v1; scope: department-d1; simulated R1 approval in session.md; sources D1/D2/C2/S1/S2 and A1. P1 unresolved and required. No handoff or client verification. Full source mapping: D1 to create/query; D2 to rename and P1; C2 to identifier and name propagation. No calculation approval yet.

<!-- Historical v1 evidence only; not current authority. -->
