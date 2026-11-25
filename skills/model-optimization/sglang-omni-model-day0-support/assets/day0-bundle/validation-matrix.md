# Validation Matrix

## Risk Pairs

{{APPLICABLE_CAPABILITIES_SHARING_STATE_TIMING_OR_PLACEMENT_AND_HOW_TO_TEST_THEM_OR_REASON_NONE_APPLY}}

## Required Lanes

Cover source, load, protocol, state, topology, quality/performance and release for the scoped claims. Record the reason for any inapplicable gate. Mark missing weights, hardware or reference evidence as blocked for the affected claim.

| Gate | Claim | Reproducible command and input | Expected result and reference or tolerance | Status | Observed result and artifact |
| --- | --- | --- | --- | --- | --- |
| {{GATE}} | {{CLAIM}} | {{COMMAND_AND_INPUT}} | {{EXPECTED_RESULT}} | {{STATUS}} | {{OBSERVATION_OR_BLOCKER}} |

For each claimed path, retain the real request and the final output or event sequence from the public entry point. For a performance claim, record the hardware, workload, amount of output and measured result.
