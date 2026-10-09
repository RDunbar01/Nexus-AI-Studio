# Smol compatibility and representation notes

The Smol portion targets ordinary GGUF text execution for SmolLM and SmolLM2, including 135M, 360M, and 1.7B base/Instruct profiles. The wider release now also contains implemented experimental Gemma3, GPT-oss, Mistral/Ministral, and Qwen2.5-VL paths; their exact version/format/evidence boundaries are in [CAPABILITIES.md](CAPABILITIES.md). Smol tests do not qualify those other backends.

## Smol inputs

| Input | Route | Boundary |
| --- | --- | --- |
| SmolLM 135M / 360M / 1.7B Instruct | Single-file GGUF, official Smol1 frame | No injected Smol2 default system message |
| SmolLM2 135M / 360M / 1.7B Instruct | Single-file GGUF, official Smol2 frame | Distinct from Smol1 |
| SmolLM / SmolLM2 base profiles | Single-file GGUF, explicit plain completion | Do not invent an Instruct template |
| Custom LittleBit GGUF | Existing packed-factor route | Requires exact supported custom metadata, shapes and component encodings |
| Legacy NHSC1 wrapper | Existing host reconstruction route | Reconstructs blocks before GPU upload; not direct compressed inference |
| Experimental F16TRI1 | Explicit pinned SmolLM2-135M-Instruct reference | 128-token total prompt-plus-reply cap; [COMPRESSED_MODE.md](COMPRESSED_MODE.md) |
| Experimental Q8 NHD1 direct chat | Gated | Required full-model comparison remains incomplete |

The Auto and Strict SmolLM compatibility settings are session-only and locked while a model/activity is active. They select an admission policy; they do not convert a model or bypass validation. Model compatibility depends on architecture metadata, tokenizer/chat contract, tensor shapes and encodings, not filenames or model-folder labels.

Official configuration/tokenizer fixtures cover twelve Smol family/size/variant combinations. Exact F16/Q8_0 tensor inventories and real-file numerical checks cover the 135M proof model, not twelve complete pretrained models. See the matrix for the limited eight-position comparison, tokenizer corpus, and numerical differences from llama.cpp.

Ordinary dense GGUF has implementations for F32, F16, BF16, Q4_0, Q4_1, Q5_0, Q5_1, Q8_0, Q4_K, Q5_K, and Q6_K. Each tensor role/shape and row alignment still has to pass. Small Smol shapes do not imply every all-K conversion is valid. IQ/TQ, repacked layouts, MXFP4 on the Smol graph, Safetensors, PyTorch, and split GGUF sets are not admitted by this support statement. The ordinary app cap is 4096 tokens, further bounded by the memory plan; direct F16TRI1 has its separate cap.

## Weights, provenance, and downloads

Language-model weights are not bundled or automatically downloaded. Keep the exact full-file SHA-256, source/revision, quantization, converter, and tensor inventory with each qualification record. Official Smol source fixtures are pinned in `patches/compatibility/smol_provenance.json`; inherited compressed-file identities are in [MODEL_PROVENANCE.md](MODEL_PROVENANCE.md).

Settings → Model Downloads provides explicitly requested publisher/converter directory lookup and local streaming downloads. A transfer pins the returned revision and declared size/SHA-256. A canonical publisher repository containing only Safetensors is a source link, not a directly loadable GGUF choice. Gated licenses/access must use the publisher's own process; the app stores no credentials and does not bypass gates.

Catalog availability is narrower than architecture implementation. An available format is still only a candidate until full local admission succeeds. Unsupported repacked/split files, unmatched image companions, and GPT-oss-120B on the current hardware profile remain restricted. Downloading a matching name is not numerical or security qualification.

Catalog evidence is recorded in `qa/release_inventory/catalog_metadata.json`, `catalog_verification.json`, and `catalog_http_headers.json`. Header/core/DOM tests do not replace actual browser CORS, file-picker, cancellation, or physical transfer tests.

## Optional expression sidecars and startup

The release includes YuNet detection (232,589 bytes), ProgressiveTeacherFER expression scores (4,791,892 bytes), three pinned ONNX Runtime Web 1.22.0 files, and a generated expression worker. These are separate from language-model inference and Qwen image understanding. Select the supplied `assets` folder when opening the HTML directly, or use localhost/HTTPS. All runtime/model/worker bytes are checked; a lone HTML contains no expression sidecars.

Expression processing and capture are default-off. Labels are uncertain appearances, not internal emotions. A separate default-off local-tone option can share a fresh uncertain label with local chat only; no frame is sent to the language model or online provider. Identity/gallery/scene/object/animal/optional-pack and remote-camera upload implementations are removed. Camera/voice controls remain independent. [EXPRESSION_ONLY.md](EXPRESSION_ONLY.md)

Export an existing workspace before changing files, origins or browsers. Start with the small text baseline and actual truthful memory settings, then follow [RADEON_TEST_PLAN.md](RADEON_TEST_PLAN.md). No browser/Radeon performance or real-face accuracy result is implied by this release.
