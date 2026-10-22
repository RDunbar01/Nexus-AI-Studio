# Nexus AI

## Current release licensing

This Nexus release is not offered under Apache License 2.0. Nexus-owned software may be used only for personal, non-commercial purposes. Any other use, including commercial use, modification or redistribution, requires express written consent from the rights holder. Third-party code, models, datasets and separately licensed components retain their own licenses and notices. Previously granted rights and rights that cannot lawfully be restricted remain unchanged.

**Candidate 24 · next-release staging · not a published application update**

Local AI workspace with separate custom WebGPU and Nexus.cpp paths. Model admission, resident weights, server health and chat readiness are separate states. A compatible tokenizer, architecture and quantization are required for the selected engine.

## Current baseline and release status

Verified starting baseline: **Candidate 23**. The staged source and package advance to **Candidate 24**. Native Windows binary qualification remains separate.

Current audited source includes plain chat with no automatic past-workspace retrieval, stale-reply cancellation, isolated fresh-install mode, local model import and explicit hardware profiles. Native and browser engines do not have identical capabilities. Full Mistral 7B Windows/Radeon operation has not been qualified by these tests.

## A useful first chat model

[Mistral 7B Instruct v0.3, official model card](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) is a useful first model to consider for Nexus AI when the chosen backend supports its exact architecture, tokenizer and quantization. The official model card distributes Safetensors, not a ready-to-load GGUF: select a trustworthy compatible GGUF conversion for the GGUF loader, check its provenance and license, and validate loading before calling the model ready. Do not download every Safetensors shard expecting the GGUF loader to accept it.

Radeon RX 7900 XT and XTX nominal VRAM specifications are 20 GB and 24 GB respectively; these are not guaranteed available budgets. Runtime allocations, context/KV cache and other processes reduce usable capacity. A manual profile is a declared configuration, not hardware detection or a benchmark result.

## Start and inspect the original project

Use the exact launch instructions accompanying the matching release package. The [preserved previous README](docs/README_PREVIOUS.md) contains the original workflow, research citations, credits, downloads and limitations. Treat its release-specific statements as historical; this staged update does not silently replace its software or relicense dependencies.

## Evidence and licensing

Developed by Rich Dunbar / Nexus Emerging Technology with AI-assisted coding. Retain existing licenses, attribution and third-party notices. No additional Windows, physical GPU, device-write or model-quality qualification is claimed by this documentation refresh. No live browser-trial deployment is created by this README.

### Real SmolLM2 CPU inference check

Nexus AI has been exercised through its real HTTP import/load/chat-streaming routes with a SHA256-verified SmolLM2-135M-Instruct Q8_0 GGUF using its independent Nexus.cpp CPU engine. A bounded CPU optimization removes repeated per-weight format dispatch for F32/Q8_0 and skips unused intermediate prefill vocabulary projections. The paired real-model request produced identical token IDs and text; 26 synthetic before/after comparisons preserved exact full logits.

See [the profiling report](docs/SMOLLM2_CPU_FINDINGS.md) and [raw evidence](qualification/smollm2_cpu/results/SUMMARY.json). Timing was highly variable on the shared cloud CPU, so the single before/after pair is diagnostic, not a reliable speedup or hardware benchmark. Windows native binaries must be rebuilt to include the change. No Radeon HIP, WebGPU or Windows performance qualification is implied.
