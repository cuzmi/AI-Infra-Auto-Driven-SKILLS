# 按优化机制检索 PR 历史

保留原有“框架 → 模型 → PR”档案，在上面增加一层机制索引。目标是帮助选择调查方向，
再回到原始档案和具体代码分析；不要求每次任务都检查所有类别。

先看 [分类统计与条目预览](summary.md)。完整索引是 [index.jsonl](index.jsonl)，
来源文件及哈希在 [manifest.json](manifest.json)。

## 六个方向

| 标识 | 方向 | 要问的问题 | 典型子类 |
| --- | --- | --- | --- |
| `compute` | 计算方法与算子执行 | 计算本身能否更省、更快？ | 融合、kernel 替换、量化、稀疏计算、推测解码；数值与质量约束按机制检查 |
| `overlap` | 依赖与执行重叠 | 哪些工作在不必要地等待？ | 提前启动、独立 stream、通信/计算重叠、细化等待点 |
| `scheduling` | 调度与执行粒度 | 谁先执行，每次执行多少？ | 合批、continuous batching、chunked prefill、准入、优先级、公平性 |
| `data` | 数据驻留、布局与复用 | 数据放在哪里、如何交接和复用？ | 去掉重复复制、分块队列、layout、内存池、分页、缓存、offload/prefetch |
| `host` | CPU 控制与提交开销 | GPU 是否在等待准备与提交？ | metadata 预计算、隐式同步、Python 开销、减少 launch、避免重复编译 |
| `distributed` | 分布式与资源分配 | 工作和数据如何分配到多卡或多实例？ | TP/EP/PP、P/D 分离、专家负载均衡、请求路由、通信方式与传输量 |

六类是搜索入口，不是互斥的硬件层次，也不保证现有档案覆盖每一个子类。
按主要改变的机制定主类，其他机制作为交叉标签。多重命中且证据不足时不强行指定主类。
例如，通信量不变、只提前启动 all-gather，主类可为 `overlap`，附加 `distributed`；
重新分配专家负载则优先看 `distributed`。这些主次关系必须结合实现判断。

`scheduler` 不一定是请求调度：kernel 内部调度、扩散数值更新器、CI 调度分别判断。
`CPU` 后端不等于 CPU 控制开销，`metadata` 也可能由 GPU kernel 处理。
CUDA Graph 若主要减少 host launch 开销，归 `host`；若改变依赖重叠，可增加 `overlap`。

## 三个独立维度

1. **优化机制**：六类候选标签、候选主类、分类依据。
2. **工作性质**：`performance`、`support`、`fix`、`refactor`、`test-docs-ci`、`revert` 或 `unclassified`。
   允许多个性质并存；带有性能词汇的修复或测试不能因此当作成功优化。
3. **证据范围**：档案出处、是否重读完整 diff、是否审查测量、适用范围是否建立。
   合并状态和标题中的性能数字都不能替代这些证据。

## 当前证据边界

- 批量分类只根据标题中的明确短语生成 `title_heuristic`，未匹配项保留为待分类。
  这不是对全部 PR 内容的人工归类；需要完整 diff 才能确认机制。
- 7 个种子条目经过本地卡片/代码摘录阅读，标为 `local_excerpt_read`，仍不是完整 diff 审核。
  其中六个有 [四格代表案例](../../skills/optimization-analysis/references/history-cases.md)。
- 所有记录的测量都是 `not_assessed`，适用范围是 `not_established`。
  这表示本次未评估，**不是说原 PR 没做过实验**。案例中的代价、变量和验证步骤是分析假设。
- `archived_status_date` 来自旧档案，未联网刷新；使用具体 PR 时重新核对状态、完整 diff 和当前调用方。
- `model_dossiers` 仅表示哪些档案收录了该 PR，不证明这些模型都执行该路径。
- 只索引英文档案内的独立 PR 卡片，中文镜像不重复计数；只有时间线、没有卡片的项目不在本次索引范围。
  同一 PR 跨模型重复收录按框架和编号去重，保留全部卡片出处和行号。

当前来源按模型文件收集，因此通用 scheduler、路由、队列和集群策略可能收录不足。
某类数量少不能证明该方向不重要，也不能证明没有相关优化。

## 查询与刷新

在 `model-pr-optimization-history/` 下运行（仅需 Python 标准库，无网络/GPU）：

```bash
python3 scripts/mechanisms.py --category scheduling --limit 20
python3 scripts/mechanisms.py --category host --framework tensorrt_llm --kind performance
python3 scripts/mechanisms.py --category data offload --json
python3 scripts/mechanisms.py --category unclassified --limit 10
python3 scripts/mechanisms.py sglang:21932
python3 scripts/mechanisms.py --check
python3 scripts/mechanisms.py --rebuild
```

查询的多个词同时匹配；结果显示候选机制、工作性质和回读原档案的位置。
`--check` 核对生成内容与来源哈希；历史刷新后用 `--rebuild` 更新索引，不改写原档案。
记录中的 `matched_title_terms` 保留自动命中的理由，便于发现误分。

下一轮应优先读完整 diff、调用方和原实验，再把“收益假设”提升为带明确范围的证据。
对于暂缺的公平性、队首阻塞、流式缓冲等方向，补查框架级 PR，而不是把标题近似的条目硬塞进去。
