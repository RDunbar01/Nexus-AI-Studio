# Nexus AI

> Draft documentation staging: application packages and browser HTML are pending a later verified commit. Any proposed version or trial path below is not a shipped release or live trial. Do not merge until package and link checks pass.

**Next-release documentation staging · not a published application update**

Local AI workspace with separate custom WebGPU and Nexus.cpp paths. Model admission, resident weights, server health and chat readiness are separate states. A compatible tokenizer, architecture and quantization are required for the selected engine.

## Current baseline and release status

Verified baseline: **Candidate 23**. Next identifier: **Candidate 24**. Do not tag or label a binary with a new version until its application, installer and package metadata agree.

Current audited source includes plain chat with no automatic past-workspace retrieval, stale-reply cancellation, isolated fresh-install mode, local model import and explicit hardware profiles. Native and browser engines do not have identical capabilities. Full Mistral 7B Windows/Radeon operation has not been qualified by these tests.

## A useful first chat model

[Mistral 7B Instruct v0.3, official model card](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) is a useful first model to consider for Nexus AI when the chosen backend supports its exact architecture, tokenizer and quantization. The official model card distributes Safetensors, not a ready-to-load GGUF: select a trustworthy compatible GGUF conversion for the GGUF loader, check its provenance and license, and validate loading before calling the model ready. Do not download every Safetensors shard expecting the GGUF loader to accept it.

Radeon RX 7900 XT and XTX nominal VRAM specifications are 20 GB and 24 GB respectively; these are not guaranteed available budgets. Runtime allocations, context/KV cache and other processes reduce usable capacity. A manual profile is a declared configuration, not hardware detection or a benchmark result.

## Start and inspect the original project

Use the exact launch instructions accompanying the matching release package. The [preserved previous README](docs/README_PREVIOUS.md) contains the original workflow, research citations, credits, downloads and limitations. Treat its release-specific statements as historical; this staged update does not silently replace its software or relicense dependencies.

## Evidence and licensing

Developed by Rich Dunbar / Nexus Emerging Technology with AI-assisted coding. Retain existing licenses, attribution and third-party notices. No additional Windows, physical GPU, device-write or model-quality qualification is claimed by this documentation refresh. No live browser-trial deployment is created by this README.
