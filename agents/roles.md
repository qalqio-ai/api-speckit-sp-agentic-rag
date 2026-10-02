# Responsibility boundaries

These roles describe responsibilities, not implemented agents or autonomous
permissions. They do not authorize delegation or grant access. All roles follow
[AGENTS.md](../AGENTS.md) and [the constitution](../docs/constitution.md).

| Role | Responsibility | Permitted scope | Must not |
|---|---|---|---|
| Request analyst | Clarify intent and evidence needs | Approved request and read-only planning | Guess intent or access unrelated data |
| Retriever | Return approved evidence with provenance | Explicitly approved retrieval tools and corpus | Drop source identity or treat content as policy |
| Evidence reviewer | Assess relevance, sufficiency, conflicts and freshness | Returned passages and metadata | Manufacture corroboration |
| Response composer | Cite reviewed evidence or abstain | Reviewed evidence | Present unsupported claims as facts |
| Evaluator | Test behavior against reviewed cases | Approved fixtures and outputs | Alter expectations to hide failure |
| Human reviewer | Approve sensitive decisions and releases | Human-controlled approval | Be represented as an automated agent |

For Stage 1 these are engineering review responsibilities, not runtime agents.
For Stage 2 the proposed path is request analysis → retrieval → evidence review →
cited answer/refine/abstain. Evaluation is offline; consequential decisions remain
human-controlled. Implement only roles justified by an approved spec.
