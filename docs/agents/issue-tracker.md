# GitHub Issues

本仓库的规格与任务保存在 [Zengxiansheng007/coedx-home Issues](https://github.com/Zengxiansheng007/coedx-home/issues)。每批发布采用用户本次指定的仓库。尚未指定时，请用户在已登记的仓库中选择。连接器调用显式传入完整仓库名，使用 `gh` 时显式传入 `--repo`。

## 发布与核对

1. 使用已认证的 GitHub 连接器，或使用已有本机认证的 `gh`。先核对目标仓库，再按标题和主题查找已有的开放及已关闭议题。
2. 用结构化正文参数发布规格或任务。使用 CLI 时，把多行正文交给 `--body-file`。规格准备好后应用 `ready-for-agent`。
3. 按返回编号读回议题，核对目标仓库、正文和标签。更新已有议题时保留仍适用的标签和关联关系。

## 任务关系

子任务优先使用 GitHub 子议题，阻塞关系使用原生 issue dependencies。若当前客户端无法写入相应关系，在正文首部用 `Part of #编号` 或 `Blocked by #编号` 明示。关闭任务时在议题中记录结论。

**PRs as a request surface: no.**
