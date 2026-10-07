# 统一验证

使用 Python 3.13（工具兼容 Python 3.10+），先在选定 Python 环境安装明确依赖：

```powershell
python -m pip install -r requirements-checks.txt
npm run check
npm run check:local
```

两个 npm 脚本均调用 tools/checks.py。`check` 验证现有状态/路由测试、新增检查工具回归、技能格式、注册表及仓库分发副本；`check:local` 额外强制核验 CODEX_HOME/skills（未设置则 ~/.codex/skills）的全局 develop-system 与 grill-with-docs。也可直接 `python -B tools/checks.py --installed <技能父目录>`。全局副本不存在不会静默跳过。

每次运行使用独立结果目录；可指定 `--output-dir <尚不存在的目录>`。任一阶段非零/超时/启动失败，最终退出码非零；各阶段记录命令数组、退出码和完整 stdout/stderr，summary.json 记录状态、范围和记录哈希。结果在 `.scratch/verification/<唯一编号>`。专业技能查看输出判断充分性，调度器核验机器记录，不重新做业务验收。

格式校验器为 tools/verification/skill_format.py 的固定本地快照，来源见同目录 README。依赖固定 PyYAML==6.0.3；缺失或版本不同直接失败，工具不会自动安装依赖。不会把旧包装报告的成功声明当作当前证据。

源码在 .agents/skills，下游分发副本在 skill-packages；修改后显式同步对应文件，然后运行检查。比较完整相对文件集合与字节哈希，忽略 __pycache__ 和 .pyc；新增、缺失、多余和变化的文件均会失败。不要用同步命令隐式抹除用户副本改动。

GitHub Actions 的 check-skills.yml 在 push、pull_request、手动触发时，在 Windows/Linux Python 3.13 执行相同入口，并始终尝试上传结果。CI 只检查仓库源码与分发副本，不声称访问开发者全局目录。本地全局核验须使用 check:local。

CI 配置采用 [GitHub Python 工作流说明](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) 的 setup-python 与结果归档方式。没有给 Git 配置强制提交钩子；CI 作为提交后的持续检查。工作流实际远程执行和分支保护需在仓库发布后查看结果；本地通过不等于 GitHub runner 已通过。
