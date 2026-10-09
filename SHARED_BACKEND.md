# Shared Nexus inference backend v2.1

Reusable before/after PPL and single-step direct-compressed inference for the Nexus Zero Loss Compression Suite and NexusAI. This version extends the frozen F16 graph with exact Q8_0/NHD1 weight helpers. It does not replace or mutate the standalone frozen F16 v1 archive.

## Load order

Load the canonical `../shared_codec/src/codec.js`, then these files:

1. `src/pinned.js` (unchanged frozen protocol and original shader data)
2. `src/formats.js` (F16/Q8 descriptors, Q8 shader identities, tokenizer equivalence, byte-restoration proofs)
3. `src/core.js` (strict model admission and shared scoring)
4. `src/webgpu.js` (one graph with format-specific weights)
5. `src/controller.js` (one benchmark lifecycle)

All modules are local IIFEs. No package install, external resources, network calls or dynamic execution of model data are used. Do not fork the graph or scorer into a second compressor engine.

## API

`NexusBench.modelSpec('f16'|'q8')` exposes a pinned descriptor.

`controller = new NexusBench.BenchmarkController((event, receipt) => {})`

`await controller.run({raw: originalFile, direct: compressedFileOrBlob}, 'both-raw-first', 'q8')`

- Second argument: `both-raw-first`, `both-direct-first`, `raw`, `direct`.
- Third argument: `f16` (default) or `q8`.
- `controller.cancel()`, `.receipt`, `.gate.active` retain the same lifecycle contract as v1.
- Concurrent runs are rejected. Cancellation, including during the final token hash, cannot publish a completed comparison. Reentrant completion callbacks return the correct previous receipt.

For single-step inference:

`model = await NexusBench.loadModel(file, 'direct', signal, progress, 'q8')`

`prefix = NexusBench.originalMetadataPrefix(model)`

`selected = await NexusBench.WebGPU.requestAdapter()`

`graph = await NexusBench.WebGPU.Graph.create(selected.adapter, model, signal, progress, {context: 2048})`

`{logits, timing} = await graph.step(tokenId, position, signal)`

`graph.close()`

Positions must start at 0 and proceed exactly once below the selected context. Single-step/chat contexts are explicitly limited to 128, 512 or 2048, with a default of 128. The benchmark controller always forces 128. The pinned model metadata context of 8192 is verified, but contexts above 2048 are rejected. A prompt plus requested generation exceeding the selected cap must fail clearly; do not wrap or silently truncate. Allocation is guarded by adapter binding limits and a 350 MiB explicit-buffer budget. Existing original-GGUF application routes do not need to change. The longer chat cap has separate host/mock and native attention/RoPE/KV boundary coverage; full-model execution beyond 128 and browser/Radeon execution remain unperformed.

Copy the metadata prefix for an existing tokenizer, then release parsed host model references after graph upload if no longer needed. The graph keeps compressed packets as GPU matrix weights. It does not need a reconstructed matrix. `metadataBytes` contains 1,785,664 original GGUF bytes for F16 and 1,785,952 for Q8. It is not a tokenizer implementation. Custom-corpus text is not supported by the fixed benchmark controller; a future option must use identical verified tokenization for both paths.

## Admitted formats

F16 identities remain unchanged:

- Raw 270,885,952 bytes: f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57
- F16TRI1 195,676,989 bytes: d365dd74dd8cb89603182f3c70372f6f27d4c73602a6df09d6de430f11f76605

Recovered Q8 identities:

- Raw Q8_0 144,811,360 bytes: 5a1395716f7913741cc51d98581b9b1228d80987a9f7d3664106742eb06bba83
- NHDMOD1 container (.nhd1) 140,446,944 bytes: 896c6bf6bda9cf1dab262ae4144816057d7ab8705c1ad5e46931c1827fd0fa41

Known shapes, source SHA, entire canonical container SHA, manifest coverage, all region checksums, tensor compatibility and finite scales/norms are checked before GPU use. NHD1 packet validation and scalar lookup use the canonical NexusCodec implementation. The exact pinned Q8 file uses 211 NHD1 matrix packets and 61 literal F32 norm vectors. Generic codec support does not broaden the inference admission gate to arbitrary models or container encodings.

Filename-only metadata variants are admitted without trusting the declared source SHA: actual manifest checksum and canonical JSON are checked, the pinned manifest offset is required, and only source_name plus dependent global manifest length/checksum are replaced virtually. The complete virtual canonical container must hash to the exact frozen reference. Any payload change, source-hash spoof or noncanonical JSON is rejected. The original file stays unchanged; observedFileSha256, canonicalContainerSha256 and filenameNormalization are reported separately. The frozen v1 standalone remains exact-file-only.

The compressed Q8 kernel is a new recovered 256-lane source identity, not a promoted optimization of the F16 shader. Q8 matvec binds compressed W, FP32 X and FP32 Y only; its shape comes from the validated packet. Q8 gather additionally binds a 16-byte [row,0,0,0] uniform. The raw Q8 control uses the explicitly versioned QuantGPU qt8 R2 path: only half conversion changes to unpack2x16float to preserve signed-zero bit patterns. Its gather uses the same weight() function with token in row_base. The old signed-zero failure evidence is retained. All 4,202,496 actual Q8 scale values were separately checked positive, finite and nonzero. Frozen F16 shaders are unchanged. All other graph kernels and dispatch ordering are shared.

## Evidence and interpretation

The same frozen pilot is used for both formats: 128 inputs predict the next 128 targets from 129 IDs. The entire 304,978-ID corpus tokenization was independently checked to match between the original F16 and Q8 files. That is tokenizer evidence, not Q8 inference or PPL evidence.

Both canonical compressors separately reproduced their pinned containers and restored every original byte and SHA-256. These full-byte restoration proofs are in `referenceByteRestoration`. Actual imported file hashes are recorded per path. The inference runtime does not expand matrices to repeat the byte restoration itself.

GPU numerical comparison is separate. `numericComparisonCriteria` applies no tolerance: every unequal logit remains counted and the maximum absolute difference is reported. A tiny difference can result from permitted floating-point fusion/reassociation across compiled WGSL and is not, by itself, evidence that source weights were compressed lossily. A matching PPL alone is also not an exactness proof. Partial and complete outcomes remain distinct.

Performed here: full real-file parsing, 252,677 scalar/norm checks per family, same-token protocol checks, synthetic/scorer tests, controller tests, and mock WebGPU graph allocation/binding/uniform/lifetime tests. No shaders were executed by these tests. Browser, Radeon and visual QA remain unperformed. Fresh native SwiftShader R2 parity is now supporting evidence: five synthetic mode combinations and three actual matrices passed bitwise raw/direct matvec and gather; four actual embedding rows passed gather. Both 65,536-scale-bit-pattern probes passed. The full embedding-output GEMV was deliberately not executed in that bounded test; its receipt false field means unexecuted, not mismatch. Full Q8 graph/PPL remains pending. These native results do not establish JavaScript/browser/Radeon execution.

At context 128, application buffers including readback are:

- F16 raw: 272,492,064 bytes; direct: 197,284,380 bytes.
- Q8 raw: 146,417,200 bytes; direct: 141,983,320 bytes.

These are allocation-ledger totals, not total VRAM. Driver/compiler memory, hidden staging and host memory are excluded. Q8 direct has 353 buffers; the other paths have 564. Every path uses 483 dispatches per token. Only one device/path is resident at a time for the benchmark.

## Tests

From this directory, with the adjacent recovered source/reference tree present:

- `node tests/test_core.cjs`
- `node tests/test_controller.cjs`
- `node tests/test_models_and_graphs.cjs`
- `node tests/test_filename_admission.cjs`
- `node tests/test_guarded_contexts.cjs` (current guarded 128/512/2048 contexts)

The model test needs both exact raw/packed model pairs. They are not shipped in source deliverables. The core fixture test reuses the frozen v1 package's independent synthetic/native-logit fixtures. `validation/source_manifest.json` records current source/dependency identities. `build_formats.py` is a maintainer pinning helper and requires the local reference model tree; ordinary users do not need to run it.

The historical experimental candidate and its tests are retained only as review evidence; do not bundle experimental/ into applications. Current supported contexts come solely from production src and the pinned descriptors. Native long-attention fixtures cover named positions through 2047 with exact packed KV bits and untouched inactive-score sentinels. They do not imply a full long-context model/PPL evaluation.
