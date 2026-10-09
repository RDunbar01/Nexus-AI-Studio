# Model provenance and redistribution

Language-model weights are not bundled in these repositories. The two proof fixtures are SmolLM2-135M-Instruct Q8_0 and F16 representations, identified by full-file SHA-256 in `docs/CODEC.md` and the codec receipts. Compression preserves the already-selected numerical representation; it does not make Q8 weights identical to their F16 counterpart.

The [original SmolLM2-135M-Instruct model card](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct/blob/main/README.md) declares Apache-2.0. The [GGUF distributor's model card](https://huggingface.co/bartowski/SmolLM2-135M-Instruct-GGUF/blob/main/README.md) identifies the source model and distributed conversions. Preserve applicable notices when redistributing model files; a model-card declaration is not an independent audit of every training-data right or permission for a particular deployment.

Q8 recovery was verified against distributor revision `b57b6475ae6f5f2b1b51c43a1190a64cab325ef4`, file `SmolLM2-135M-Instruct-Q8_0.gguf`, SHA `5a1395716f7913741cc51d98581b9b1228d80987a9f7d3664106742eb06bba83`. The exact download URL is recorded in `qa/shared_codec/q8_redownload.json`.

F16 recovery verifies 270,885,952 bytes and SHA `f535f83ec568d040f88ddc04a199fa6da90923bbb41d4dcaed02caa924d6ef57`. Its preserved recovery receipt did not record a download URL; no new provenance URL is inferred from the filename. See any later verified supplementary receipt before redistribution.

This NexusAI release bundles only the two small expression models and the pinned ONNX Runtime Web sidecars documented in [EXPRESSION_ONLY.md](EXPRESSION_ONLY.md) and `assets/pretrained_manifest.json`. Preserve `licenses/`, including the unresolved FER model-specific license-evidence caveat. General vision packs are not part of this release.

New Gemma/Mistral/GPT-oss/Qwen work used configuration/tokenizer sources, bounded public metadata headers, and small generated numerical fixtures. Those are not complete new pretrained checkpoints. Synthetic fixture weights are test data and must be labeled as such; the runtime release contains no language-model weights. Public source names are provenance references, not evidence that the user's exact local files were inspected. [Capabilities and evidence](CAPABILITIES.md) records the actual boundaries.
