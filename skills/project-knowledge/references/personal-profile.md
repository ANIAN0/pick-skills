# 个人知识库 profile

建设、迁移、查询或维护个人知识库时读取。本 profile 只扩展 OKF。

## 回答范围

- 当前项目的目标、边界、决策和修改风险；
- 相似历史问题的做法、结果和适用条件；
- 参考项目的可借鉴机制与限制；
- 长期主题的结论、争议和待验证问题。

## 类型

| 目录 / `type` | 核心内容 |
|---|---|
| `projects/` / `Personal Project` | 目标、范围、状态、架构入口、决策、成果、相关经验 |
| `reference-projects/` / `Reference Project` | 位置、观察版本/日期、机制、可借鉴模式、限制、许可证、来源 |
| `topics/` / `Personal Topic` | 综合结论、概念关系、争议、学习路径 |
| `lessons/` / `Personal Lesson` | 情境、症状、证据、行动、结果、适用边界 |
| `decisions/` / `Personal Decision` | 背景、选择、取舍、结果、重评条件 |
| `sources/` / `Personal Source` | 出处、日期、可信度、贡献页面 |
| `inbox/` / `Personal Inbox` | 原始 Capture 的可选浏览投影，不作为来源或长期事实入口 |

横切维度使用 tags 和关系，不按技术栈、行业或年份复制目录。项目页是知识地图；稳定机制、经验和取舍分别进入 topic、lesson 和 decision。缺少结果或适用边界的 lesson 保持 `draft`。

## 多来源与维护

不相交的项目、参考仓库和资料目录分别使用稳定 `source-id` 运行 inventory；manifest 放在 `<okf-root>/_meta/sources/<source-id>/`，并在 `_meta/sources.md` 登记根路径/URI、观察版本和权威范围。每个本地来源独立同步队列并披露进度；外部 URI 只登记快照与访问日期。

查询顺序：当前 project → topic → lesson → reference project → source。回答区分当前事实、历史经验和外部参考。维护优先处理 inbox、到期 `review_after`、失效来源和重复主题；项目结束后保留其到已提炼知识的链接。
