# Six mechanism examples from the local PR history

**Evidence status: local history cards and their excerpts only.** No full PR
diff was re-audited, no current dispatch was checked, and no experiment was run
for these examples. The observations below are limited to the archived material.
Costs, eligibility factors, and tests are hypotheses to investigate, not claimed
author conclusions or demonstrated applicability. The original PR may contain
measurements that this first pass has not assessed.

Use these examples to connect a mechanism category to the four questions.
Read only the relevant example. The complete candidate index and its evidence
rules are in the [mechanism guide](../../../model-pr-optimization-history/mechanisms/README.md).

## 1. Compute: merge projections and support strided normalization

Source: vLLM #21116, "Add fused MLA QKV + strided layernorm";
[local history](../../../model-pr-optimization-history/vllm/deepseek-v3-r1/README.en.md).
Find `### PR #21116` in that file.

Observed: the archived diff introduces `MergedReplicatedLinear` and changes
`kv_a_layernorm(kv_a.contiguous())` to `kv_a_layernorm(kv_a)`. Candidate primary
category: compute; secondary: data layout.

Target/path hypothesis: separate projections and layout materialization become
a merged projection with a consumer that accepts the resulting stride; assess
layer latency and then serving latency.

| Question | Investigation |
| --- | --- |
| Saved cost | Fewer separate projection calls and a potentially avoidable contiguous copy. Identify both independently. |
| Conditions | Weight partitioning, shapes, strides, and quantization contracts must match. Benefit may depend on batch and projection dimensions. |
| Added cost | A merged shape can select a different GEMM; strided consumer access may be slower. Neither tradeoff is established by the excerpt. |
| Comparison | Test numerical contracts and actual dispatch. Compare original, merge-only, stride-only where feasible, and combined paths at the same shapes, then unprofiled serving. |

Decisive question: does removing the copy improve the producer/consumer total,
or does the consumer lose more time than the copy saved? No measured range is
established here. Next read the merged weight layout and normalization caller.

## 2. Overlap: run Q/K normalization on two streams

Source: SGLang #5977, "Overlap qk norm with two streams";
[local history](../../../model-pr-optimization-history/sglang/deepseek-v3-r1/README.en.md).
Find `### PR #5977`.

Observed: the card locates the change in `deepseek_v2.py::forward_absorb` and
records use of two streams. Candidate primary category: overlap, not request
selection. Target: reduce the completion time at the Q/K consumer join.

| Question | Investigation |
| --- | --- |
| Saved cost | Potentially overlap independent normalization work instead of adding its elapsed times. |
| Conditions | Verify producer readiness and consumer waits. The two paths need legal concurrency and enough effective resource headroom. |
| Added cost | Stream/event management and competition for compute or bandwidth can offset hidden time. |
| Comparison | At fixed work and shapes, compare serial/concurrent paths. Check correctness, all relevant streams and the join time, then measure without profiling. |

Decisive question: did the join move earlier, rather than only making the
timeline look more overlapped? Next read all stream dependencies. No tested
shape or hardware benefit is established in this analysis.

## 3. Scheduling/granularity: batch vision encoder work

Source: vLLM #43169, "Batch vision encoder calls for image and video processing";
[local history](../../../model-pr-optimization-history/vllm/gemma4/README.en.md).
Find `### PR #43169`.

Observed: the card identifies `_encoder_max_batch`, `_process_image_input`, and
encoder budget/bytes-per-patch state. It does not prove cross-request batching
or a new request admission policy. Candidate primary category: execution
granularity. Target/path hypothesis: fewer encoder calls for eligible items.

| Question | Investigation |
| --- | --- |
| Saved cost | Amortized call overhead and potentially better device utilization. |
| Conditions | Items must be compatible, available together, and fit the encoder memory budget; preserve output order. |
| Added cost | Larger activations, possible padding, or longer uninterrupted work. Added queue wait applies only if this implementation actually waits for arrivals. |
| Comparison | Compare the same image/video items and total patches; sweep compatibility and size spread. Measure actual batch formation, memory, encoder latency, and request latency. |

Decisive question: is there enough compatible ready work to form useful batches?
Next inspect the grouping and memory-budget logic, plus the subsequent #43296
fix recorded in the same history. No concurrency or batch-size range is proven
here; support for batching alone is not a throughput measurement.

## 4. Data residency: avoid transient GPU allocation of an offloaded table

Source: SGLang #39928, "Build the offloaded PLE table on the meta device";
[local history](../../../model-pr-optimization-history/sglang/qwen4-exp/README.en.md).
Find `### PR #39928`.

Observed: the title and initializer excerpt concern an offloaded embedding
table and `Qwen4ExpPinnedHostEmbedding`. Candidate primary category: data;
lifecycle phase: model initialization, not per-token serving.

| Question | Investigation |
| --- | --- |
| Saved cost | Hypothesis: avoid allocating the full table on GPU only to move it to its intended host placement. Target startup peak memory. |
| Conditions | The offload path must initialize/load all weights correctly without relying on materialized GPU storage. |
| Added cost | Inspect loader/lifetime changes. Do not charge this patch for CPU lookup or transfer costs already present in the baseline offload path. |
| Comparison | Compare old/new implementations with offload enabled in both, using identical weights and hardware. Check loading correctness, startup peak memory/time, and subsequent lookup behavior. |

Decisive question: does the change remove a transient allocation or alter the
steady-state storage policy too? Next inspect the full load path. The archived
card is explicitly a generated inventory; no startup or serving gain is proven
by this example.

## 5. Host control: avoid an implicit device-scalar synchronization

Source: TensorRT-LLM #16734, "Avoid implicit device-scalar syncs in DeepSeek-V4
ctx sparse metadata";
[local history](../../../model-pr-optimization-history/tensorrt_llm/deepseek-v4/README.en.md).
Find `### PR #16734`.

Observed: the excerpt computes host-side compressed-token counts so position-ID
construction does not read a device scalar for sizes/slice bounds. Candidate
primary category: host; secondary: data transfer. Target: host critical-path
delay and the resulting prefill latency.

| Question | Investigation |
| --- | --- |
| Saved cost | A device-to-host scalar read and its implicit stream wait. Few transferred bytes can still expose a long dependency wait. |
| Conditions | Host-derived sizes must exactly match device semantics across compression ratios, empty outputs, and mixed request modes. |
| Added cost | Host computation/state maintenance may replace the read; inspect whether new synchronization remains elsewhere. |
| Comparison | Compare generated positions and boundaries first, then count synchronization points and GPU gaps at identical workloads. Measure unprofiled prefill/serving latency separately. |

Decisive question: does the removed read lie on the critical path? Next inspect
count derivation and fallback branches. Small byte volume does not rule out
benefit, and removing a sync alone does not establish an end-to-end gain.

## 6. Distributed allocation: balance shared-expert dispatch

Source: SGLang #19290, "Add waterfill load balancing for shared expert dispatch";
[local history](../../../model-pr-optimization-history/sglang/deepseek-v3-r1/README.en.md).
Find `### PR #19290`.

Observed: the card lists `WaterfillDispatchPlan`, per-rank routed counts,
dispatch expansion, and integration into MoE routing. Candidate primary
category: distributed resource allocation. Target: the slowest-rank completion
time and serving throughput at a fixed topology.

| Question | Investigation |
| --- | --- |
| Saved cost | Hypothesis: reduce imbalance-driven waiting by redistributing eligible shared-expert work. |
| Conditions | Verify expert semantics, placement, dispatch/combine contracts, and backend eligibility. Routed-load skew is a candidate benefit factor. |
| Added cost | Planning, redistribution, communication, and extra buffer work may offset a shorter rank tail. |
| Comparison | Compare the same tokens/routing inputs and topology; vary skew at fixed total work for a mechanism experiment. Inspect per-rank load, communication, join time, correctness, and serving repeats. |

Decisive question: is the removed slow-rank tail larger than redistribution
overhead? Next read placement and combine semantics. A balanced synthetic case
and a skewed case can have different outcomes; no measured threshold or
deployment recommendation is established here.
