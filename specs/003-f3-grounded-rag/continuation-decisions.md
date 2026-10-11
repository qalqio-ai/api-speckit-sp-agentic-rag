# Current frozen evaluation result — 2026-10-05

EDM authorized the measured threshold/configuration/case freeze as a provisional
candidate and actual held-out/F3 evaluation; no numerical approval remains pending.
[Freeze](evaluation-freeze.json), [actual results and corrections](evaluation-results.md).
Retrieval4/5 (receipt-proof false negative); supported generation0/3
(output_too_large); both unsupported cases pass with zero generation.
Normal wrapper exit1; collection and owned stack absence verified. Candidate,
expected results and protected code preserved. Full live acceptance failed;
implementation completion is separate. Earlier pending-review statements below
are historical and superseded. No commits/publication/settings changes.

---

# Current approval and live evidence — 2026-10-04

EDM (`emcbee@alphaqidz.com`) confirmed owner/reviewer and approved the prepared
source/model/runtime proposals. [Session receipt](session-approval.json) records
that decision. Earlier pending-acquisition statements below are historical.
No source/model/local implementation or prior build/run permission is requested again.

| Decision/work | Current disposition and evidence |
| --- | --- |
| Sources | Four exact synthetic F2 proposal tuples approved for local F2/F3 use; [manifest](../../tests/fixtures/f3/approval.json), catalog and purpose receipts bind exact hashes. EDM owns/reviews; synthetic/non-sensitive, local operator/repository demo only, no external redistribution/license grant; owned run collection/stack deleted at demo end. Exact texts/hashes remain below. |
| Model | Existing approved MiniLM remains F1/F2 embedding-only. Approved SmolLM2-360M-Instruct pin `a10cc1512eabd3dde888204e902eca88bddb4951` supplies F3 generation; all six files, 725,784,865 bytes, acquired at the proposed local destination and checked against upstream identities plus separately computed local SHA256. [Acquisition receipt](acquisition-receipt.json) and immutable [manifest](generation-download-proposal.json). Offline CPU/Linux x86_64 Python3.12 Docker runtime on Intel Mac; Apache2 model-card evidence retained outside strict snapshot. Official Torch/Transformers compatibility was verified before the existing Docker installation; native environment unchanged. |
| Memory | 10 GiB is a planning estimate, not a measured physical minimum. Existing runner8GiB/Qdrant1GiB caps and Docker settings preserved. FP32 load15.93s, peak2.72GiB; calibration runner1.08GiB/Qdrant0.39GiB, queries8.13–8.27s. These separate probes do not establish concurrent generation peak or answer latency. No model substitution or cap change. [Runtime probes](live-runtime-probes.json), [calibration](live-calibration-report.json), [isolation](live-isolation-report.json). |
| Implementation/live acceptance | Integration/factory/wrapper/cleanup/evaluation wiring implemented; 389 deterministic tests pass. Genuine calibration and isolation/replacement/clear pass with owned collection/stack absence. Held-out retrieval, actual F3 generation, supported citations, abstention counts, full-stack peak/latency and live resource/timeout failure acceptance remain unrun. No mock or weight-load probe supplies live answer acceptance. |

Only the newly measured numeric separator and its frozen case/configuration bindings
remain for specific review: `min_score=0.45614706000000005`, calibration ID
`EDM-f2-20261004-v1`; minimum supported calibration score0.7199879 versus maximum
negative0.19230622. [Threshold proposal](threshold-proposal.json) binds the actual
report, source manifest, F2 fixed cases and F3 case proposal hashes. The unchanged
[F2 plan](../002-f2-retrieval/plan.md#verification-and-calibration) requires proposing
the measured separator and **“then obtain review”**. This value was unavailable at
the earlier approval. The specific question is pending; held-out/answer acceptance
has not run and no expectation was tuned from model outputs.

No Docker settings changes, native installation, commits, pushes or publication.

---

# F3 continuation decisions — 2026-10-04

This is a proposal and implementation report, not a source-use or acquisition
receipt. The latest user instruction authorizes deterministic work and prohibits
model downloads, unapproved source processing, Docker setting changes, commits
and publication. Existing governance and exact-alias answer scope are preserved.

## Sources: prefer the synthetic workshop corpus

Already approved F1 workshop documents are
`tests/fixtures/f1/original.txt` (learning-a/shared-guide/v1),
`tests/fixtures/f1/shorter.txt` (learning-a/shared-guide/v2), and
`tests/fixtures/f1/isolation.txt` (learning-b/shared-guide/v1). Exact bytes and
hashes are bound by `tests/fixtures/f1/approval.json`: owner/reviewer EDM,
2026-10-02 session approval, synthetic/non-sensitive, local demo operator,
local repository/demo only, no external redistribution or license grant,
owned run collection/stack deletion at demo end. Their approved purpose is F1.
Use these existing fixtures for deterministic boundary tests. They do not contain
return-policy facts or two competing source identities in one scope, so alone
they cannot establish the planned F2 retrieval/F3 answer acceptance.

The prepared [F2 T002 proposal](../002-f2-retrieval/tasks.md#t002-concrete-corpuscase-proposal--not-processed-or-approved)
extends that synthetic workshop, without real documents or private data. These
are exact UTF-8 strings with **no trailing newline**:

- `f2-synthetic/returns/v1`: `Synthetic returns: unused items may be returned within 7 days with a receipt.`
  SHA256 `50e85780308baf9945671e2c05be5ef4fa3e02ccd805babd2b6809ee52eb841d`.
- `f2-synthetic/hours/v1`: `Synthetic opening hours: the shop opens Monday through Friday from 9 am to 5 pm.`
  SHA256 `f19298916273b5ad01a43fdaa740eba1c37596049e59059f6141df6b69baa03d`.
- `f2-neighbor/returns/v1`: `Synthetic neighbor: unopened items may be returned within 3 days with an order number.`
  SHA256 `17a36a6f7e0ca4f4d90a57dc56feb5bf151e654fd57101989df5b0fe42037f18`.
- `f2-synthetic/returns/v2`: `Synthetic returns: unused items require a receipt.`
  SHA256 `42e29fd89ba570415acadc4555e6249e8d00c0a511e982f8abfea0bdc31ac324`.

Provenance: project-authored synthetic learning proposals recorded in the F2
ledger; no external policy authority, personal data or real shop policy is asserted.
Proposed owner/reviewer: **EDM**, continuing the existing workshop custodian/reviewer
attribution, subject to confirmation for these additions. This does not establish
the repository's unresolved legal rights holder.

Recommend reusing these exact proposed scopes/documents for both F2 and F3,
rather than introducing a second corpus under the earlier f3-synthetic proposal.
This requires explicit F2/F3-purpose approval and a reviewed matching catalog:
full current source coverage, complete return conditions, exact aliases/renderings,
neighbor isolation and separately reviewed replacement rules. Freeze calibration
and held-out expectations before testing; approve a measured threshold afterward.
Access: local demo operator only. Redistribution: local repository/demo only,
no upload, external redistribution or new license grant. Retention: temporary
owned index until demo end, verified deletion; safe metadata/claim checks only
in repository reports. No new source file, ingestion or approval receipt was made.

## Models: embeddings and generation are separate

Already available and approved for F1:
`sentence-transformers/all-MiniLM-L6-v2`, revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; upstream Apache-2.0 declaration in
the local pinned README. Its eleven hash-listed snapshot files occupy
**91,578,415 bytes**, observed by file-size inventory without model loading.
Location:
`/Users/edmcbee/Projects/api-speckit-sp-agentic-rag/local-data/f1-models/1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
F2 reuse needs its purpose/configuration approval. MiniLM creates 384-dimensional
document/query vectors; it cannot generate F3 text responses.

Proposed F3 decoder: `HuggingFaceTB/SmolLM2-360M-Instruct`, immutable revision
`a10cc1512eabd3dde888204e902eca88bddb4951`.
[Pinned upstream model card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct/blob/a10cc1512eabd3dde888204e902eca88bddb4951/README.md)
declares Apache-2.0 and documents CPU inference. Review its terms/notices before
acquisition; the pinned root tree has no separate LICENSE file. No repository
license or generation-asset approval is inferred from that declaration.

Public pinned Hub tree metadata, read using a bounded metadata-only HTTP GET,
reports: config.json 846 bytes; model.safetensors 723,674,912;
tokenizer.json 2,104,556; tokenizer_config.json 3,764;
special_tokens_map.json 655; generation_config.json 132.
The four required files total **725,784,078 bytes**; all six allowlisted runtime
files total **725,784,865 bytes (692.16 MiB)**. This excludes transport overhead,
README/license review metadata and unnecessary ONNX/training/vocab/merges files.
Source:
[pinned tree metadata](https://huggingface.co/api/models/HuggingFaceTB/SmolLM2-360M-Instruct/tree/a10cc1512eabd3dde888204e902eca88bddb4951).
No weights or tokenizer files were downloaded; no asset hash manifest was fabricated.

Proposed acquisition destination, not created:
`/Users/edmcbee/Projects/api-speckit-sp-agentic-rag/local-data/f3-models/a10cc1512eabd3dde888204e902eca88bddb4951`.
Mount read-only into /generation. Runtime: existing locked Linux x86_64 Python3.12,
Torch2.14.1+cpu, Transformers5.18.0; CPU FP32, greedy batch1/beams1,
four intraop/one interop threads, offline/local-only, no custom code.
This host reports x86_64: the reviewed Intel Mac arrangement is Linux Docker CPU,
not native macOS/MPS. Architecture and upstream CPU support are consistent;
the exact locked stack, tokenizer/EOS/template, latency, memory and held-out
answer quality are **not live-verified**. The decoder is required to demonstrate
one actual model-generated answer; a scripted catalog response cannot substitute.

## Docker memory: planning allocation, not measured minimum

The unchanged Compose ceilings are runner **8 GiB**, Qdrant **1 GiB**, plus
approximately **1 GiB VM/daemon headroom**, yielding the recommended **10 GiB**
Docker allocation. The runner limit covers Python/Torch/tokenizers, embedding
and generation workers, FP32 weights, activations/KV cache and descendants.
Runner 64 MiB tmpfs is inside its 8 GiB; Qdrant 256 MiB index tmpfs is inside
its 1 GiB. Do not add those mounts again. Four CPUs are a separate ceiling.
No observed peak-memory measurement establishes 10 GiB as a physical minimum.
The previous "needs at least10GiB" wording was too strong and is corrected here.

Last recorded capacity: host64GiB; Docker4,101,435,392 bytes (~3.82GiB)/16CPUs.
This is below the combined container ceilings; it does not prove the selected
workload cannot fit. Peak usage and latency must be measured after acquisition.
No Desktop settings or reviewed limits were changed. Authorized image builds and
a source-free Linux runtime import check succeeded; no generation weights loaded.

A 135M decoder would reduce approximate FP32 parameter storage from
360M×4 (~1.34GiB) to135M×4 (~0.50GiB), excluding all other allocations.
The [model family](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct/blob/a10cc1512eabd3dde888204e902eca88bddb4951/README.md)
includes that size, but **no exact alternative revision/runtime configuration is
approved and no evidence shows it satisfies the F3 acceptance cases**. Changing
model/caps needs a reviewed design/configuration change and real quality/deadline
tests. Sequential cold loads or another authorized Linux x86_64 Docker host might
reduce local peak pressure or avoid Desktop changes while retaining criteria;
the implementation already sequences fresh embedding/generation workers, but its
live peak is unmeasured. No hosted inference or automatic fallback is proposed.

## Implementation and live verification are separate

Implemented F3-owned runtime.py connects the unchanged F1 Service/Index and F2
retrieval pipeline to fresh supervised embedding/storage workers. Live factory
checks actual kernel memory/swap/CPU, purpose receipts, file/configuration hashes,
read-only snapshots and tokenizer readiness before READY or input. LocalGenerator
loads generation weights only inside a fresh owned worker, with actual invocation
controls. All workers share the factory group/cgroup. Parent records kernel
identities independently and verifies original workers gone, without signaling
reused PIDs. Native fixtures cannot establish actual Linux enforcement.

Executable demo.py/scripts/f3-demo.sh creates only a unique owned stack from
existing image IDs; verifies mounted paths, internal network/storage DNS alias,
resource/image identities and actual tmpfs; forwards complete records with private
remaining-time metadata and delivery acknowledgments. Parsed delegated ceilings
reach the hard supervisor. First teardown is immutable across signals/forwarding
failures; worker/group stop, collection cleanup and exact-ID Docker removal/absence
checks remain bounded inside original45 seconds. Unknown absence is nonzero.
No runtime installation, model acquisition, pull, build or global prune occurs.

Optional evaluation mount/CLI/factory wiring is implemented. After successful
approved ingest-only input and EOF, frozen cases use separate case deadline
signals and one ordinary answer each in the same session. No stdin replay or
expectations in model context. Source/catalog/assets/model/retrieval/case hashes
are checked before model/query use; mismatch never edits reviewed expectations.
Runner and Qdrant cgroup peak counters and completed transport latency are wired
for measurement, not reported as observed before an authorized live run.

Remaining live gates: source additions/F2/F3 purpose and EDM ownership/review;
MiniLM F2 purpose reuse; exact catalog claims/spans/aliases and frozen calibration
and held-out cases; generation acquisition/verified hashes/license notices;
measured reviewed F2 threshold; model/template/EOS/JSON behavior and semantic
answers/abstentions; actual cgroup/OOM/descendant/mount/residue and deadline tests.
Current Desktop allocation is below the reviewed aggregate container caps. A
Docker allocation change or another host requires its own decision. Local
implementation/build/run permission persists and needs no renewed generic approval.

### Resource-control trace

| Criteria | Implemented control | Verification boundary |
| --- | --- | --- |
| FR-012, SC-006 | Original240 request; F2 120; delegated inspect/clear10; startup120; hard parent deadlines and remaining-time host IPC | Clock/stall/private-case/native process fixtures pass; actual live latency pending |
| FR-013, SC-004/005 | Bounded lines/frames/output; actual worker search/generation dispatch counters; fatal transport stops input | Deterministic malformed/broken/stalled-output/count fixtures; live JSON/model quality pending |
| FR-012/015, SC-006/007 | First45 teardown; per-request workers already reaped, collection10 then final group5 and Docker30 within45; independent identity and absence checks | Native/fake-resource probes; Linux/Docker collection/escaped-worker/OOM residue pending |
| FR-014/018, SC-008 | Exact existing lock/images, CPU offline local-only safetensors; eight GiB runner/four CPUs/no swap and one GiB Qdrant/256 MiB index tmpfs | Official wheel availability/declared compatibility verified; actual kernel/runtime acceptance pending |

### Official runtime compatibility, checked before installation

Existing unchanged requirements.f1.lock pins Torch2.14.1+cpu and Transformers5.18.0.
The official [PyTorch CPU wheel index](https://download.pytorch.org/whl/cpu/torch/)
lists torch-2.14.1+cpu-cp312-cp312-manylinux_2_28_x86_64.whl: CPython3.12,
Linux x86_64, glibc2.28+. This is the Linux Docker path on Intel Mac, not native
macOS/Python3.10. The selected CPU wheel is not an Intel macOS wheel.
[Transformers5.18.0 release metadata](https://pypi.org/project/transformers/5.18.0/)
requires Python>=3.10 and supplies a universal py3-none-any wheel. Its official
SHA256 d79e5a515a572ee3deb33eb0d578be47d91e70c75d54cf21bf6eede6edef14a9
matches the protected lock. The [official installation guide](https://huggingface.co/docs/transformers/installation)
declares Python3.10+/PyTorch2.5+ compatibility. This verifies published compatibility
and target-wheel availability, not observed selected-model behavior or performance.

Exact generation acquisition URLs/files/bytes/upstream Git-blob SHA1 or LFS SHA256
are in [the download proposal](generation-download-proposal.json). Computed local
SHA256 fields remain null until authorized download and independent verification.
All four exact synthetic strings/hashes and access/redistribution/deletion rules
are above; owner/reviewer EDM and acquisition questions await actual user answers.
