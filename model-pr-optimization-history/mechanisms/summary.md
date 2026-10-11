# 初步分类统计与条目预览

由 `scripts/mechanisms.py --rebuild` 从本地历史生成；这是检索线索，不是源码审核或收益证明。
分类可交叉，数量不能相加；功能支持、修复、测试和文档也可能命中。

覆盖 118 份英文模型档案、5660 张卡片，按框架和 PR 编号去重后 4618 个 PR。
其中 3358 个没有可靠的标题匹配，107 个具有多个候选机制。

| 方向 | 候选 PR 数 |
| --- | ---: |
| 计算方法与算子执行 (`compute`) | 874 |
| 依赖与执行重叠 (`overlap`) | 49 |
| 调度与执行粒度 (`scheduling`) | 13 |
| 数据驻留、布局与复用 (`data`) | 156 |
| CPU 控制与提交开销 (`host`) | 111 |
| 分布式与资源分配 (`distributed`) | 165 |

完整条目见 [index.jsonl](index.jsonl)，来源哈希见 [manifest.json](manifest.json)。
下方每类仅按框架和编号展示前 6 项，不表示优先级或代表性；四格代表案例从分类入口单独链接。

## 计算方法与算子执行

| PR | 标题 | 工作性质线索 |
| --- | --- | --- |
| [sglang:460](https://github.com/sgl-project/sglang/pull/460) | port fp8 mixtral | unclassified |
| [sglang:1290](https://github.com/sgl-project/sglang/pull/1290) | fix: resolve fp8 for mixtral | fix |
| [sglang:1341](https://github.com/sgl-project/sglang/pull/1341) | Add torchao quant (int4/int8/fp8) to llama models | unclassified |
| [sglang:1835](https://github.com/sgl-project/sglang/pull/1835) | [FP8 KV Cache, Mixtral] Avoid KeyError at loading pre-quantized FP8 m… | unclassified |
| [sglang:2637](https://github.com/sgl-project/sglang/pull/2637) | AMD: set weights and scaling numbers properly for block FP8 | unclassified |
| [sglang:2667](https://github.com/sgl-project/sglang/pull/2667) | AMD DeepSeek_V3 FP8 Numerical fix | fix |

## 依赖与执行重叠

| PR | 标题 | 工作性质线索 |
| --- | --- | --- |
| [sglang:5977](https://github.com/sgl-project/sglang/pull/5977) | Overlap qk norm with two streams | unclassified |
| [sglang:6598](https://github.com/sgl-project/sglang/pull/6598) | qwen3moe support two batch overlap | support |
| [sglang:9405](https://github.com/sgl-project/sglang/pull/9405) | Use dual stream for DS MoE whenever cuda graph is used (instead of with token threshold) | unclassified |
| [sglang:12405](https://github.com/sgl-project/sglang/pull/12405) | Fix the shared expert & routed expert overlap in Llama 4 | fix |
| [sglang:12660](https://github.com/sgl-project/sglang/pull/12660) | overlap shared + routed expert computation in kimi linear | unclassified |
| [sglang:12811](https://github.com/sgl-project/sglang/pull/12811) | use fast stream instead of torch.cuda.current_stream in llama 4 shared experts overlap | unclassified |

## 调度与执行粒度

| PR | 标题 | 工作性质线索 |
| --- | --- | --- |
| [sglang:5113](https://github.com/sgl-project/sglang/pull/5113) | Support MHA with chunked prefix cache for DeepSeek chunked prefill | support |
| [sglang:25333](https://github.com/sgl-project/sglang/pull/25333) | perf(mla): hybrid Triton fused cat+FP8-quantize for MLA chunked-prefill K/V | performance |
| [sglang:25964](https://github.com/sgl-project/sglang/pull/25964) | [EPD] Cross-request batching for image/audio encoder | unclassified |
| [sglang:32118](https://github.com/sgl-project/sglang/pull/32118) | Fix nightly CI: NVFP4 cuda-graph crash, NVILA batching, CuTe paged-KV zero-size, Kimi-VL OOM | fix, test-docs-ci |
| [sglang:33214](https://github.com/sgl-project/sglang/pull/33214) | Fix DeepSeek-OCR batching crash on variable local-crop counts | fix |
| [sglang:34044](https://github.com/sgl-project/sglang/pull/34044) | docs(cookbook): DeepSeek-V4-Flash-0731 — drop chunked-prefill/autotune flags on B300 low-latency | test-docs-ci |

## 数据驻留、布局与复用

| PR | 标题 | 工作性质线索 |
| --- | --- | --- |
| [sglang:7](https://github.com/sgl-project/sglang/pull/7) | fix radix cache match | fix |
| [sglang:1835](https://github.com/sgl-project/sglang/pull/1835) | [FP8 KV Cache, Mixtral] Avoid KeyError at loading pre-quantized FP8 m… | unclassified |
| [sglang:5113](https://github.com/sgl-project/sglang/pull/5113) | Support MHA with chunked prefix cache for DeepSeek chunked prefill | support |
| [sglang:5349](https://github.com/sgl-project/sglang/pull/5349) | vlm: enable radix cache for qwen-vl models | support |
| [sglang:5748](https://github.com/sgl-project/sglang/pull/5748) | Fuse MLA set kv cache kernel | unclassified |
| [sglang:6109](https://github.com/sgl-project/sglang/pull/6109) | [Feat] Support FlashMLA backend with MTP and FP8 KV cache | support |

## CPU 控制与提交开销

| PR | 标题 | 工作性质线索 |
| --- | --- | --- |
| [sglang:4514](https://github.com/sgl-project/sglang/pull/4514) | Support FlashMLA backend cuda graph | support |
| [sglang:6162](https://github.com/sgl-project/sglang/pull/6162) | [Bugfix] Fix Llama4 gibberish output with long context and CUDA graph | fix |
| [sglang:9405](https://github.com/sgl-project/sglang/pull/9405) | Use dual stream for DS MoE whenever cuda graph is used (instead of with token threshold) | unclassified |
| [sglang:13055](https://github.com/sgl-project/sglang/pull/13055) | [VLM] Support Piecewise CUDA Graph for Qwen2.5-VL | support |
| [sglang:13081](https://github.com/sgl-project/sglang/pull/13081) | Support piecewise cuda graph for Qwen3-next | support |
| [sglang:13466](https://github.com/sgl-project/sglang/pull/13466) | [Piecewise CUDA Graph] Support Kimi-K2 (non-Thinking) | support |

## 分布式与资源分配

| PR | 标题 | 工作性质线索 |
| --- | --- | --- |
| [sglang:2203](https://github.com/sgl-project/sglang/pull/2203) | MoE Expert Parallel Impl | unclassified |
| [sglang:2371](https://github.com/sgl-project/sglang/pull/2371) | MoE Expert Parallel | unclassified |
| [sglang:6250](https://github.com/sgl-project/sglang/pull/6250) | Add pipeline parallelism for Qwen2 and Qwen3 Model | unclassified |
| [sglang:6533](https://github.com/sgl-project/sglang/pull/6533) | support eplb for qwen3 | support |
| [sglang:6546](https://github.com/sgl-project/sglang/pull/6546) | added support for tied weights in qwen pipeline parallelism | support |
| [sglang:6818](https://github.com/sgl-project/sglang/pull/6818) | Fix wrong weight reference in dynamic EPLB | fix |

## 待分类

| PR | 标题 | 工作性质线索 |
| --- | --- | --- |
| [sglang:1](https://github.com/sgl-project/sglang/pull/1) | Add flashinfer && Oultines | unclassified |
| [sglang:108](https://github.com/sgl-project/sglang/pull/108) | Fix Mistral model loading | fix |
| [sglang:1081](https://github.com/sgl-project/sglang/pull/1081) | Update the mixtral to use the better FusedMoE layer | unclassified |
| [sglang:1418](https://github.com/sgl-project/sglang/pull/1418) | Add torchao quant for mixtral and qwen_moe | unclassified |
| [sglang:2055](https://github.com/sgl-project/sglang/pull/2055) | Add support for Qwen2-VL-based embedding models | support |
| [sglang:2156](https://github.com/sgl-project/sglang/pull/2156) | feat: update other MoE models deps | support |
