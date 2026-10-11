# Approved v2 prompt diagnostic experiment

EDM approved exactly generation-prompt-v2-proposal.json for one known supported
regression query; follow-up exposed regressions conditional on success. This is
not F3 acceptance and does not promote the proposed prompt to production.

[Separate run configuration](prompt-v2-experiment-configuration.json),
[actual safe report](prompt-v2-single-report.json).

- Proposal file SHA256:5c092694cc39e4fa3b187669bcadd7fd154d2cb0e25497e6cb383dfd41788d49.
- Proposed system text SHA256:c4aa4bb69891335828aa2188911460b9e84cd1c1205b3cb0ed3a8dedc0c873f9.
- Experiment fingerprint:a833b8e47983fba6e827c68e595af6377034d92f25052d5ede097853d2385f0a.
- Original system text SHA256:855fbb8ea2364c7e54cfe0baa66b43cad5aa44e6498ce7d1c7c7736207931572.
- Real question/rules/evidence context SHA256:3e6e8c29f78de7171b365eafdd08a7bf4ab364a30829f4ad3ec04192f8e02fac.

Only the system-message text at the temporary tokenizer diagnostic boundary was
replaced with the approved proposal. The original user context, chat template,
model/revision/files, generic query embedding, threshold, corpus/catalog/case
expectations, CPU FP32 greedy beams1/batch1, EOS2/pad2, limits and real schema/
grounding/citation validators remained unchanged. The production prompt, source
code and frozen failed evaluation were preserved. Baseline generation fingerprint
is not a claim that this experiment uses the original prompt; the separate prompt
hash and experiment fingerprint above distinguish the changed system message.

| Check | Observed |
| --- | --- |
| Case |edm-answer-1, known exposed supported regression |
| Outcome |failed / invalid_model_response |
| Stop |configured EOS2, at new-token index42 |
| Tokens |630prompt +43new =673total; cap384new unchanged |
| Bytes |1,642prompt;157generated;51serialized error JSON payload |
| Schema |invalid; safe telemetry does not distinguish JSON parsing from shape failure |
| Grounding / citation correctness |unverified; no valid response reached claim validation |
| Exposed claims/citations |0 /0; no partial answer |
| Actual searches / generations |1 /1; no retry/repair |
| Actual model.generate |7.752s |
| Generation cold load |10.604s |
| Retrieval / generation stage / total |8.792s /18.613s /27.407s |
| Runner / Qdrant peaks |3,068,592,128bytes /412,012,544bytes |
| Collection / owned stack absence |verified /verified |
| Worker Python stdout |0bytes; private socket response independent of logs |

EOS termination improved versus the original cap exhaustion, but the approved
success requirement was not met. This hypothesis did not resolve valid grounded
answer generation. Other exposed regressions and fresh acceptance cases were not
run because follow-up authorization was conditional on success. Threshold0.45614706000000005
and calibrationEDM-f2-20261004-v1 unchanged; no tuning. No new acceptance claims.

Actual commands:cached pinned F3 build plus diagnostic runner exit0; exit0 means
measurement/cleanup completion, not quality success (`all_cases_pass=false`).
Image139a1f015734889f0bef40f66a4db65a1addc1a3dc5dc41f6bc82fe9d936757f
unchanged. Focused EOS tests2pass/47deselected, existing native environment, exit0;
Ruff/diffcheck exit0. No full local gate repeated for this experiment because
production and tests were unchanged; the prior gate record remains historical.
All133 existing app/test/docs/spec files retain before-experiment SHA256, including
original proposal, failed evaluation, cases and frozen configuration. Only new
experiment configuration/report/narrative records and ignored temporary helpers
were created. No production fix/prompt promotion, model/dependency downloads,
Docker settings, commits/pushes/publication. No raw model text retained.
