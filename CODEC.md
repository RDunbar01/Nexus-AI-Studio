# Nexus ZLC shared browser codecs

This is the canonical data-only codec source for the Nexus ZLC compression/restore
suite and Nexus AI's compressed-model import. Copy `src/codec.js` identically into
both products; record its SHA-256 in each build receipt. Do not fork its format
logic inside a UI. Model files never supply executable code.

## Verified recovery identities

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Original SmolLM2 Q8_0 GGUF | 144,811,360 | `5a1395716f7913741cc51d98581b9b1228d80987a9f7d3664106742eb06bba83` |
| NHDMOD1 compressed Q8 | 140,446,944 | `896c6bf6bda9cf1dab262ae4144816057d7ab8705c1ad5e46931c1827fd0fa41` |
| Original SmolLM2 F16 GGUF | 270,885,952 | `f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57` |
| F16TRI1 compressed F16 | 195,676,989 | `d365dd74dd8cb89603182f3c70372f6f27d4c73602a6df09d6de430f11f76605` |

These outputs were reproduced after workspace recovery with this browser JavaScript
under Node. They match the pre-reset model-container identities exactly. Full
Restore verified every original byte and the complete original-file SHA-256.
The Q8 source was redownloaded once from the pinned public model revision; the
receipt records that URL. Compression introduces no quantization or training.

The Q8 format saves 3.013863% of the complete input. F16TRI1 saves approximately
27.76%. Neither percentage is an inference-speed claim. Model sizes include all
metadata, headers, dictionaries, indexes, exceptions, alignment, and hashes.

## Browser API

The IIFE exports `globalThis.NexusCodec` and also supports CommonJS tests.

- `await compress(file, {signal, onProgress, format?})` returns `{blob, manifest,
  report}`. The default selects NHDMOD1 for Q8 matrices or F16TRI1 for F16 matrices.
  It verifies every encoded word/byte against the original before returning.
- `await restore(container, {signal, onProgress, original?})` returns `{blob,
  manifest, report}` only after full original-file SHA verification. Providing the
  original File additionally compares every restored byte directly.
- `await inspect(file, {signal})` validates metadata/container structure and returns
  its format, tensor directory, original metadata bytes and source identity.
  Inspection does not replace per-region validation before inference upload.
- `storedRegion(file, region, format, signal)` verifies a stored region's SHA.
- Q8 packet functions: `encodeQ8`, `q8Layout`, `q8Lookup`, `validateQ8`, `decodeQ8`.
- F16 packet functions: `encodeF16`, `f16Layout`, `f16Lookup`, `validateF16`,
  `decodeF16`. F16 lookup returns exact original integer bit patterns.

Progress callbacks receive `{phase, completed, total, fraction, message}`. All
operations honor AbortSignal at bounded work/read/hash boundaries. Errors and
cancellation return no successful result. File inputs are read-only; the codec
never opens a filesystem destination or overwrites a source. The host controls
explicit user download/save actions.

`src/worker.js` is an optional job wrapper. Concatenate the unchanged codec source
before it in a Blob worker, or load it next to `codec.js`. A run message is
`{type:'run', id, operation, file, original?}`. Operations are `compress`, `restore`,
`inspect`, or `roundtrip`. The latter enables export only after compression and
full Restore against the original. Cancel with `{type:'cancel', id}`. Every event
includes the job ID, and the host must ignore stale jobs. The host may terminate a
worker when abandoning a task; it must release old Blob URLs and results.

## Limits and supported inputs

- Little-endian GGUF v2/v3
- Maximum original model: 512 MiB; tensor/metadata region: 64 MiB; manifest: 16 MiB
- Q8_0 matrices and F32/F16/BF16 literal ancillary regions in NHDMOD1
- F16 matrices and F32 vectors in F16TRI1
- Mixed Q8/F16 matrix families are rejected by default
- One source tensor is processed at a time; compressed output Blob parts remain
  in memory. Restore intentionally holds the restored download Blob, outside the
  inference path. A UI should disclose this memory use.

Direct inference uses packet lookups, never `decodeQ8`/`decodeF16`. Those two
functions are offline Restore/verification functions, not inference fallbacks.
The engine may enforce narrower model-specific, finite-value and shader-mode
admission in addition to this generic exact-byte validator.

## Validation scope

- Complete Q8 and F16 browser-codec conversion and exact Restore under Node
- 72 independent named baseline cases: Python byte oracles, all 65,536 F16 bit
  patterns, F32 NaN payload/signed-zero preservation, malformed bounds/ranks,
  data/hash/source mismatch, cancellation, truncated reads, repeat isolation
- Local regression cases and incremental SHA boundary tests
- 16 fixed worker-envelope lifecycle cases under Node VM, using mocked codec
  calls: cancellation, busy-job rejection, failure cleanup, and repeat jobs
- 37 independent Experimental cases, including legal 15-bit primary keys and
  zero-bit rare keys; 8 separate pinned-filename helper cases
- Full-model lineage check: all 4,202,496 Q8 blocks reproduce byte-for-byte from
  the frozen F16 weights using the recorded reference rounding, and all 140,544
  F32 bytes match. This is a source-lineage check, not part of the lossless codec.
- No fresh interactive browser or GPU execution is claimed by these codec tests

The recovered `nhd1_direct_256.wgsl` has a new source identity:
`f1e95d0eb35a9684328e6f239f26133581a68e1a8d69fc3217b19e7cd8f89dce`.
It preserves the documented 256-lane reduction strategy but requires new native
parity tests before a Q8 perplexity result. F16's separately frozen, shared Nexus
graph/scorer remains unchanged. Experimental mode8/9 formats are outside this
baseline and must not inherit its perplexity claims.

## Frozen source revisions

- `src/codec.js`: `af4ce6eb43fd3ed3891b8fc84955ff19059dfb2a5f137c3a2da5539cd3295fc2`
- `src/experimental.js`: `320c7e7388d2ea76913fa3810fec16df66aeef2676b9df73c10aad8e661a4183`
- `src/pinned-proof.js`: `d77c2d587bc5d1c13a3cfbd35901d92100f4e45407ea833f4dd7434ed0672b1d`

The baseline revision adds cancellation checks after final progress callbacks.
It does not change serialization. Historical receipts identify the prior source;
`qa/final_identity_replay.json` records fresh whole-model verification using the
final source revisions. Independent final audit receipts identify the exact
loaded source and confirm that it did not change during each run.

## Commands

```sh
node tests/codec_tests.cjs
node tests/worker_protocol.cjs
node tests/full_roundtrip.cjs source.gguf new-output.nhd1 receipt.json
```

The full-roundtrip harness refuses an existing output. No PyTorch, llama runtime,
Python, or network service is required by the browser codec. The optional
`nhd1_reader.py` is a separate standard-library reference for native QA only.
