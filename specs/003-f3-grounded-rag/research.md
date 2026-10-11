# F3 research decisions

Date: 2026-10-02. Two read-only research agents were dispatched as required by
speckit-plan. No installation, model download, corpus processing or live run occurred.
These are proposed technical decisions, not execution or legal approvals.

## R1 — Local model and locked runtime

**Decision**: Propose HuggingFaceTB/SmolLM2-360M-Instruct at immutable revision
`a10cc1512eabd3dde888204e902eca88bddb4951`, CPU FP32, through existing locked
Transformers5.18.0/Torch2.14.1+cpu in dedicated Linux Python3.12 packaging.
**Rationale**: Standard LlamaForCausalLM minimizes new dependencies. Native context
is8,192; application prompt2,048 plus completion384 is stricter. Compatibility,
JSON reliability, latency and quality are unmeasured and must pass actual live gates.
**Alternatives considered**: Larger instruct model (more resources); GGUF serving
(new runtime/lock); hosted provider (outside local-only scope). No fallback.
Sources: [model card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct),
[configuration](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct/blob/main/config.json),
[immutable revision](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct/commit/a10cc1512eabd3dde888204e902eca88bddb4951).
Upstream Apache2.0 metadata is research, not a repository license grant, rights
clearance or acquisition/redistribution approval.

## R2 — Grounding and full-question coverage

**Decision**: Closed-domain reviewed GroundingCatalog with exact unnormalized question
aliases and exact accepted claim renderings, selected by the user on 2026-10-03 via
"recommended" (Option A) in [Clarifications](spec.md#session-2026-10-03). Unseen aliases
abstain without generation even when evidence might answer them. This is a requirements
choice; detailed design/model/source/implementation/run approvals are not inferred.
**Rationale**: Citation identity or substring matching cannot establish full support;
conditions/negation can change meaning. Catalog reviewers bind complete claims and
question coverage to full current supporting spans. Runtime checks apply those
reviewed rules against the actual returned passages before accepting model output.
**Alternatives considered**: NLI classification adds no generation attempt but another
model and probabilistic entailment/contradiction errors; quotation alone omits relevance
and coverage. An unrestricted automatic semantic proof is not claimed.
Sources: [ALCE](https://arxiv.org/abs/2305.14627),
[TRUE](https://aclanthology.org/2022.naacl-main.287/),
[TrueTeacher](https://aclanthology.org/2023.emnlp-main.127/),
[negation/quantification limitations](https://aclanthology.org/2022.aacl-main.65/).
Catalog recommendation was an engineering inference and was selected by the user;
its runtime behavior and semantic quality have not been empirically validated here.

## R3 — Loading, bounded generation and JSON

**Decision**: Immutable read-only safetensors/config/tokenizer/generation assets;
SHA256 of every actually used file; local_files_only, trust_remote_code=False,
use_safetensors=True, token=False; offline flags set before imports. No custom code,
custom generation hooks, device_map auto, pickle weights or runtime acquisition.
Single batch, greedy do_sample=False/num_beams1; four intra-op threads/one inter-op.
**Rationale**: Existing runtime can provide a local adapter without new serving stack.
Slice completion tokens after prompt token length; parse exactly one strict JSON value,
reject duplicate keys/nonfinite values/trailing prose, never substring extraction or repair.
**Alternatives considered**: Prompt-only JSON trust, max_time as hard timeout, repair
calls and persistent workers; none supplies the required application boundary.
Sources: [offline mode](https://huggingface.co/docs/transformers/installation#offline-mode),
[loading API](https://huggingface.co/docs/transformers/main_classes/model),
[generation API](https://huggingface.co/docs/transformers/main_classes/text_generation),
[decoder-only generation](https://github.com/huggingface/transformers/blob/main/docs/source/en/llm_tutorial.md).
max_time may finish an active pass; parent supervision must enforce wall limits.

## R4 — Interface, lifecycle and approvals

**Decision**: Separate app.answer local JSONL session composing the planned F2 service
and unchanged F1 service in one owned readiness session. Preserve the F2 process-group,
framed IPC, original deadlines and independently verified cleanup contract. F3 adds
answer envelopes only, not changes to Stage1/F1/F2 entry points.
**Rationale**: Reopening loses readiness; leader death does not prove descendant stop.
**Alternatives considered**: New HTTP route, reopened collection, unsupervised model
load and detached worker; unnecessary scope or unsafe ownership.
Repository evidence: F2 CLI contract, F1 Dockerfile/Compose and source/tests.

## R5 — Concrete resource proposal and empirical gates

**Decision**: Total240 seconds; retrieval120; generation110 including cold load,
output transfer and reserved TERM2/KILL3; post-retrieval grounding/serialization10.
Prompt64KiB/2,048 generation tokens; completion384 tokens/16KiB; request/result/IPC
caps and8GiB aggregate runner ceiling specified in contracts. Keep256MiB index tmpfs.
**Rationale**: Concrete ceilings fail closed; no measured fit or latency promise.
**Alternatives considered**: Silent truncation, runtime enlargement and RSS polling
as hard enforcement; rejected. Linux cgroup memory enforcement is mandatory.
Host RAM probe was denied by sandbox; host capacity is unknown. Docker capacity and
locked model compatibility require authorized checks, not an assumed fit.

## Resolution ledger

Technical proposals are concrete. The catalog requirements boundary is resolved by
the recorded user clarification; changing to freer generation/NLI requires revising this plan,
contracts and resource/approval gates. Other pending items are actual implementation,
asset/source/retention/run approvals and empirical acceptance, never replaced by
schema-valid placeholders. No successful F2 or F3 live result is asserted.

## Analysis remediation decisions — 2026-10-03

The spec expresses the same closed-domain restriction as R2. The user selected
that requirements boundary on 2026-10-03; no detailed design/model/source/runtime
approval is inferred. Verified F2 gates real composition
and live acceptance; authorized deterministic F3 seams need not wait for it.
An internal retrieve_with_receipt port returns full represented-source bindings,
registry fingerprint and actual query dispatch count from the existing one-search
pipeline under the original clamped deadline. No public F2 envelope change/extra read.
Final stdout/forwarding requires bounded nonblocking readiness/write loops, not merely
IPC size limits; blocked consumer/broken pipe is fatal with independent owned cleanup.
Model-declared conflicting_evidence is invalid_model_response; the application alone
reports conflicts after reviewed current-source preflight. No extra model adjudication.

## Refresh scope — 2026-10-03

Reused prior primary-source research and immutable model proposal; no new model/version
recommendation or technical alternative was introduced by the clarification. A targeted
read-only research review checks selected-boundary consistency. Existing empirical
compatibility/capacity/JSON/grounding risks remain live acceptance gates, not claims
of successful research probes or approvals. No install/download/model/corpus run.
