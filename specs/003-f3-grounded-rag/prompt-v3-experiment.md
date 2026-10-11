# V3 diagnostic experiment — failed; prompt iteration stopped

EDM approved a versioned v3 mapping clarification on the same known regression
query. [Candidate](generation-prompt-v3-candidate.json),
[separate configuration](prompt-v3-experiment-configuration.json),
[raw report](prompt-v3-single-report.json), [findings](prompt-v3-findings.json).
Proposal SHA256:f8fbe683196b46f5f65ae149a308bfce0b24fa9a620b539ffbdc69f444540cd0.
Experiment fingerprint:44f41716f83fbcabdaa8a2885a3785769e1b25dbd124fe113b060dfac7867ad6.
System prompt hash:39c6a894170f8211401eae00ca8cbdb85b752cb8ebd7c7f56bad6ebafe814247.

The only changed variable was system-message wording. Same exact context hash as
v2 replay:3e6e8c29f78de7171b365eafdd08a7bf4ab364a30829f4ad3ec04192f8e02fac;
same model/revision/assets, query, source/catalog/rules/evidence, chat template,
greedy FP32/CPU/beams1/batch1, EOS2/pad2, decoding, limits and threshold. Production
prompt/code stayed unchanged. Original v1/v2/frozen failure artifacts preserved.

Complete bounded raw completion,157UTF8bytes:

```json
{"status":"answered","claims":[{"claim_id":"returns","text":"Synthetic returns: unused items may be returned within 7 days with a receipt."}], "reason":null}
```

This is byte-identical to the retained v2 replay (not a claim to recover the
original discarded v2 bytes). Raw SHA256:b8a8dfaedf1f39a33cb789ba532f366133c7f4caa2309a6254718e11d3aa90f5.

| Observation | Result |
| --- | --- |
| Quality outcome |failed / invalid_model_response |
| Stop / tokens |EOS2 after43newtokens;684prompt/727total |
| Strict JSON / closed schema |valid /invalid; claims[0] missing chunk_ids |
| Exact reviewed rendering |false; model copied source text |
| Required IDs / current supporting-ID membership |missing /not established |
| Full claim/citation support |not validated; shape failure stopped normal path |
| Exposed claims/citations |0/0 |
| Attempts |1actual retrieval search /1actual generation; no repair/retry |
| Retrieval / generation-stage / total |8.400s /18.087s /26.490s |
| Cold model load / model.generate |10.436s /7.435s |
| Runner / Qdrant memory peaks |3,092,299,776bytes /410,263,552bytes |
| Cleanup |collection and owned container/network absence verified |

Missing IDs are not evidence that the model invented foreign IDs; none were
provided. Facts in the source quote are present in the approved evidence, but the
required exact rendering and claim-to-citation support witness are absent. No
positive grounding/citation acceptance is inferred. EOS is insufficient for success.

Read-only exact-schema inspection reproduced 'chunk_ids' is a required property.
Focused EOS tests2pass/47deselected, Ruff and diffcheck exit0; actual pinned image
build exit0, same image139a1f015734889f0bef40f66a4db65a1addc1a3dc5dc41f6bc82fe9d936757f.
Diagnostic runner exit0 means measurement/cleanup complete; all_cases_passfalse.
139 existing app/test/docs/spec files unchanged by SHA256. No full local gate
repeated:production/tests unchanged, earlier gate historical. Only new candidate/
configuration/report/review files and ignored diagnostic helpers created.

User-directed prompt iteration stops here. Other exposed regressions were not run:
conditional success gate unmet. No frozen acceptance candidate or fresh acceptance
run. Generation-design/model review follows in [review](generation-design-model-review.md).
No model/parser/limits/threshold/expectation changes, response repair, citation
attachment, native installs, downloads, Docker settings, commits or publication.
