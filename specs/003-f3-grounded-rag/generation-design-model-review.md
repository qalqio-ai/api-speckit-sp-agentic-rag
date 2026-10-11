# Generation design/model review after v3 failure

Prompt iteration is stopped under EDM's explicit direction. This is a review,
not authority to implement an architecture change, acquire another model or claim
acceptance. Original contracts/limits/current factory and validators preserved.

## Accumulated observations

| Configuration | Actual observed result |
| --- | --- |
| Original approved system prompt |Three supported exposed cases failed output_too_large; one detailed regression reached384newtokens without EOS. Generated787bytes,54.015s model.generate in the detailed diagnostic, correct fail-closed boundary. |
| V2 explicit schema prompt |One regression reached EOS after43tokens but failed required chunk_ids; copied source text instead of reviewed rule rendering. Retained diagnostic replay confirms valid JSON, not schema validity. |
| V3 explicit rules-text/supporting-ID mapping |Same regression reached EOS after43tokens; byte-identical157byte raw output as v2 replay, same missing IDs and rendering error.18.087s generation stage/26.490s total. |

All observations use the pinned SmolLM2-360M-Instruct revision
 a10cc1512eabd3dde888204e902eca88bddb4951, unchanged evidence and CPU FP32 greedy
configuration. These results establish failure on the tested regression, not a
universal statement about this model or model size. Numerical resource/context
limits were not the v2/v3 rejection cause; EOS, syntax and transport succeeded.
The system properly suppressed invalid output. There is no evidence supporting
weaker claim validation, fabricated citation IDs or post-generation repairs.

## Design choices for review

| Option | Contract/resource implications | Evidence and required next proof |
| --- | --- | --- |
| Review constrained generation with current pinned model |Constrain choices during actual generation to closed JSON shape and current evidence IDs, preserving a legitimate abstention branch. Keep final exact-rendering/full-support validation, one genuine model.generate, EOS and existing ceilings. No post-generation completion or scripted answer substitution. This changes the generation design/configuration and needs reviewed scope and TDD first. |Targets demonstrated schema/ID failures. Structure constraints alone cannot establish semantic support; measure latency/memory and dead-end/invalid-prefix handling with the exact locked runtime before any claim. If constraints also force catalog strings, reviewers must acknowledge the stronger catalog-selection boundary and ensure genuine model decisions remain meaningful. |
| Review a different local generation model |Preserve existing response/grounding contracts and bounds. No specific replacement selected; approval requires exact upstream pin/files/sizes/license/destination and a fresh model/configuration fingerprint before acquisition. Do not assume fit from parameter count or increase resources. |Current model fails this frozen regression despite explicit mapping. A different model may improve instruction adherence, but no evidence of its quality or CPU memory/latency exists. Test regression set first; freeze any successful candidate before independently prepared untouched acceptance. |
| Retain present model and fail-closed behavior |No scope/resource change; safe failures remain failures. |Appropriate current operational status; cannot meet SC-001/002 supported answer/citation acceptance. |

Recommended review order:bounded constrained-generation feasibility with the
already-approved model first, then a separately approved model candidate if that
design cannot preserve the learning objective or fails regression/resource checks.
This recommendation is an inference from the observed schema/ID noncompliance,
not evidence that constrained generation will pass. Official Transformers generation
APIs expose generation-time token-control mechanisms
([official documentation](https://huggingface.co/docs/transformers/v5.12.0/en/main_classes/text_generation)).
That documentation is conceptual support, not verification of compatibility of a
new grammar with the exact installed5.18.0/greedy/CPU configuration. No dependency
installation or implementation is proposed as an already completed result.

## Gates before any fresh acceptance

Review one chosen design/model change, add behavioral failing regressions and
resource/semantic safety checks, then verify the known generation regressions.
Freeze complete prompt/model/assets/generation mechanism/retrieval/catalog/source/
case fingerprints. Fresh cases must be independently prepared, untouched and
reviewed under the approved exact-alias/catalog boundary before execution. No
relabeling exposed cases as fresh acceptance. The separate F2 receipt regression
remains failed under frozen threshold0.45614706000000005/calibrationEDM-f2-20261004-v1;
do not silently retune it within generation work or claim full F3 acceptance.

No prompt-v4 experiment, fallback, acquisition, acceptance run, commit or publication.
