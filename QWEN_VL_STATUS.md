# Qwen2.5-VL-7B: implemented experimental text and still-image path

The earlier staged-only description is obsolete: the custom text graph, strict local companion importer, GPU image encoder, preprocessing/prompt/position path, and explicit image-question UI are implemented. **Full 7B checkpoint quality, image-conditioned next-token parity, real-browser execution, and Radeon qualification are still unverified.** Final composed UI/lifecycle tests pass against the accepted release HTML; consult [RELEASE_STATUS.md](RELEASE_STATUS.md).

This implementation targets the exact inspected Qwen2.5-VL-7B profile. It does not claim support for original Qwen-VL, Qwen2-VL, Qwen3-VL, other sizes, MoE variants, video, arbitrary projector conversions, or all versions.

## Accepted inputs and computation

### Text GGUF

A single-file `qwen2vl` GGUF must pass the inspected 7B geometry and tokenizer/template contract: 28 text layers, hidden 3584, FFN 18944, 28 query / 4 KV heads, full 128-wide heads, vocabulary 152064, RMS epsilon 1e-6, RoPE base 1e6, and M-RoPE sections 16/24/24 (an explicit trailing zero is accepted where specified). Active sliding-window/scaled-RoPE variants are not silently normalized to this contract.

The dense text path includes biased Q/K/V projections, SiLU-gated FFN, and separate sequential KV indices versus rotary positions. The application context cap remains 4096, bounded further by memory and prompt/output limits. A model's larger advertised context is not this app's allocation.

### Matching local companion

Select the matching local GGUF companion explicitly. It must declare `general.architecture=clip`, `clip.projector_type=qwen2.5vl_merger`, the expected vision/SwiGLU metadata and complete exact tensor mapping. Matrices may be F32, F16, or Q8_0; normalization and bias vectors must be F32. Arbitrary quantized projector formats are not accepted.

The importer checks GGUF version, metadata counts/lengths, duplicates, alignment, tensor sizes/shapes/ranges, overlap, normalization, and local/full-attention schedule. It bounds the file at 2 GiB, header at 4 MiB, and individual tensors at 128 MiB. Temporal patch slices and split Q/K/V names must match the implemented mapping. A filename containing `mmproj` alone is insufficient.

The real custom WebGPU encoder implements the inspected 32-block vision graph: hidden 1280, FFN 3420, 16 heads, 14×14 spatial and two-frame temporal patches, local-window/full attention with full layers 7/15/23/31, RMSNorm, biased SwiGLU blocks, 2×2 merger, GELU, and output dimension 3584. Packed weights use bounded cache/tile handling; the full network is not replaced with an expression model or a dummy embedding.

### Explicit still-image questions

Open **Models → Local image questions**. The image-question panel requires the loaded local Qwen graph, a matching companion, and one deliberately selected JPEG or PNG. Input is limited to 32 MiB, with dimensions inspected in a bounded header before decoding, at most 24 million source pixels, and aspect ratio at most 200. Transparent images are flattened onto opaque white by the UI. Deterministic antialiased bicubic preprocessing keeps the encoded image at most 50,176 pixels, 256 patches, and 64 merged image tokens (224×224 for a square at the maximum budget).

The prepared prompt expands the exact image placeholder and binds its token IDs to image vectors. Three-axis M-RoPE preserves time/height/width positions and the subsequent text-position delta. The dedicated image flow uses those prepared IDs directly for prefill/decode; it must not generic-retokenize away image tokens or reset the visual context before generation.

Image questions visibly use base weights, without chat memory or an active learned output-head adapter. Image, question context, and answer are not automatically added to ordinary chat history, RAG/memory, backups, or correction-training capture. Model loading, companion loading, image decoding, encoding and generation have separate cancellation/ownership guards. The image path does not start camera/microphone capture or send images to an online provider.

The optional facial-expression sidecar is entirely separate. It cannot provide Qwen's learned image embeddings or qualify general image understanding.

## Evidence actually obtained

- Independent NumPy/SciPy reference: non-square 24-patch, two-layer, tiny synthetic vision encoder/projector; JavaScript output maximum absolute error about 1.93e-7. Fixtures are generated test data, not pretrained checkpoint weights.
- Exact custom WGSL replay on CPU Vulkan SwiftShader: 128 captured application commands per reduced F32/F16 case. Maximum absolute errors about 1.80e-6 (F32; tolerance 2e-5) and 2.38e-4 (F16; tolerance 0.002).
- Separate F32/F16/Q8_0 matmul shader cases cover partial 16×16 tiles and unaligned Q8 scale words; largest recorded error about 1.56e-7.
- Strict importer, exact official-tokenizer/prompt fixtures, deterministic resize fixtures, M-RoPE/token-binding and graph lifecycle checks are included.
- UI input validation, cancellation, direct prepared-prompt binding, base-weight isolation and privacy/lifecycle checks are separate composed-app tests. `qa/QWEN_IMAGE_FLOW_RECEIPT.json` records 11 core, 7 composed UI, and 21 related reference/importer/tokenizer checks passing against the final hash.

Key sources: `patches/qwen_vl/`, `tests/qwen_vl_reference.cjs`, `tests/qwen_vl_importer.cjs`, `tests/qwen_vl_tokenizer.cjs`, and the image UI tests. Receipts: `qa/qwen_vl_numerical.json`, `qwen_vl_gpu_native_f32.json`, `qwen_vl_gpu_native_f16.json`, `qwen_vl_quant_native.json`, and final integration results.

These checks establish bounded component behavior. They do not establish real 7B output accuracy, arbitrary browser image-decoder parity, full-size performance, high-resolution image quality, or physical GPU stability. Native software-adapter execution is not a browser or Radeon test.

## Source provenance and remaining qualification

Pinned/source-hashed configuration, tokenizer, image-processor and conversion research are retained under `patches/qwen_vl/`. They reference the official [Qwen2.5-VL-7B configuration](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct/blob/main/config.json), [preprocessor configuration](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct/blob/main/preprocessor_config.json), versioned Transformers semantics, and GGUF conversion mappings. Mutable upstream links are research references; exact admitted local files still need their own provenance/hash record.

Before claiming a qualified local vision model:

1. Identify the exact text and companion GGUF hashes, source revisions, converter version, storage layouts and tokenizer/prompt contract.
2. Compare full-size intermediate image embeddings, text-only and image-conditioned next-token logits against a pinned independent reference using the same representation and image preprocessing.
3. Exercise actual browser file decoding, WebGPU compilation, real device limits, cancellation, context reset, model unload, memory peaks and repeated requests.
4. Measure useful latency and output quality separately. Keep the bounded resolution, base-weight-only image flow, privacy exclusions and unsupported version/format errors visible.

No complete new language-model checkpoint was downloaded for these tests. Do not use component success to remove those remaining qualifications or silently widen model admission.
