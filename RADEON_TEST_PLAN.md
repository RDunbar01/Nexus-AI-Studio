# RX 7900 XT qualification and performance plan

Target: the user's Radeon RX 7900 XT, reported as 20 GB. This is a procedure, not a completed benchmark. Browser, driver, GPU and full-model tests remain unperformed until their actual receipts are filled in.

## 1. Identify the exact run

Record the HTML SHA-256, expression-worker/asset hashes, model full SHA-256 and byte size, source revision, GGUF producer, architecture, tensor-type inventory, tokenizer/chat format, selected backend and runtime settings. Record OS, browser/build, driver, CPU/RAM, adapter identification, adapter/device limits, context allocation and whether any teacher, adapter or expression model is loaded.

Use the same actual model file, rendered prompt and token IDs for every A/B comparison. Match BOS/EOS handling, sampler/seed and maximum output tokens. Disable learned adapters, retrieval/personalization and expression analysis for the baseline; record any unavoidable difference. A reconstructed or differently quantized model is a separate test case.

## 2. Safe local setup

- Export a workspace backup. Use one app tab and a dedicated localhost-served directory; do not disable browser security or enable experimental flags to force a pass.
- Check that the selected adapter is the intended Radeon and not a software fallback. High-performance power preference is a selection hint, not proof of which adapter the browser chose. [GPU.requestAdapter documentation](https://developer.mozilla.org/en-US/docs/Web/API/GPU/requestAdapter)
- Enter the driver-reported VRAM capacity in GiB, matching the UI units. “20 GB” in a product name alone is not an automatic WebGPU memory reading. Keep the application's conservative headroom; other apps, browser overhead and expression models also consume memory.
- Save actual `maxBufferSize`, `maxStorageBufferBindingSize`, dispatch/workgroup limits and device features. Browser-exposed limits can be tiered and may differ from physical hardware limits; sufficient aggregate VRAM does not make an oversized individual binding valid. [GPUSupportedLimits documentation](https://developer.mozilla.org/en-US/docs/Web/API/GPUSupportedLimits)
- A requested device must actually expose the limits/features required by the graph. Treat adapter selection, device creation, shader compilation and model load as distinct stages. [GPUAdapter.requestDevice documentation](https://developer.mozilla.org/en-US/docs/Web/API/GPUAdapter/requestDevice)
- Do not overclock, increase voltage or run other GPU-heavy tasks. Stop on device loss, validation errors, nonfinite logits, runaway allocations or driver thermal warnings. Never substitute “the page stayed open” for a pass.

## 3. Admit and check correctness before speed

Begin with an ordinary SmolLM2-135M-Instruct GGUF in a supported representation. Then cover all twelve Smol family/size/variant combinations: SmolLM and SmolLM2, 135M/360M/1.7B, base/Instruct. Track each actual quantization separately; do not mark missing files passed. Base models use explicit plain completion. Keep custom LittleBit and pinned experimental direct compression in separate rows.

For newly integrated Gemma, GPT-oss, Mistral and Qwen-VL paths, require the component and integration evidence in [CAPABILITIES.md](CAPABILITIES.md) first. Qwen-VL image tests need the exact matching projector and preprocessing; a text-only pass is insufficient. Never try GPT-oss-120B fully resident on this 20 GB GPU / 32 GB RAM machine merely because its graph becomes available.

For each admitted file:

1. Inspect metadata, dimensions, tensor coverage, tokenizer, formatted prompt and allocated context. Require an explicit rejection for unknown graphs/tensors/templates rather than a guessed fallback.
2. Compare tokenizer IDs and fixed-prefix logits/greedy output with a trusted runtime using the same file and prompt. Record the reference runtime version, absolute/relative differences, top-1 agreement and termination behavior. Predetermine the comparison criterion; do not select a tolerance after seeing the result. Bitwise source restoration and numerical inference parity are different tests.
3. Test single-turn, multi-turn, Unicode, empty/short input, near-context-limit input and prompt-plus-reply overflow. A tokenized prefix must not silently wrap or discard newer user text.
4. Check cancellation, second-run retry, New conversation, model unload/reload and exit while work is pending. No late token, old observation or released buffer may reappear in the new session.

A model-health check and a coherent short answer are smoke tests; neither establishes factual accuracy or whole-model parity.

## 4. Measure useful performance

Use one cold load measurement, two untimed warm-ups and at least five timed repetitions per case. Report individual samples and median/range. Alternate baseline/candidate order to reduce warm-cache and thermal bias. Keep the foreground tab, rendering settings and machine load consistent. Separate load/compile time from inference.

Use a short prompt and longer prompts targeting roughly 128, 512 and 2048 model tokens where the allocated context permits, reserving room for the requested answer. Record the exact resulting token counts. Request a fixed answer budget such as 128 tokens, but calculate throughput from tokens actually generated; EOS can end early. Do not use a 2048-token prompt in the experimental 128-token path.

Record these separate quantities:

| Metric | Measurement boundary |
| --- | --- |
| Load-ready latency | File selection/start to fully ready, including parse/upload/compile and any required identity check. |
| End-to-end TTFT | Send/start of the recorded request to its first generated token callback, including formatting/tokenization/prefill/sampling. Record time to first visible text separately if relevant. |
| Prefill throughput | Prompt tokens actually processed divided by completed prefill wall time. Include required GPU completion/readback, and state whether tokenization is included. |
| Decode throughput | For token timestamps t1…tN, `(N - 1) / (tN - t1)` after conversion to seconds; N must exceed 1. Report output count, EOS/cancel status and any tokens hidden by UI filtering. |
| Full-response latency | Send/start to completion, separately from sustained decode throughput. |
| Memory | Peak application-owned GPU allocation ledger, plus separately sampled driver/process GPU memory and host memory if available. Record idle baseline and sampling interval. |

Do not label wall-clock queue submission time as GPU execution time. Timing queries require supported features and a separate validated instrumentation path. If a metric is unavailable, record null/unmeasured. The built-in short “Benchmark / tune speed” is a tuning smoke test, not by itself a TTFT, sustained-throughput or peak-physical-VRAM benchmark.

GPU utilization percentage is optional diagnostic context, not a success target. More work, larger batches or duplicated requests can raise utilization while making interactive latency worse. Select a change for reproducible latency/throughput gains with equal correctness and acceptable memory, responsiveness and power/temperature behavior; do not promise a target percentage or tokens/s in advance.

## 5. Expression-only and mixed workload checks

After the text baseline passes, use consented local camera input and the expression-only starter:

- Verify no camera/analysis starts on load, reload or restored settings. Starting and stopping must be obvious.
- Verify that only local detector/expression/runtime assets load. Identity enrollment/recognition, scene/object/animal paths and remote camera submissions must remain unavailable, including after restoring old settings.
- Test no face, partial face, low light, multiple faces and low-confidence output. Expressions remain uncertain visual cues; no identity or internal-emotion claim is permitted.
- Stop while loading/analyzing; close video; change model; leave the page. Late worker results must be discarded and capture must stop.
- Repeat the same text prompts with expression analysis active. Record the change in TTFT, decode speed, CPU/host memory and GPU allocation if any. Worker/WASM activity is not automatically Radeon work.

## 6. Release gate and receipt

An eligible release has matching artifact hashes, passing current build/syntax/host/DOM suites, explicit model-format rejection tests and separately recorded browser/real-model/hardware results. Keep previous receipts labelled historical. A skipped test is not a pass, and mocked WebGPU does not execute Radeon shaders.

Use `qa/release_inventory/hardware_result_template.json` for each physical-machine run. Add test cases for missing assets/hash failure, unsupported tensor type, context overflow, allocation rejection, cancellation, repeated load/unload and expression stop/races. Mark a speed change qualified only when correctness remains within its declared criterion and repeated measurements show the claimed improvement without a meaningful latency, stability or memory regression. No hardware-specific performance claim is made until that evidence exists.

## 7. Download checks

Verify initial app load and source-only entries make no download-directory request. Check files must contact only the chosen public directory and pin its returned revision. Confirm that the displayed license/source is reviewable, unsupported formats remain unavailable, and a save picker is opened only by Download. Test cancel during metadata fetch, during the picker, during streaming, and on session end; double-clicking must not create parallel transfers. Test missing SHA/size, length mismatch, hash mismatch, network failure and unavailable direct-to-disk support. Existing local models must not be loaded/replaced as a side effect. No conversation/profile/frame content or credential may be included in downloader requests. Directory lookup and HEAD-only server checks do not replace these actual-browser tests.

## 8. Session learning qualification

Use explicit reviewed, approved corrections on the exact locally loaded model. Record the full model SHA-256, adapter ID, optimizer options, held-out prompt-family counts, base/previous/candidate complete-answer losses, preference margins/accuracy and fixed-regression results. Require improvement against both the frozen base and previous adapter with all regression gates passing before promotion. Repeating a deterministic training run that cannot improve the previous adapter should retain it rather than report another improvement.

Test End Session with no local model, no approved examples, insufficient held-out families, successful training, evaluation rejection, GPU loss, storage quota failure, other-tab edits, cancellation and End without training. Verify names and approved memories survive restart, the prior adapter remains recoverable, model hashes select separate checkpoints, and revoking/deleting/editing an approved source invalidates retained derived data. Browser closing or crashing during training may require retraining from the saved approved snapshot; this flow does not claim an optimizer-resume checkpoint. Use the explicit restore-and-evaluate control after loading the same model to qualify persistence across sessions. The synthetic bridge tests demonstrate optimizer and orchestration behavior only; repeat with actual model activations on the Radeon before claiming a practical personalization benefit.
