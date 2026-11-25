---
name: sglang-omni-model-day0-support
description: Plan, implement, or audit Day-0 support for a model in SGLang-Omni. Use when mapping a checkpoint and serving variant to the Omni pipeline or deciding whether its public entry point delivers the promised output.
---

# SGLang-Omni Model Day-0 Support

Define a release claim that a client can exercise. For a full release, copy the [eight bundle templates](assets/day0-bundle/) into the model-support workspace. For a plan or a review, fill the parts needed for the decision and mark unexecuted checks as pending.

## Define the release claim

1. In the scope contract, name the checkpoint revision, serving variant, public entry point, accepted input, expected output, mode of delivery, and target hardware. If a model exposes several variants, state which ones this release covers.
2. Lock the Omni revision and the artifacts actually loaded by that variant. These may include a processor, codec, vocoder, VAE, SGLang backend, or separately versioned weights. Record the launch command and configuration that select them.
3. Identify the upstream reference or task evaluation and the correctness criterion before implementing the path. Distinguish a requested release target from a measured result.

## Map the request through Omni

Trace a representative request in the pinned upstream implementation and the closest Omni pipeline. Begin at the client entry point, follow request conversion, model registration, stage factories and routing, and finish at the payload or events the client receives. Read the selected variant in `sglang_omni/models/<family>/config.py`. Follow `next`, `stream_to`, joins and terminal stages where present. Stage construction order can differ from request order.

Create a gap-map row for each part of this path that needs implementation or verification. Name the upstream behavior, existing Omni symbol, delta, and test. At a stage boundary, record the payload and units, who produces and consumes it, and any state kept across chunks or requests. Check attention, KV ownership, quantization, or distributed placement when the traced path uses them. A single-stage model can have a single row.

Classify implementation work as `day0-required`, `post-day0-fix`, `performance-only`, or `experiment-or-revert`. Build the PR dependencies from the actual gaps. A small integration can be one PR. Keep a runnable baseline when adding an optional fast path.

## Verify and report

Apply the [seven release gates](references/day0-contract.md) to each claim. Use the public client entry point on the declared hardware, retain its output, and compare it with the agreed reference. For streaming, capture what the client receives during generation and at completion. For sessions, exercise the promised interaction and state lifetime. Record performance only for a named workload and metric.

For a full release, complete the validation matrix, release lock, PR body, follow-up ledger, and sanitization report. If a required run lacks weights, hardware, or a reference result, record the blocker or narrow the release claim. A planned test, successful startup, and completed template each answer a different question from an observed user result.

### Public evidence

For a cited PR, review its diff, tests, and final reachable code. Use the bundle validator's record format, replacing each field with the reviewed value:

```text
- Evidence: https://github.com/sgl-project/sglang-omni/pull/NUMBER | state: STATE | head: FULL_HEAD_SHA | limitation: SCOPE_OF_EVIDENCE
```

Use `open`, `merged`, `closed` (closed without merging), or `reverted`; include a 40-character commit SHA. If support has no prior PR, cite the pinned model and Omni source instead. Check the final bundle for unresolved fields and private artifacts, paths, identifiers, and credentials. Keep any private denylist outside the public bundle.

The existing Day-0 tools accept the Omni repository explicitly. From a checkout of this skills repository, run the following with `bundle` set to the completed bundle directory:

```bash
tools_dir=skills/model-optimization/sglang-model-day0-support/scripts
python3 "$tools_dir/validate_day0_bundle.py" "$bundle" --allow-repository sgl-project/sglang-omni
```

Add `--denylist FILE` for a private-input audit. To collect PR metadata, use `python3 "$tools_dir/collect_public_pr_evidence.py" "$pr_url" --output "$output_file" --allow-repository sgl-project/sglang-omni`. Repeat the repository flag for each additional public evidence source. Standalone installations can obtain the same [validator](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/9b3505b8477bdd4826e34c1d7fd0c2f2795bd8cd/skills/model-optimization/sglang-model-day0-support/scripts/validate_day0_bundle.py) and [collector](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/9b3505b8477bdd4826e34c1d7fd0c2f2795bd8cd/skills/model-optimization/sglang-model-day0-support/scripts/collect_public_pr_evidence.py). The validator checks the documents. Use the recorded run evidence to decide readiness.
