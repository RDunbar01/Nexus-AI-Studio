# Nexus AI

## Current release licensing

This Nexus release is not offered under Apache License 2.0. Nexus-owned software may be used only for personal, non-commercial purposes. Any other use, including commercial use, modification or redistribution, requires express written consent from the rights holder. Third-party code, models, datasets and separately licensed components retain their own licenses and notices. Previously granted rights and rights that cannot lawfully be restricted remain unchanged.

**Candidate25 · hardening candidate · draft package staging, not a published update**

Local AI workspace with separate custom WebGPU and Nexus.cpp paths. Model admission, resident weights, server health and chat readiness are separate states. A compatible tokenizer, architecture and quantization are required for the selected engine.

## Start locally: Python and browser requirements

Candidate25 requires the **full download and local loopback service**, including every matching installer/data component. Its HTML is not an approved standalone browser trial, and the existing project Pages site must not be presented as a live Candidate25 app.

Use **CPython 3.10 or later** for the installer and launcher; the recorded Linux checks used Python **3.12.14**, not every possible later version. The optional desktop window requires the package's declared `pywebview>=5,<7` runtime. A compatible browser with WebGPU is needed for the custom browser GPU engine. Native Nexus.cpp additionally needs a compatible built executable and, for Radeon acceleration, the supported compiler/HIP/driver setup.

Nexus AI uses its own **WebGPU and Nexus.cpp engines, not a PyTorch backend**. Python does not run inside the browser HTML. Do not treat GPU detection or a selected hardware profile as model compatibility, successful inference or measured performance. Physical Windows/Radeon/WebGPU and full-model qualification remain outstanding.

## Current baseline and release status

Verified starting baseline: **Candidate24**, retained as the previous staged package. Candidate25 adds single-user hardening; it is not enterprise-approved. Current Windows, HIP and physical Radeon/WebGPU qualification remain outstanding.

Current audited source includes plain chat with no automatic past-workspace retrieval, stale-reply cancellation, isolated fresh-install mode, local model import and explicit hardware profiles. Native and browser engines do not have identical capabilities. Full Mistral 7B Windows/Radeon operation has not been qualified by these tests.

## A useful first chat model

[Mistral 7B Instruct v0.3, official model card](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) is a useful first model to consider for Nexus AI when the chosen backend supports its exact architecture, tokenizer and quantization. The official model card distributes Safetensors, not a ready-to-load GGUF: select a trustworthy compatible GGUF conversion for the GGUF loader, check its provenance and license, and validate loading before calling the model ready. Do not download every Safetensors shard expecting the GGUF loader to accept it.

Radeon RX 7900 XT and XTX nominal VRAM specifications are 20 GB and 24 GB respectively; these are not guaranteed available budgets. Runtime allocations, context/KV cache and other processes reduce usable capacity. A manual profile is a declared configuration, not hardware detection or a benchmark result.

## Start and inspect the original project

Use the exact launch instructions accompanying the matching release package. The [preserved previous README](docs/README_PREVIOUS.md) contains the original workflow, research citations, credits, downloads and limitations. Treat its release-specific statements as historical; this staged update does not silently replace its software or relicense dependencies.

## Evidence and licensing

Developed by Rich Dunbar / Nexus Emerging Technology with AI-assisted coding. Retain existing licenses, attribution and third-party notices. No additional Windows, physical GPU, device-write or model-quality qualification is claimed by this documentation refresh. No live browser-trial deployment is created by this README.

### Historical SmolLM2 CPU inference evidence

The Candidate24 baseline was exercised through its real HTTP import/load/chat-streaming routes with a SHA256-verified SmolLM2-135M-Instruct Q8_0 GGUF using its independent Nexus.cpp CPU engine. A bounded CPU optimization removes repeated per-weight format dispatch for F32/Q8_0 and skips unused intermediate prefill vocabulary projections. The paired real-model request produced identical token IDs and text; 26 synthetic before/after comparisons preserved exact full logits.

See [the profiling report](docs/SMOLLM2_CPU_FINDINGS.md) and [raw evidence](qualification/smollm2_cpu/results/SUMMARY.json). Timing was highly variable on the shared cloud CPU, so the single before/after pair is diagnostic, not a reliable speedup or hardware benchmark. Candidate25 preserves the optimization but also changes the native conversation runtime. Existing native binaries must be rebuilt to gain its new features; the historical timing/parity evidence does not qualify the complete Candidate25 source. No Radeon HIP, WebGPU or Windows performance qualification is implied.

## Candidate25 hardening and installation

Native protocol 3 adds explicit conversation-session prefix caching, cooperative Stop and New Chat reset while retaining loaded weights where supported. New native min-p/repetition controls, actual-capability settings, bounded metrics/diagnostics, continuing rotating logs and durable registry recovery are included. Native batch remains one token per step; native Flash Attention and reduced-precision KV are not implemented.

Keep all files in this directory together. Run `python Install_Nexus_AI.py --cli` or the equivalent release-local `python installer.py --cli`; review the plan before typing INSTALL. `--no-launch` installs without opening the app. Fresh install does not import saved workspace data; Update preserves it and creates a rollback backup. See [README_FIRST.txt](README_FIRST.txt), [the Word guide](Nexus_AI_Readme.docx), [readiness and outstanding gates](ENTERPRISE_READINESS.md), and [reproduction instructions](RELEASE_REPRODUCTION.md).

The producer's Candidate25 logs report 495 Python passes/1 skip, 71 native passes/1 skip, 15 tokenizer passes/2 skips, 37 successful web scripts and three launcher/HTTP/native integration passes. These are test executions, not unique behaviors. [The producer receipt](RELEASE_VALIDATION.json) is distinct from [this package's focused integration checks](CANDIDATE25_INTEGRATION_VALIDATION.json). Neither is Windows/Radeon, enterprise, universal-model or full-model performance approval.

Focused integration checks passed: 65 Python test executions across installer/recovery, new native conversation/runtime and numerical sampler/prefill checks, plus seven browser scripts. Fresh/update/no-launch package checks verified all 408 payload hashes. This narrower rerun is separate from the producer's full regression logs and is not target-platform approval.
