# Nexus AI Candidate25 readiness

Candidate25 improves the reliability of the existing single-user desktop application. It is a **hardening candidate, not an approved enterprise release**. The application remains an independent Nexus.cpp and browser WebGPU implementation. No llama.cpp runtime has been substituted.

## Implemented in this release

| Change | Result and boundary |
|---|---|
| Native conversation cache | Dense CPU/HIP source reuses only an exact token prefix in the same explicit session. The final prompt token is recomputed for correct logits. Different sessions, unsupported recurrent architectures and calls without a session do not reuse it. |
| Cooperative Stop | Updated native workers check a private request-specific cancellation file during prompt processing and generation. Stop clears the cache and retains weights. Old workers or workers that do not acknowledge within five seconds still require termination/reload. |
| New Chat | Clears native and browser conversation state and rotates the native session ID. It waits for a bounded Stop/reset conflict. Stored conversations remain inactive unless explicitly recalled. |
| Native sampling | Temperature, top-k, top-p, min-p, repetition penalty, bounded repetition window and seed are forwarded and validated. Native DRY remains unsupported. |
| Accurate controls | Unsupported native batch, Flash Attention and sampler controls are disabled. The settings note reports the loaded worker's actual capabilities. Browser preferences are retained. |
| Diagnostics | A downloadable report contains allowlisted configuration and numerical metrics, excluding chat text, model paths and credentials. `/metrics` requires the local token and trusted origin. Metrics cover native chat requests in the current server process. |
| Continuing logs | `state/NexusAI.server.jsonl` rotates at 8 MiB with three backups. `NexusAI.log` retains launcher output and a pointer when server logging moves to its dedicated file. |
| Registry resilience | JSON updates use unique temporary files, fsync and atomic replacement. A validated previous registry generation supports explicit logged recovery. Damaged data is preserved; invalid main and backup copies stop startup without resetting saved data. |
| Installer runtime detection | A prior model-compatible native binary is distinguished from the new conversation runtime. An available existing HIP compiler can rebuild it with backup. Otherwise missing features are reported and old binaries are preserved. |
| Release controls | Source inventory, regression runner, real-model qualification script, current test receipts and continuation tasks ship with the source. State, runtime locks and build outputs are excluded from distribution. |

## What is still missing

Native prompt evaluation still executes one token per step. Native Flash Attention, FP16/quantized KV storage, GPU sampling, Vulkan, partial offload, continuous batching, speculative decoding and multi-GPU execution are not implemented. The eligible browser Mistral graph retains its separate physical-batch and fused-attention implementation; these settings do not accelerate Nexus.cpp.

There is no enterprise identity provider, user/role isolation, remote-service TLS gateway, organizational key management, central audit collector, signed Windows distribution, managed fleet deployment or independently assessed supply-chain process. The loopback desktop service is not a shared multi-user server. The separate native service provides only its documented completion API subset, not complete OpenAI or LM Studio API parity.

Full Mistral 7B and Ministral 14B model quality, current HIP compilation, Windows installation/runtime behavior and Radeon performance remain unqualified for Candidate25. Historical receipts under other qualification folders describe earlier sources and environments. They do not qualify this version.

## Installation and rollback

Extract the complete distribution ZIP and run `Install_Nexus_AI.py` with existing Python. Keep every `.nxd` part, the manifest, GUI files and dependency helper together. The graphical installer uses tkinter from that Python installation. Terminal alternative: `python Install_Nexus_AI.py --cli`.

Choose **Fresh install** for a new workspace with no active saved chats, memories, documents, adapters, settings, model registrations or startup model. An old installation may remain only in the explicitly reported backup; it is not imported. Choose **Update** when you want to retain the current workspace. Close Nexus before replacement. To roll back, close Nexus, retain the failed installation for diagnosis and restore the backup folder to the original install path. Browser-mode storage is separate and is not automatically migrated.

Dependencies are app-local or reused only when the existing installer checks establish compatibility. Python 3.10+ is required by the installer; this release was exercised with Python 3.12. Windows desktop mode needs pywebview 5–6, its Windows Python/.NET dependencies and an existing working WebView2 runtime. Jinja2 3.1.6 or later below 4 provides bounded template rendering; regex supports the required tokenizer patterns. See `installer/dependencies.py` for the authoritative ranges and reuse policy. Existing binaries do not acquire new features from a Python-only update.

No global Python package, driver, compiler, PATH, registry or shared runtime is modified. Native HIP compilation requires an already installed compatible compiler and gfx1100 target; the installer does not supply one. A CPU build is an explicit separate choice through `native/Nexus.cpp/scripts/build.py --backend cpu`.

## Operator checks

1. Confirm the installed worker reports `runtime_revision: nexus-conversation-v1` and protocol 3. Check the actual backend/device before interpreting speed.
2. Load the exact GGUF. A ready application or loaded weights alone do not prove the tokenizer/template is chat-ready.
3. Send two turns, press Stop during generation, then send another turn without reloading. Start New Chat and verify no previous question is supplied.
4. Download diagnostics beside the backend selector. Use the server JSONL log for continuing failures. Error messages in raw logs can contain paths and diagnostic details; review raw logs before sharing them.
5. Benchmark prompt processing and decoding separately. Prefix reuse helps later turns with matching prefixes; it does not eliminate cold prefill or model loading.

## Reproducible local checks

Use an isolated development environment with NumPy, Jinja2 3.1.6, regex, an existing C++17 compiler and Node. Browser DOM tests require jsdom 30 and fake-indexeddb 6; these are development dependencies and are not shipped as app runtime packages. Set `NODE_PATH` to that isolated installation and `JSDOM_PATH` to its jsdom directory if it is outside `/tmp/nexus-dom-tests/node_modules`.

Build the CPU executable using `python native/Nexus.cpp/scripts/build.py --backend cpu`. Build the C ABI shared library with the included CMake project or the documented existing compiler command in `docs/RELEASE_REPRODUCTION.md`. Then run:

```text
python tools/release_check.py --output local-checks
```

The output directory must be new. The runner checks the frozen source hashes and runs Python, native reference, tokenizer and browser suites. It performs no installation and cannot approve an enterprise deployment. Read skip reasons as well as exit codes. Linux CPU fixtures establish numerical/control-flow behavior, not physical GPU or full-model quality.

## Windows Radeon qualification

After building the updated native executable with the existing HIP toolchain, run from the installed app directory using its configured Python:

```text
python tools/qualify_model.py --model "D:\Models\model.gguf" --backend hip --context 4096 --prompt-tokens 512 --decode-tokens 128 --output qualification-model.json
```

Repeat for each exact 7B/14B GGUF and hardware configuration. Use a new output filename each time. This explicitly requested diagnostic hashes the model once for reproducible evidence; normal chat does not add a full-model hash step. It records load time, time to first token, cold prefill/decode timings, session parity/isolation, fresh-chat reset and resident Stop. It fails instead of declaring success if the model, tokenizer, protocol or functional checks fail.

Manually review answer quality, a requested 1000-word essay, long-context behavior and a multi-hour soak. Record accepted latency/throughput targets before approving a deployment. The receipt always retains `enterprise_approved: false`; a benchmark cannot substitute for operational, security, licensing or model-quality review.

## Remaining release gates

- Build and run the current HIP changes on Windows 11 and physical RX7900XT/XTX; retain compiler, driver, binary and model identities.
- Qualify exact Mistral 7B and Ministral 14B GGUF architecture, tokenizer, quantization and context combinations with numerical and human task checks.
- Exercise fresh/update/rollback, redirected Desktop, WebView2 failure and offline dependency handling on clean Windows machines.
- Test extended memory/VRAM stability, cancellation, disk-full and crash recovery on target hardware.
- Establish the organization's required identity, remote access, signing, dependency governance and operational ownership before broader deployment.

The existing personal-use license is unchanged. Organizational/commercial use is not granted by this technical hardening work; consult the included license and rights holder's written permission.
