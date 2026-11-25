# Day-0 Scope Contract

## Release Cut

- Checkpoint and immutable revision: `{{CHECKPOINT_AT_REVISION}}`
- Omni revision and serving variant/config: `{{OMNI_SHA}}`, `{{VARIANT_CONFIG}}`
- Hardware, precision and deployment topology: {{TARGET_ENVIRONMENT}}

## Required Capabilities

Write one row per publicly claimed behavior. Use the same claim name in the gap map and validation matrix.

| Claim | Public entry point | Input | Observable output and completion condition |
| --- | --- | --- | --- |
| {{CLAIM}} | {{ENTRY_POINT}} | {{REQUEST_INPUT}} | {{EXPECTED_CLIENT_OUTPUT}} |

## Out of Scope

{{EXCLUDED_VARIANTS_OR_BEHAVIORS_AND_REASON}}
