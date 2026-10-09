# Optional RAM-backed GPU weight streaming

The default weight-placement mode is **GPU-only**. The optional streaming mode keeps a bounded cache of quantized weight bytes in system RAM and uploads nonresident row-aligned weight tiles as needed. Arithmetic still runs on the GPU. It is not CPU inference, shared VRAM, or a claim that all weights fit at once.

## Settings and budgets

- RAM weight-cache default: 0.5 GiB.
- Actual installed system RAM: blank/unknown until the user declares it. Streaming requires a truthful declaration; `navigator.deviceMemory` is not treated as an installed-RAM measurement.
- The managed host cache cannot exceed 75% of declared RAM. GPU configuration retains a maximum 75% policy for declared GPU capacity and the combined student/teacher guard.
- Changes require model reload. If weight bytes exceed the resident-GPU-plus-host-cache budgets, the UI warns that uncached bytes will be reread from the local model file and can be very slow.
- Browser/OS/driver memory, tokenizer metadata, temporary transfer/decompression buffers and other programs are additional. These managed limits do not guarantee the absence of an out-of-memory failure.

The current 20 GiB GPU + 32 GiB RAM profile gives at most 39 GiB of combined declared-policy capacity before additional reservations/overhead. It does not make the standard GPT-oss-120B weight set fit. That model has a separate future-hardware admission gate; enabling disk-backed streaming does not bypass it. Do not inflate either memory declaration to force admission.

## Implementation scope

The host cache reads immutable bounded file chunks, deduplicates pending misses, limits retained bytes plus reservations, evicts least-recently-used entries, and returns independent byte copies. Model release closes the cache and invalidates in-flight reads.

Dense Smol/Llama/Mistral, Gemma and Qwen text paths use the existing GPU math and preserved operation order with bounded row tiles for nonresident matrices. The separate GPT-oss backend retains its packed expert cache/tile policy and receives the shared host-byte cache at its reader boundary. LittleBit virtual weights are explicitly unsupported in this streaming mode. Direct F16TRI1 is a separate graph and gains no new capability from this setting.

Graph/KV/scratch, normalization vectors, safety headroom, resident matrices and a transfer tile must fit the GPU plan and actual binding limits. Model names or total declared memory cannot override a single-row or buffer-binding limit.

## Evidence and limits

Cache/policy/scheduler and composed-app tests cover exact bytes, reservations, immutable reads, evictions, concurrency, cancellation, failed/truncated reads, ordering, UI defaults and retained consent/budget guards. Native production WGSL tile cases on a CPU software adapter compare F32/F16/BF16/Q8_0 tiled versus resident matvec and an independent numeric reference. These are narrower tests than a complete large-model browser run.

Additional component evidence executes exact production dense/Gemma F32/Q8_0 graphs with fully/partially streamed weights: logits, final hidden state and KV are bit-identical to resident execution across three tokens and queued prefill. Separate GPT-oss cached/uncached checks cover six tokens, split/fused QKV, MXFP4, forced host/GPU eviction and complete GPU-buffer cleanup. Both use CPU Vulkan SwiftShader. Source-bound receipts are `patches/offload/production_native_receipt.json` and `gpt_host_native_receipt.json`. The final replay also passes against the accepted HTML in `qa/FINAL_OFFLOAD_NATIVE_RECEIPT.json`; full composed results are in [RELEASE_STATUS.md](RELEASE_STATUS.md). No real large checkpoint has been output-qualified with this streaming path; no physical Radeon, browser-GPU full-graph, sustained throughput or utilization result is claimed. Repeated file reads and transfers may dominate latency. Measure the actual workload before choosing streaming for everyday use.
