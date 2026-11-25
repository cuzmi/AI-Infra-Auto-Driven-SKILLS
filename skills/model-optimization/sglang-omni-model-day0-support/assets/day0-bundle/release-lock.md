# Release Lock

## Source Revisions

| Component | Public source | Immutable revision |
| --- | --- | --- |
| SGLang-Omni | https://github.com/sgl-project/sglang-omni | {{OMNI_SHA}} |
| Model reference implementation | {{REFERENCE_SOURCE}} | {{REFERENCE_REVISION}} |

Add the SGLang backend when this variant uses it. Pin other runtime dependencies that affect the release claim.

## Artifacts

| Artifact | Identifier and revision or digest | Used by | Verification |
| --- | --- | --- | --- |
| Model weights | {{CHECKPOINT_AT_REVISION}} | {{VARIANT}} | {{LOAD_EVIDENCE}} |

Add separately versioned processors, codecs, vocoders, VAEs, images or fixtures when the claimed path depends on them. Identify the configuration and command that reproduce the tested variant.

{{CONFIGURATION_AND_LAUNCH_COMMAND}}

## Limitations

{{VERIFIED_ENVIRONMENT_AND_REMAINING_LIMITATIONS}}
