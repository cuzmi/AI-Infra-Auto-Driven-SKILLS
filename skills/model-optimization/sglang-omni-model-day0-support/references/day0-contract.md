# SGLang-Omni Day-0 contract

Evaluate each checkpoint, variant, and public entry point named in the release claim. Define one representative input and a client-observable result. Add cases where two promised behaviors share state or an output boundary, such as concurrent requests that share an audio decoder or a session ending with a partial chunk.

| Gate | What closes it for this claim |
| --- | --- |
| Source | Record immutable revisions for Omni, the checkpoint, its reference implementation, and separately loaded components. Identify the exact configuration and backend used. |
| Load | Start the selected variant on the target hardware. Verify that its registry entry and stage factories load the expected weights and components. |
| Protocol | Run a complete request through the declared API or offline entry point. Check the input and response contract, including modality, format, units, and the final event or file as applicable. |
| State | Identify request, chunk, and session state on this path. Where it exists, exercise the relevant isolation, flush, cancellation, or close behavior. If there is no persistent state to exercise, record why. |
| Topology | Exercise the declared stage and device layout. For a split pipeline, verify delivery at the relevant boundary. For a single-stage deployment, the end-to-end run on the target device can supply this evidence. |
| Quality/performance | Compare the result with the pinned reference or a task-appropriate evaluation. For sampled outputs, define a meaningful tolerance or task score. If the release includes a performance claim, record its threshold, hardware, workload, concurrency, output work and measured result. |
| Release | Provide a reproducible launch and client command, test evidence, supported scope, and remaining blockers or limitations. Review the public artifacts at the release revision. |

## Choosing the right observation

The same endpoint can serve different products. Read the model cookbook and implementation at the target Omni revision before selecting gates and metrics.

- **Streaming speech.** Qwen3-TTS on `/v1/audio/speech` can send codec output from its engine to a vocoder before generation finishes. Use a prompt long enough to observe the first playable samples arriving while the producer is still generating. HTTP headers and the number of transport chunks alone cannot establish this. Retain the completed waveform and compare the spoken content with the input text. If latency or continuity is claimed, measure first audio and playback gaps at the client. See the [Qwen3-TTS cookbook](https://github.com/sgl-project/sglang-omni/blob/main/docs/cookbook/qwen3_tts.md) and [TTS benchmark](https://github.com/sgl-project/sglang-omni/blob/main/docs/developer_reference/tts_bench.md).
- **Offline music.** YuE2 uses the same endpoint for 48 kHz stereo music from lyrics and style. Verify the completed audio and the documented behavior for unsupported streaming. A fixed-seed smoke test checks reproducibility. To claim music quality, match the reference transformer, VAE, prompts, and generation settings. See the [YuE2 cookbook](https://github.com/sgl-project/sglang-omni/blob/main/docs/cookbook/yue2.md).
- **Realtime sessions.** For a native-duplex claim, check the advertised capabilities and exercise overlapping input and output on the session variant. If natural interruption is claimed, test user speech arriving during the reply. An explicit cancellation tests the cancel operation. See the [full-duplex guide](https://github.com/sgl-project/sglang-omni/blob/main/docs/developer_reference/full_duplex_guide.md).

Record the command, revisions, hardware, observed result or artifact, and limitation for each run. Reuse one end-to-end observation across gates when it proves each assertion. A failing or untested required capability keeps that claim open.
