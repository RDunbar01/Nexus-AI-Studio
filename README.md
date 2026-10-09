# NexusAI

An experimental local-first model studio for local chat, workspace memory, approved-correction learning, voice, and optional expression cues. Language-model inference uses a custom WebGPU engine. Language-model weights are separate from the application and are not included or downloaded automatically.

**Experimental preview release:** consult [release status](docs/RELEASE_STATUS.md) for the accepted HTML identity and test results. The packaged HTML is the exact tested composition. [Capabilities and model formats](docs/CAPABILITIES.md) distinguish implemented paths from actual checkpoint and hardware qualification. There is no “all versions,” answer-accuracy, or Radeon-performance guarantee.

## Open the app

1. Export an existing workspace backup before replacing the app or changing its browser origin.
2. Extract the complete release into a dedicated folder. Keep `NexusAI.html`, `assets/`, and `licenses/` together. The HTML contains the application; the small offline expression feature uses the supplied sidecars.
3. Open `NexusAI.html` in a WebGPU-capable browser. For expression processing from a directly opened file, use **Settings → Expression → Choose local assets folder…** and select the supplied `assets` folder. The app checks every required model/runtime/worker file's size and SHA-256 before use. Choosing files does not start processing or the camera.
4. If browser security or file-origin restrictions prevent a feature, serve the same folder locally: `python -m http.server 8000 --bind 127.0.0.1`, then open `http://localhost:8000/NexusAI.html`. Stop the server with Ctrl+C. Do not disable browser security to force a pass. Actual browser/file-origin behavior still needs device qualification.
5. Keep strict offline mode enabled for local-only use. Check the selected adapter and enter actual GPU capacity in the UI's GiB units. Start with a compatible small local GGUF, such as the tested SmolLM2-135M-Instruct F16 or Q8_0 profile. Admission checks the file's metadata, complete tensor inventory, tokenizer, layout, and memory limits.

Browser storage belongs to the browser profile and origin. Moving from a file to localhost, changing ports, or switching browsers can produce a different workspace. Keep an exported backup; local browser storage is not an independent backup.

## Five-minute first run

You can try the preview without completing the full qualification checklist:

1. Load your local SmolLM2-135M-Instruct Q8_0 file with strict offline mode on.
2. Send one short prompt. Interrupt generation, then send a second prompt to check that the old response does not continue.
3. Export a workspace backup and keep it outside browser storage.
4. If wanted, try the microphone by itself, then stop it. Try the expression camera separately after selecting the assets and granting the separate consent/processing controls. Neither is required for text chat.

If something fails, send the visible error/status text or a screenshot, app HTML hash, public model filename/quantization, browser/OS version, selected GPU, declared GPU/RAM settings, context size, and whether streaming was enabled. Say which step failed and whether retrying changed it. No model upload or full benchmark report is needed; omit API keys and private chat content. The longer [device test plan](docs/RADEON_TEST_PLAN.md) is for systematic correctness/performance qualification.

## Models and memory

Implemented experimental paths include SmolLM/SmolLM2, the inspected Mistral/Ministral dense text profiles, Gemma3 text, GPT-oss MoE, and the exact inspected Qwen2.5-VL-7B text/image profile. Each has different accepted formats and evidence. Gemma generations other than Gemma3, Mistral image encoders, unrelated Qwen variants, arbitrary Jinja templates, and unsupported quantization layouts do not become supported because a folder or filename looks familiar.

Qwen image input requires a separately selected matching local `qwen2.5vl_merger` GGUF companion. Its image route is independent of the expression camera and has bounded still-image input. See [Qwen-VL status](docs/QWEN_VL_STATUS.md).

GPU-only is the default weight-placement policy. Optional RAM-backed streaming caches quantized bytes in a bounded host cache and uploads weight tiles for GPU computation. It requires a truthful installed-RAM declaration; it is not CPU inference, extra VRAM, or a speed/fit guarantee. Leave headroom for the browser, OS, teacher, and other apps. See [memory policy](docs/WEIGHT_STREAMING.md).

**GPT-oss-120B is reserved for upgraded hardware.** The current 20 GiB GPU + 32 GiB RAM profile is insufficient for its standard resident weight set and fails the application's upgrade gate. Streaming does not remove that release restriction. No full 20B/120B, Gemma 27B, Mistral large-model, or Qwen 7B checkpoint has been qualified in a physical browser/GPU run here.

## Expression, voice, and privacy

- Expression processing is optional and default-off. The included YuNet detector and ProgressiveTeacherFER model run in single-threaded ONNX Runtime Web WASM, separate from chat's WebGPU engine. Notice, participant consent, enable, load, and camera capture are separate controls.
- Estimates describe uncertain visible expressions, not internal emotions, identity, health, intentions, or risk. No real-person accuracy or fairness claim is established. [Scope, licenses, and limitations](docs/EXPRESSION_ONLY.md)
- By default, expression labels are UI-only. A separate default-off tone-cue option can include a fresh, uncertain label in local chat context. Frames are not sent to the language model; labels never go to an online provider. Camera-influenced contexts are excluded from automatic adapter-training capture.
- Camera and microphone start independently. Stopping camera capture preserves separately started voice. Ending the session stops both; interrupted or cancelled starts do not silently restart them.
- Browser speech recognition may use an online speech service when strict offline mode is disabled. Strict offline recognition requires browser support and an already installed on-device language pack; there is no online fallback. Browser recognition uses the browser/OS microphone selection; the app's exact-device picker applies to API recorder mode.
- Browser TTS uses voices available on the device/browser. Strict offline mode permits local voices only; it cannot promise a particular voice or naturalness. Online chat/STT/TTS require their separate configured services. [Voice limits and checks](docs/VOICE.md)

Saved chats, names, memories, RAG documents, reviewed corrections, and backups may contain private information. The app's local-only model path is distinct from any explicitly configured online service. Do not share a workspace backup unintentionally.

## End Session learning

End Session saves the conversation, names, and existing approved memories before optional approved-correction training. RAG content and feedback keep their explicit save/review controls. The trainer adapts the **output head** with LoRA-style factors and DPO/positive-answer objectives; it does not fine-tune the full transformer or automatically train every model family.

Promotion requires held-out improvement and separate regression gates. Failed or worse candidates keep the prior adapter. Cancel-and-stay, save-without-training, model-hash-scoped restore, and deletion controls remain available. These narrow tests do not guarantee better factual accuracy or reasoning. [Session learning](docs/SESSION_LEARNING.md)

## Optional model directory/download tools

**Settings → Model Downloads** contacts only the chosen public directory when you explicitly request it. The downloader pins a repository revision and checks declared size and SHA-256 while streaming to a location you select. It sends no conversation, profile, or camera frames and stores no service credentials. Hosting services still see ordinary network information such as your IP address. Review the listed source and license; publisher gates must be completed through the publisher's own process.

A verified transfer establishes integrity, not compatibility, safety, or model quality. Safetensors source repositories are not GGUF files; split, repacked, or unsupported files remain blocked. [Smol formats and download scope](docs/SMOL_RELEASE.md)

## Build and evidence

`python3 scripts/build.py` creates `src/NexusAI_compressed_candidate.html`. Run the build and relevant tests, then promote that exact frozen candidate to `NexusAI.html`; never substitute the old root baseline. `npm ci`, `npm test`, and `npm run test:regressions` cover only part of the verification matrix. See [build instructions](docs/BUILD.md), [release packaging](docs/RELEASE_PACKAGING.md), and the [physical-device test plan](docs/RADEON_TEST_PLAN.md).

Evidence includes Node/vm/jsdom lifecycle tests, real bundled expression ONNX/WASM execution in Node, bounded exact-WGSL synthetic graphs, and two-prefix-position runs of the actual SmolLM2-135M F16/Q8_0 files on a software adapter. No browser was launched and no physical Radeon was tested for this work. Synthetic numerical fixtures do not establish real-checkpoint accuracy or useful speed.

Application code currently declares `UNLICENSED`. A free-use description is not an open-source license grant. Preserve bundled third-party notices and provenance; expression checkpoint/training-data license-evidence caveats remain unresolved. Nothing here grants blanket deployment clearance.
