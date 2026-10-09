# Accepted experimental release

The integrated runtime passed the available release gates and was approved for packaging on 2026-10-09. The released `NexusAI.html` is copied byte-for-byte from the frozen composed candidate, not from the historical root baseline.

- HTML SHA-256: `d1d45f1825852cfb20b80a868101820cdb89f504d8eeff707bed8c797177db93`
- HTML size: 4,084,777 bytes
- Final aggregate receipt: `qa/release_validation/final_verified/receipt.json`
- Original aggregate receipt SHA-256: `804cf967abf43b5240cc7bda66e4094d948f2c9c826a1658334496b82facdbc3`
- Final evidence index: `qa/FINAL_INTEGRATION_RESULT.json`

## Completed checks

| Evidence | Result | Scope |
| --- | --- | --- |
| Final aggregate | All 8 top-level groups passed; unchanged HTML hash | 439/439 component tests, 75/75 app tests, recorded-metadata/factory/head checks, 15 lifecycle sub-suites, 8 learning regression sub-suites, and real expression WASM smoke |
| Independent focused audit | 37/37 passed; no skips | Whole-app local-folder corruption/cancellation, native File clones into exact worker, real ONNX/WASM sessions, black-frame abstention/pixel erasure, native SHA-256 oracle, and source/worker/manifest identity |
| Final synthetic native checks | 10 recorded execution stages passed | Exact custom WGSL on CPU software WebGPU; captures/execution steps are not ten independently qualified real models |
| Final streaming replay | Four dense/Gemma cases and two GPT-oss host-cache cases passed | Streamed/resident and cached/uncached logits/hidden/KV equality in tiny software-adapter graphs |
| Session learning focus | 41/41 passed; no skips | Real output-head optimizer/coordinator/frozen-family logic with synthetic activations and whole-app IndexedDB tests |
| Qwen image focus | 11 core, 7 composed UI, 21 related checks passed | Synthetic fixtures, exact prompt binding, base-weight isolation, no automatic history/training capture, cancellation and locked-settings behavior |
| Actual SmolLM2-135M checkpoint prefix | Two positions per F16/Q8_0 format; 2/2 top-1 matches per format | Full 30-layer resident model computation under a CPU software-WebGPU bridge; no conversational/quality or browser claim |

Some focused checks overlap the aggregate. Do not add the counts together as independent coverage. The earlier `qa/release_validation/final` aggregate recorded two legacy/harness issues; `final_verified` is the corrected all-pass aggregate for the unchanged runtime. Its portable tooling uses recorded Gemma metadata and a synthetic Smol directory for ordinary factory tests; an explicit external header can separately verify the raw directory.

## Important remaining limits

- No browser was launched, no physical Radeon was executed, and no live camera/microphone, voice quality, browser file-origin/CORS/picker behavior, or real-face accuracy/fairness was qualified.
- No complete new large Gemma/GPT-oss/Mistral/Qwen checkpoint was downloaded or output-qualified. The actual Smol run covers only two plain prefix positions per format, not a generated answer, benchmark corpus, long-context behavior, training, compressed/offload path, or full browser startup/health workflow.
- GPT-oss-120B remains reserved for upgraded hardware; the current 20 GiB GPU + 32 GiB RAM profile does not qualify.
- Learning is approved text-only output-head adaptation with frozen transformer weights, held-out/regression promotion gates and recoverable prior adapters. Narrow metrics do not establish general reasoning or factual improvement.
- The application is still experimental. Passing these scoped tests does not guarantee model accuracy, useful speed, hardware fit, deployment clearance, or the absence of bugs.

The runtime ZIP supplies all offline expression assets and notices. The source/QA companion ZIP must be extracted beside it into the same `NexusAI/` folder before rebuilding/testing. Clean-package verification and final ZIP checksums are reported separately with the delivered artifacts. Missing optional external model fixtures must be reported as skips, never replaced with a download or counted as passes.

## Actual Smol numerical observations

`qa/real_smol/RESULT.json` and `REPORT.md` bind the exact F16/Q8_0 files, official reference, shader identities, and two input IDs to the frozen runtime. All four full-vocabulary rows are finite and all four top-1 comparisons agree. Maximum absolute differences against the same-format llama.cpp CPU reference reach approximately 0.03100 (F16) and 0.58432 (Q8_0). No predeclared near-equality threshold or bitwise CPU parity claim is made.

A separate F32 export preserves all 272 original Q8/F32 tensor values exactly and produces much smaller errors against the custom Q8 path, about 0.000168 and 0.002960 at the two positions. This strongly supports differing activation/dot precision as the dominant direct-Q8 difference, but is not a complete layer-by-layer proof. The native run uses CPU Vulkan SwiftShader and is not a Radeon speed result.

## Gemma numerical distinction

The synthetic Gemma3 Q4_0 comparison to llama.cpp has 7/8 matching top-1 tokens and maximum absolute logit difference 0.0834474266. At zero-based position 2, host token 3 differs from reference token 147; top-two margins are 0.0071994066 (host) and 0.0145751238 (reference).

A follow-up preserved all 80 stored tensor values exactly but ran them through llama.cpp F32 arithmetic: 8/8 top-1 matches and maximum error 0.0026168078. Actual CPU dot-function inspection/calls confirm direct-Q4 llama.cpp uses Q8_0-quantized activations, whereas the custom graph uses F32 activations. This isolates the dominant arithmetic-path difference; residual error remains and exact parity is not claimed. The separate custom-JavaScript versus exact-software-WGSL checks also pass their declared tolerances.

See [GEMMA_NUMERICAL_CAVEAT.json](GEMMA_NUMERICAL_CAVEAT.json), `qa/gemma/q4_arithmetic_audit/receipt.json`, and its `isolate.py`. This uses synthetic weights and a preinstalled reference toolchain, not a real 27B checkpoint.

## Receipt interpretation

Source-bound component receipts retain their original candidates and limits; older artifacts are not silently certified by final composition. Final native/source checks explicitly bind the frozen runtime. Packaged evidence may replace absolute local paths with shareable placeholders; `EVIDENCE_PATH_REDACTIONS.json` records any such path-only change and the original receipt hash. Numerical results and source identities are not rewritten to manufacture a pass.
