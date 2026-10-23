# Nexus AI

**Version 25**

A local AI workspace for importing supported language models and running chat through the custom WebGPU or Nexus.cpp inference engine.

**[Download the full application](releases/Candidate25/)** · [Installation guide](releases/Candidate25/README_FIRST.txt) · [Wiki](https://github.com/RDunbar01/Nexus-AI-Studio/wiki)

Nexus AI needs its local service and complete application package. This version is not a standalone hosted HTML trial. The existing release directory keeps its `Candidate25` identifier so published downloads and hashes remain valid; the product name is **Nexus AI**.

## What it does

- Imports local models and checks the selected engine's architecture, tokenizer and quantization support.
- Provides local chat, explicit hardware profiles and capability-aware controls.
- Supports cooperative Stop, New Chat reset, session-scoped prefix caching and min-p/repetition controls through native protocol 3.
- Records bounded diagnostics, rotating logs and registry-recovery information.
- Keeps model admission, loaded weights, server health and chat readiness separate.

## Engineering contribution

Nexus AI brings custom browser and native inference paths into one local workspace. Its contribution is the integration of model checks, controllable conversation state and inspectable diagnostics, rather than a claim that every model or GPU is supported.

The engines have different capabilities. An existing native executable must be rebuilt for protocol 3 features. Native batch remains one token per step; native Flash Attention and reduced-precision KV are not implemented in this release.

## Install and run

1. Download every file in [releases/Candidate25](releases/Candidate25/), preserving the supplied layout.
2. Keep both numbered data files with `Nexus_AI_Manifest.json`, the installer, GUI, artwork and dependency helper.
3. Run [Install_Nexus_AI.py](releases/Candidate25/Install_Nexus_AI.py) with **CPython 3.10 or later**. The recorded Linux checks used Python **3.12.14**. Review the installation plan before confirming. The command-line option is `python Install_Nexus_AI.py --cli`; `--no-launch` installs without opening the app.

The optional desktop window uses `pywebview>=5,<7`. Browser GPU work needs a compatible WebGPU browser. Nexus.cpp needs a compatible built executable and the appropriate compiler, HIP and driver setup for Radeon acceleration. Nexus AI uses its own inference engines, **not a PyTorch backend**.

Each distributed data part is at most 10,000,000 bytes; every individual distribution file is below 20,000,000 bytes. The installed application and downloaded model weights can be larger.

## A first model to consider

[Mistral 7B Instruct v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) is a useful first chat model to consider when the chosen engine supports its exact format. The official model card distributes Safetensors; the GGUF loader needs a trustworthy, compatible GGUF conversion instead. Check provenance, license and a successful load before using it.

RX 7900 XT and XTX profiles use their nominal 20 GB and 24 GB VRAM capacities. Available memory is lower once other processes, runtime allocations and context/KV cache are included. Selecting a profile is not a benchmark result. Full Mistral 7B operation on Windows/Radeon has not been qualified by the recorded tests.

## Validation and technical detail

The package includes [producer regression results](releases/Candidate25/RELEASE_VALIDATION.json), [focused integration checks](releases/Candidate25/CANDIDATE25_INTEGRATION_VALIDATION.json), [readiness boundaries](releases/Candidate25/ENTERPRISE_READINESS.md) and a [Word guide](releases/Candidate25/Nexus_AI_Readme.docx). Focused checks covered installer/recovery behavior, native conversation controls, sampler/prefill behavior and all 408 payload hashes.

These are scoped software checks, not enterprise certification, physical Windows/Radeon qualification or a guarantee of model quality and speed. [The previous package](releases/Candidate24/) remains available for rollback.

## Use and attribution

Developed by Rich Dunbar / Nexus Emerging Technology. Personal use and internal commercial testing and evaluation are permitted for Nexus-owned material. Distribution, modification, production deployment and other commercial use require express written consent. Third-party licenses and previously granted rights remain unchanged. See the [license](LICENSE) and [evaluation permission](COMMERCIAL_EVALUATION_PERMISSION.md).

[Historical project notes and credits](docs/README_PREVIOUS.md) describe earlier releases; they do not replace the requirements above.
