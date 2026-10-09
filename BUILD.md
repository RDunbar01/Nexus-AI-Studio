# Build and verify this repository

## Inputs and output

Run `python3 scripts/build.py` from the repository. The builder composes the checked-in `src/NexusAI_modular.html`, guarded feature patches, shared codec/backend snapshot, and compressed host adapter into **`src/NexusAI_compressed_candidate.html`**. It checks embedded teacher/backdrop preservation and script syntax. `qa/build_receipt.json` records that candidate's identity and patch list.

The modular template is reconstructed source, not an original historical release. `input/NexusAI_a59480b7.html` is a provenance input. The root `NexusAI.html` remains historical until explicit release promotion. Never use it as the source for the new release, and never label a new output with a lost historical hash.

Freeze the composed candidate only after all feature owners are integrated. Run final tests against that same file, regenerate/verify expression sidecars, then copy the exact candidate bytes to `NexusAI.html`. Recompute the full-file hash after copying. Any runtime edit/rebuild after freeze invalidates the final receipt until relevant checks are rerun.

## Local checks

1. Install pinned Node test dependencies with `npm ci`.
2. Run `python3 scripts/build.py`.
3. Run `npm run test:release` for the aggregate release checks. The optional `--native-software` runner flag requires a preinstalled compatible software WebGPU stack and obtains no dependencies or weights.
4. Run `npm test` for appearance/compressed-host checks and `npm run test:regressions` for recovered learning/media checks.
5. Run the complete lifecycle matrix: `python3 tests/upgrade_lifecycle_runner.py --html src/NexusAI_compressed_candidate.html --label final`.
6. Run focused whole-app expression, SHA-256 oracle, and exact source/worker-binding checks with `python3 tests/upgrade_lifecycle_adversarial_runner.py` using its explicit final-HTML/label options.
7. Run the component and integrated suites referenced in [CAPABILITIES.md](CAPABILITIES.md), including compatibility/tokenizer, Gemma/Mistral/GPT-oss/Qwen, offload, expression assets, and session-learning checks. `npm test` alone is not the full release suite.
8. Record test commands, exit status, case counts, skips, source hashes, and the final candidate hash in the release receipt.

Tests commonly accept an explicit `NEXUS_*_HTML` environment variable. Inspect each harness before running; do not let it fall back to a historical candidate. The lifecycle runner freezes its own HTML snapshot and copies legacy fixtures before result writers run. It also records scoped legacy fixture adaptations for the changed camera/voice contract.

The public 8 MiB Gemma checkpoint prefix is excluded from the shareable source ZIP because it includes real weight bytes. Normal Gemma geometry/router checks reconstruct the recorded target inventory from the retained `target_meta.json`/`target_directory.json` through `qa/gemma/metadata_fixtures.cjs`; this checks recorded metadata and synthetic routing, not a fresh raw-checkpoint parse. `NEXUS_GEMMA_HEADER` can optionally supply an already available raw header for the separate directory comparison. No downloader is substituted.

For the full-file compressed-host case, set `NEXUS_F16_DIRECT` to the exact pinned F16TRI1 fixture already available locally. It is visibly skipped when absent. Codec/parser/tokenizer are real, while that test's graph/device are mocked. No ordinary test should silently download model weights.

Independent reference regeneration uses optional Python dependencies (for example NumPy, SciPy, tokenizers, Pillow, SentencePiece or reference runtimes as specified by the individual generator). Native shader/graph checks require the documented software-adapter helper and its dependencies. Python and these native helpers are test tools, not browser runtime dependencies. Missing dependencies must be reported as not run/skipped, never passed.

## Expression assets

The runtime release contains the exact two ONNX model files and three ONNX Runtime Web files listed in `patches/expression/manifest.json`, plus a generated `assets/workers/expression_worker.js` and notices. These are the only bundled pretrained models; language-model checkpoints remain separate.

Use `package_assets(destination)` from `patches/expression/apply.py` to copy the strict whitelist, verify model/runtime hashes, and generate the expression worker from current source. The HTML embeds the expected worker size/hash, so the worker must be generated from the same source as the frozen HTML. A stale worker deliberately fails integrity checking.

Do not copy general-purpose vision packs or unrelated models into the release. From a directly opened HTML, the explicit local-folder picker supplies verified file bytes without asset downloads. A localhost/HTTPS route can fetch the same-origin assets with redirects forbidden. Both still require actual browser qualification; Node worker/WASM execution is separate evidence.

## Shared-source and release rules

Current local shared codec/backend files must agree with `SHARED_SOURCE_IDENTITIES.json`. The inherited `SHARED_SOURCE_LOCK.json` preserves a historical upstream-path snapshot and is not a current local-file manifest. Changes require fresh codec, graph, lifecycle, and paired-evaluation checks. Model files are data, not trusted kernels or executable code. Unknown representations, graph features, or contexts fail unless implemented and separately tested.

See [RELEASE_PACKAGING.md](RELEASE_PACKAGING.md) for the runtime/source layout, exclusions, integrity manifest, and promotion gate. See [RELEASE_STATUS.md](RELEASE_STATUS.md) for actual current completion rather than inferring it from these instructions.

## Source/QA companion archive

Extract both `NexusAI_Offline_App.zip` and `NexusAI_Source_QA.zip` into the same parent folder, allowing their shared `NexusAI/` directory to merge. The app ZIP supplies the exact FER/WASM sidecars required by the build and expression tests; the source ZIP supplies code, normal test inputs and compact evidence. From that combined `NexusAI/` folder, use `npm ci`, `python3 scripts/build.py`, then `npm run test:release`. The source archive alone is not a substitute for the app's required asset bytes. See `SOURCE_PACKAGE.md` in the companion archive for optional generator/reference dependencies and exclusions.
