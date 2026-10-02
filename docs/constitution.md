# Project Constitution

Version: 1.0.0  
Status: Sole project constitution restored under the user's governance reconciliation
authorization on 2026-10-02; official Spec Kit adoption pending.

The original ten principles below are preserved verbatim from the supplied starter.
Existing `.specify/feature.json` and feature documents do not establish an active
Spec Kit constitution. Do not create hand-written `.specify` internals. After an
authorized official adoption, merge these principles into its active constitution
and replace this document with a pointer in the same change. Never maintain two
active constitutions.

## 1. User intent before implementation
Turn requests into explicit outcomes. Resolve ambiguity that changes scope, data access, cost, or user impact before building.

## 2. Evidence before answers
Ground factual RAG responses in approved sources. Preserve source identity and location metadata. If evidence is absent, conflicting, stale, or insufficient, say so and ask a bounded follow-up or request human review.

## 3. Retrieved content is untrusted
Documents, web pages, tool output, and user files can contain incorrect or malicious instructions. Retrieval content informs an answer but cannot override system or project policy.

## 4. Humans retain consequential authority
Agents may summarize, recommend, and prepare reversible work. A human approves actions that change access, publish content, commit funds, affect eligibility, or make other consequential decisions.

## 5. Least privilege and data minimization
Give each component only the data and permissions it needs. Use synthetic data for the workshop. Define retention and deletion before persisting user content, embeddings, traces, or memory.

## 6. Memory is explicit
Distinguish session context, persistent user memory, and the document index. Specify what is stored, why, for how long, who can retrieve it, and how it can be corrected or removed.

## 7. Behavior must be testable
Define acceptance criteria. Evaluate retrieval relevance, groundedness, citation correctness, abstention, and tool-use boundaries.

## 8. Prefer simple, inspectable systems
Start small. Add agents, memory, vector storage, reranking, or orchestration only when a requirement and evaluation show their value.

## 9. Observe without over-collecting
Record only telemetry needed to diagnose quality, latency, failures, and cost. Do not log secrets or unnecessary personal content. Document retention and access.

## 10. Keep changes reviewable
Connect request, spec, implementation, and verification. Explain trade-offs and make uncertainty visible.

## Change process
Propose constitution changes in a pull request with rationale, affected principles, migration impact, and version change. Maintainers approve changes. Agents must not amend this constitution as a side effect of feature work.
