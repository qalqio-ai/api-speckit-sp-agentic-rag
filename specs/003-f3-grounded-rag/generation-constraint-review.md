# Prompt delivery audit and isolated generation constraint proposal

Review only. Prompt iteration remains stopped. No new answer generation or acceptance run was performed. All prior failed artifacts, frozen configurations and protected implementation remain unchanged.

## Delivery evidence and limits

The audit recomputed immutable proposal-file and system-text hashes against retained worker diagnostics and checked mounted input copies byte for byte. Full hashes are in `prompt-delivery-audit.json`.

| Worker evidence | v2 parser replay | v3 experiment |
|---|---:|---:|
| Proposal SHA-256 prefix | 5c092694cc39 | f8fbe683196b |
| System-text SHA-256 prefix | c4aa4bb69891 | 39c6a894170f |
| Rendered prompt tokens | 630 | 684 |
| Rendered prompt UTF-8 bytes | 1,642 | 1,894 |
| Output tokens / new tokens | 673 / 43 | 727 / 43 |

Both user-context hashes are `3e6e8c29f78de7171b365eafdd08a7bf4ab364a30829f4ad3ec04192f8e02fac`. The original production system hash is unchanged. Retained helpers read their distinct mounted proposal filenames, assert the system-text hash, replace the system message, call the actual tokenizer chat template, measure the rendered string, tokenize it, and call the actual inner model.generate with those inputs.

This supports delivery of different prompts; it is not a cryptographic historical attestation of the final rendered bytes or token IDs, which were not retained. Current helper-source inspection cannot establish its historical source identity. Identical completion bytes alone establish neither stale configuration nor a cached response. Current code inspection found fresh exec workers, local-only weights, unique private channels and no response-cache lookup; normal per-call attention KV caching is a different mechanism. No affirmative evidence of stale prompt delivery or response caching was found; retrospective gaps remain.

## One proposal: bounded token-trie generation

Use the current SmolLM2-360M-Instruct revision `a10cc1512eabd3dde888204e902eca88bddb4951`, unchanged v3 prompt, and existing Torch 2.14.1+cpu / Transformers 5.18.0 on Linux x86_64, Python 3.12.15, glibc 2.41. Add no package. The installed `_get_logits_processor` incorporates `PrefixConstrainedLogitsProcessor` when `prefix_allowed_tokens_fn` is supplied. See the [upstream versioned implementation](https://github.com/huggingface/transformers/blob/v5.18.0/src/transformers/generation/utils.py) and the actual installed-code probe report, which records the source hash and CPU masking tests.

This is a controlled selection design, stronger than a generic JSON grammar. For this isolated query only, compile two complete canonical JSON paths: one eligible exact reviewed claim with its actual supporting chunk ID, and the existing `insufficient_evidence` response. The model still performs one real autoregressive generate call and chooses among permitted next tokens; all forbidden logits become negative infinity before token selection. Structure, reviewed wording and citation IDs are constrained during generation. We do not insert them into a completed answer. This experiment would test catalog selection and contract compliance, not free-form reasoning or general F3 acceptance.

Select the answered path using the unchanged `eligible` catalog/scope/source fingerprint checks and the unchanged `validate_claims`. Require exactly one eligible claim and exactly one returned chunk which independently supports every required span, matching source ID, revision, content hash, offsets and exact quote. Enumerate actual retrieved IDs, validate each one-chunk candidate with the existing validator, and reject ambiguity before generation. Never import IDs from expected regression results. Multiple claims, multiple support candidates, missing support or scope drift stop this narrow experiment; they do not trigger fallback generation.

Serialize both schema-validated paths with `json.dumps(..., ensure_ascii=False, separators=(',',':'))`, tokenize without added special tokens, and append the current configured EOS. Require exact decode round trips and existing token/byte limits before generation. Build a token-ID trie. The callback strips the actual input prompt length, traverses only newly generated IDs and returns precisely the next trie edges. EOS is allowed only after a complete JSON path. An unknown prefix or empty edge set fails closed; no early EOS or repair. After generation, use the existing prompt slicing, strict JSON parser, ModelResponse schema and claim validator on actual raw output without modification. A schema-valid abstention still fails the known supported-query expectation.

## Exact isolated changes proposed for review

Create only the four ignored local-data helpers listed in `generation-constraint-v1-proposal.json`. Do not modify production app files, schemas, catalog, prompt files, evaluation expectations, dependencies, locks, spec, plan or resource settings.

1. `constraint-v1-trie.py`: bounded path compiler and callback; reuse unchanged validators; cap two paths, 768 token edges and 1 MiB accounted trie storage. Record all path hashes and measured size; abort if limits fail.
2. `constraint-v1-worker.py`: fork the retained v3 diagnostic worker into a new file. In its real Model.generate wrapper, compile the trie from the captured user context's rules/evidence, after host binding to the unchanged eligible catalog result. Do not treat arbitrary context rules as approved catalog. Validate the full context/catalog binding before generate. Add exactly one generation kwarg:

   ```python
   prompt_length = kw['input_ids'].shape[-1]
   kw['prefix_allowed_tokens_fn'] = trie.callback(prompt_length)
   out = self.inner.generate(**kw)
   ```

   Existing model, kwargs, decoding and validators stay unchanged. Include compilation/callback time within the original deadline. Record worker nonce/PID, helper-source hashes, immutable prompt-file/system hashes, chat-template hash, rendered-input hash, input-token-ID hash, context hash and trie/path hashes immediately before generate, then bind raw-output hash to the same nonce before terminal response. Use deterministic integer-array serialization for token-ID hashes. Keep stdout solely on its existing response protocol and bounded diagnostics separate.
3. `constraint-v1-single.py`: use only the same exposed `edm-answer-1` regression, same frozen retrieval configuration and current actual evidence. Use fresh owned stack and fresh diagnostics; abort on any hash or nonce mismatch. No retries, fresh acceptance or automatic follow-up. Report unchanged expected answer, raw output, exact schema/claim/citation results, stopping reason, token count, compilation/retrieval/generation/total latency, cgroup peaks and collection/worker/stack absence.
4. `test-constraint-v1.py`: run focused tests before the single experiment. These are proposed tests, not completed tests.

## Required rejection tests

- High-scoring unknown/foreign/stale chunk-ID token sequences cannot leave the trie; premature EOS, omitted chunk_ids, source wording instead of reviewed wording, extra fields and trailing text cannot complete an allowed path.
- Compiler refuses a current but irrelevant chunk, incorrect quote/span, stale revision/hash, wrong scope, duplicate/ambiguous support and multiple claims.
- Feed schema-valid responses with a fabricated ID, valid-but-unsupported ID, changed text or unrelated extra citation directly to unchanged validate_claims; require its existing errors. Constraint success cannot bypass semantic checks.
- Token prefix is based on new tokens only; nonterminal EOS and unsatisfiable prefixes fail. Canonical round trip, path length/byte limits, trie storage limit and remaining deadline fail closed.
- Integration uses genuine model.generate once; no scripted completion, retry, response rewrite or automatic citation attachment. Supported-query abstention remains a failed regression. Existing resource and owned-process cleanup tests remain mandatory.

## Resource evidence and gates

The source-free probe loaded tokenizer/config only, no model weights, and executed no answer generation. Installed greedy-mask tests passed; an empty allowed set raised ValueError. Actual tokenizer lengths were 80 tokens including EOS / 190 bytes for the historical one-chunk answered path, and 23 tokens / 78 bytes for abstention; the experiment must recompute using its actual evidence. Vocabulary size is 49,152, so one float32 logit mask is 196,608 bytes. Probe cgroup peak was 1,469,505,536 bytes, which excludes weights and must not be presented as answer-generation peak memory.

Keep completion 384 tokens/16,384 bytes, prompt 2,048 tokens/65,536 bytes, context 8,192, generation 110 seconds, request 240 seconds, cleanup 45 seconds, runner 8 GiB and Qdrant 1 GiB. Trie/mask overhead appears modest relative to the prior measured generation runner peak of 3,092,299,776 bytes; this is a feasibility estimate. No full-model constrained latency, peak memory or cleanup result exists yet. Preflight measures bounded compilation, then the single reviewed experiment measures all live budgets. Do not increase limits on failure.

An initial image inspection failed and an explicit network-disabled build failed at the dependency layer. No downloads occurred. Subsequent inventory exposed the existing image `139a1f015734`; the successful source-free probe ran it with `--pull=never`, network none, read-only mounts, 8 GiB hard memory/no extra swap, four CPUs, 64 MiB tmpfs, and automatic container removal. No alternative model acquisition is proposed because the existing runtime mechanism is feasible for this narrow test.

Remaining decision: review and approve this generation-design change for the single isolated regression experiment. Existing source/model/build/run approvals persist. No new acquisition is required or authorized by this proposal. Approval would not authorize prompt iteration, general rollout or fresh acceptance claims.
