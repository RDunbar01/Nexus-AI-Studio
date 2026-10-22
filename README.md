# Nexus AI

## Current release licensing

This Nexus release is not offered under Apache License 2.0. Nexus-owned software may be used only for personal, non-commercial purposes. Any other use, including commercial use, modification or redistribution, requires express written consent from the rights holder. Third-party code, models, datasets and separately licensed components retain their own licenses and notices. Previously granted rights and rights that cannot lawfully be restricted remain unchanged.


> The reviewed Candidate25 installer and complete data-part set are available below. Repository availability is not a live browser deployment or Windows/Radeon qualification.

**Candidate25 · single-user hardening candidate**

Local AI workspace with separate custom WebGPU and Nexus.cpp paths. Model admission, resident weights, server health and chat readiness are separate states. A compatible tokenizer, architecture and quantization are required for the selected engine.

## Start locally: Python and browser requirements

Candidate25 requires the **full download and local loopback service**, including every matching installer/data component. Its HTML is not an approved standalone browser trial, and the existing project Pages site must not be presented as a live Candidate25 app.

Use **CPython 3.10 or later** for the installer and launcher; the recorded Linux checks used Python **3.12.14**, not every possible later version. The optional desktop window requires the package's declared `pywebview>=5,<7` runtime. A compatible browser with WebGPU is needed for the custom browser GPU engine. Native Nexus.cpp additionally needs a compatible built executable and, for Radeon acceleration, the supported compiler/HIP/driver setup.

Nexus AI uses its own **WebGPU and Nexus.cpp engines, not a PyTorch backend**. Python does not run inside the browser HTML. Do not treat GPU detection or a selected hardware profile as model compatibility, successful inference or measured performance. Physical Windows/Radeon/WebGPU and full-model qualification remain outstanding.

## Current baseline and release status

Verified starting baseline: **Candidate24**. Candidate25 adds single-user hardening; it is not an enterprise-approved release. [Candidate24](releases/Candidate24) remains unchanged for review and rollback. Current Windows, HIP and physical Radeon/WebGPU qualification remain outstanding.

Current audited source includes plain chat with no automatic past-workspace retrieval, stale-reply cancellation, isolated fresh-install mode, local model import and explicit hardware profiles. Native and browser engines do not have identical capabilities. Full Mistral 7B Windows/Radeon operation has not been qualified by these tests.

## A useful first chat model

[Mistral 7B Instruct v0.3, official model card](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) is a useful first model to consider for Nexus AI when the chosen backend supports its exact architecture, tokenizer and quantization. The official model card distributes Safetensors, not a ready-to-load GGUF: select a trustworthy compatible GGUF conversion for the GGUF loader, check its provenance and license, and validate loading before calling the model ready. Do not download every Safetensors shard expecting the GGUF loader to accept it.

Radeon RX 7900 XT and XTX nominal VRAM specifications are 20 GB and 24 GB respectively; these are not guaranteed available budgets. Runtime allocations, context/KV cache and other processes reduce usable capacity. A manual profile is a declared configuration, not hardware detection or a benchmark result.

## Install Candidate25

Download all files in [releases/Candidate25](releases/Candidate25), retaining the directory structure. Keep both Nexus_AI_Data_001.nxd and Nexus_AI_Data_002.nxd with Nexus_AI_Manifest.json, the installer, GUI, artwork and dependency helper. Each data part is at most 10,000,000 bytes. With Python 3.10+ already installed, run [Install_Nexus_AI.py](releases/Candidate25/Install_Nexus_AI.py); terminal fallback: python Install_Nexus_AI.py --cli. Review the displayed installation plan before confirming. Use --no-launch to install without opening the app. See [README_FIRST.txt](releases/Candidate25/README_FIRST.txt) and [the package README](releases/Candidate25/README.md). The app source and HTML are carried in the verified data parts, not deployed as a live browser trial.

The package includes its exact inventory, license scope, producer validation and a separate focused integration-check receipt. Local Linux checks do not qualify native Windows execution, physical Radeon/WebGPU hardware or full-model quality/performance.

## Candidate25 changes and evidence

Native protocol 3 adds session-scoped prefix caching, cooperative Stop, New Chat reset and min-p/repetition controls. The update also adds capability-aware controls, bounded metrics/diagnostics, continuing rotating logs, durable registry recovery and detection of an outdated native runtime. An existing native executable must be rebuilt to gain the new conversation features. Native batch remains one token per step; native Flash Attention and reduced-precision KV are not implemented.

The producer's regression logs report 495 Python passes/1 skip, 71 native passes/1 skip, 15 tokenizer passes/2 skips, 37 successful web scripts and three launcher/HTTP/native integration passes. These counts describe test executions, not unique behaviors. See [the producer validation](releases/Candidate25/RELEASE_VALIDATION.json), [focused package integration checks](releases/Candidate25/CANDIDATE25_INTEGRATION_VALIDATION.json), [readiness boundaries](releases/Candidate25/ENTERPRISE_READINESS.md), and [the Word guide](releases/Candidate25/Nexus_AI_Readme.docx). The prior browser benchmark-save correction and CPU optimization are retained, but historical receipts do not qualify the full Candidate25 source.

## Start and inspect the original project

Use the exact launch instructions accompanying the matching release package. The [preserved previous README](docs/README_PREVIOUS.md) contains the original workflow, research citations, credits, downloads and limitations. Treat its release-specific statements as historical; this update does not silently replace its software or relicense dependencies.

## Evidence and licensing

Developed by Rich Dunbar / Nexus Emerging Technology with AI-assisted coding. Retain existing licenses, attribution and third-party notices. No additional Windows, physical GPU, device-write or model-quality qualification is claimed by this documentation refresh. No live browser-trial deployment is created by this README.


Focused integration checks passed: 65 Python test executions across installer/recovery, new native conversation/runtime and numerical sampler/prefill checks, plus seven browser scripts. Fresh/update/no-launch package checks verified all 408 payload hashes. This narrower rerun is separate from the producer's full regression logs and is not target-platform approval.
