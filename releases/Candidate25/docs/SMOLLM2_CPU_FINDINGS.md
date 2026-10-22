# SmolLM2 real-model CPU profiling, 22 October 2026

## What actually ran

Nexus AI Candidate24 ran as a real localhost HTTP application on the cloud Linux host. Its own resident Nexus.cpp CPU engine loaded SmolLM2-135M-Instruct Q8_0, imported through the app's existing model route, returned chat-ready, and streamed actual generated text. This was not a mock, training throughput measurement, or llama.cpp replacement.

The verified GGUF conversion is exactly 144,811,360 bytes. SHA256: `5a1395716f7913741cc51d98581b9b1228d80987a9f7d3664106742eb06bba83`. The initial truncated download was rejected by existing range validation and replaced before successful inference.

## Bounded change

- Specialize F32 and Q8_0 row reads so the CPU inner loop does not repeatedly call Tensor::at and switch storage format for every scalar weight. Loading-time shape/range validation remains unchanged.
- Compute output vocabulary logits only for the last prefill token. All prompt tokens still execute transformer layers and populate the same K/V state.
- Keep sequential FP32 accumulation, sampling, tokenizer, embedded chat template, per-request reset, model identity, cancellation and Python/UI state unchanged.

No approximation, model requantization, persistent cross-chat cache or extra CPU fallback was added. Intermediate output-only overflow checks are naturally not performed for vocabulary projections that are no longer computed; returned final logits still undergo the existing finite check.

## Single-sample diagnostic results

Same model, 18 prompt tokens and 8 generated tokens, context 512, CPU threads 1, greedy temperature 0 and seed 123. Matched GCC 14.2 builds used `-O3 -std=c++17 -fopenmp`.

| Metric | Before | After |
|---|---:|---:|
| App readiness |0.317s|2.937s|
| Model import |5.241s|5.415s|
| New native process/model load |6.669s|2.566s|
| First visible text after chat submission |187.022s|41.657s|
| Total chat request |223.166s|73.157s|
| Native prefill |186.406s|41.210s|
| Native decode,7 forward calls |36.058s|31.510s|
| Native decode forward calls/second |0.194|0.222|

Both generated exactly `[504,3575,282,4649,314,7042,30,7042]`, decoded as “The capital of France is Paris. Paris”. The 8-token cap ended the sample; this is not a general response-quality evaluation.

These are diagnostic observations, not a reliable speedup multiplier. The shared host varied strongly, including startup timing and a separate longer-prompt sample. Three repeats were initially planned, but only one complete before/after pair is reported; interrupted extra requests are excluded. The tested engine remains a slow CPU correctness-oriented implementation, not production-class optimized inference. “Cold load” here means a new app/native process, not a flushed OS page cache.

## Validation

- 26 comparisons across 13 GGUF storage formats: original versus optimized full logits and generated tokens exactly equal on synthetic fixtures.
- Real pretrained SmolLM2 generated token IDs/text exactly equal for the paired request. No full real-model-logit or llama.cpp parity claim.
- Added independent NumPy-oracle tests for F32/Q8_0, one/multiple prompt tokens, zero/four generated tokens.
- Added C ABI tests for empty prefill, exact-context fill, subsequent exhaustion, unchanged returned logits and reset.
- Fresh native CLI and C ABI suite: 71 tests run, 70 passed and one optional official-vocabulary test skipped because its asset environment variable was not set. That same skipped test was then run separately with the existing pinned official Tekken asset and passed (1 test, 3.040 seconds). All 71 test cases therefore have passing evidence across those two runs. Logs and final handoff metadata are supplied.

## Deployment and limits

Only source and test evidence are provided. A Windows native rebuild is required before an installed Windows engine gets this optimization. No Linux binary or model weights belong in the distribution overlay.

The default Python CPU build helper does not enable OpenMP, unlike CMake's optional OpenMP path. The benchmark's thread control applies to the explicitly OpenMP-enabled matched binaries; it does not qualify default installer builds or authorize changing global compilers/runtimes.

The host reports Intel Xeon Platinum 8573C, Linux 6.18.55 x86_64. No Radeon HIP, WebGPU, Windows runtime, GPU VRAM budget, Mistral7B compatibility or GPU performance was tested or changed by this patch.
