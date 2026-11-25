# Architecture Gap Map

## Capability Classification

Follow each scoped request through the selected pipeline to its client-visible result. Identify the actual stage connections, when payloads cross them and who owns any request or session state. A single-stage pipeline can have both input and output in the same row.

| Claim | Reference implementation | Omni stage or boundary | Input → output and delivery timing | Reuse or missing work | Work class |
| --- | --- | --- | --- | --- | --- |
| {{CLAIM}} | {{REFERENCE_SOURCE}} | {{OMNI_SOURCE_OR_MISSING_BOUNDARY}} | {{PAYLOAD_OR_STATE_CONTRACT}} | {{REUSE_OR_DELTA}} | {{WORK_CLASS}} |

## Evidence

{{PINNED_SOURCE_PATHS_SUPPORTING_THE_MAP}}

Link a reviewed PR record when using historical PR evidence.
