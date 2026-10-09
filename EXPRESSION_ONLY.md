# Expression-only local feature

This edition replaces the general-purpose NexusVision implementation with a bounded facial-expression feature. It preserves normal chat and voice. Camera controls are separate: opening the camera no longer starts the microphone or a voice session, and stopping camera preview does not end voice.

## Included weights and runtime

Only these two model files are distributed:

| Purpose | Model file | Bytes | SHA-256 |
|---|---|---:|---|
| Face location + five landmarks | face_detection_yunet_2023mar.onnx | 232,589 | 8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4 |
| Visible-expression scores | facial_expression_recognition_mobilefacenet_2022july.onnx | 4,791,892 | 4f61307602fc089ce20488a31d4e4614e3c9753a7d6c41578c854858b183e1a9 |

The second model is the OpenCV-distributed ProgressiveTeacherFER using a MobileFaceNet backbone. Its seven upstream classes are angry, disgust, fearful, happy, neutral, sad and surprised. The UI describes these as tentative appearance labels such as “happy-like” and “surprise-like.” Surprise is never relabeled excitement.

The included ONNX Runtime Web version is 1.22.0, with precisely `ort.wasm.min.mjs`, `ort-wasm-simd-threaded.mjs` and `ort-wasm-simd-threaded.wasm`. It runs single-threaded WASM CPU inference in a dedicated worker. Chat's WebGPU runtime is separate and unchanged by this patch. The app-owned expression worker and every runtime/model byte are SHA-256 checked before use. A directly opened HTML uses the explicit “Choose local assets folder…” control to read the supplied sidecars as local files. A localhost/HTTPS deployment can load same-origin assets with redirects forbidden. Neither route has a CDN fallback; selecting the folder does not start processing or the camera.

Exact source URLs, pinned upstream revisions, file sizes and digests are in `assets/pretrained_manifest.json`. These bytes were copied from the previously recovered local expression bundle. No new model weights were fetched or altered.

## Removed scope

The general identity, neural embedding, scene/object/animal, enrollment, gallery/vault, calibration-training, and optional-pack implementations are removed from the generated application. SFace, YOLOX, TopoFR, POSTER and ResEmoteNet are not included. There is no optional-pack importer or scene manifest. YuNet face detection is necessary to locate the input crop, and does not recognize who a person is.

The old online camera snapshot uploader is also removed. Disabled, hidden compatibility fields remain so that old ordinary settings can be read without breaking chat/voice. These fields cannot start uploads. Expression results are displayed locally by default. A separate session-only, default-off option can include a fresh uncertain label in local chat to gently adjust tone. This option never sends frames to the language model and never sends labels to an online provider. An explicit self-reported mood takes priority; stale, unknown, or unconsented estimates are omitted. Camera-influenced context is excluded from automatic adapter-training capture and is not retained as a fact about the user. This does not disable separately configured online text chat or speech services.

## Consent and lifecycle

- Startup does not fetch models, create workers, enable processing or request a camera.
- Notice acceptance, informed participant consent, enabling processing, loading local models, and starting camera capture are separate steps.
- Consent is session-only and never imported or restored from saved settings.
- The user should be alone in frame. Multiple detected faces, no face, poor heuristic crop quality, invalid output, stale output, and ambiguous scores cause an unknown result. Detection necessarily sees an image before discovering whether other people are present and may miss them.
- A label requires a top model score at least 0.65, a top-two margin at least 0.15, and two consecutive matching estimates. These are conservative application heuristics, not accuracy calibration.
- Results expire after five seconds. Foreground chat generation pauses inference. Only one frame is in flight at a time.
- Stop, consent revocation, disabling processing, hidden tab, lock, settings restore, context reset, page hide or session end clear results, release this camera lease and terminate the worker. A late permission grant is released; a late fetch or inference result cannot restart work.
- The explicit “Stop camera and clear results” control stops all camera owners. A hidden tab also stops all camera capture. The existing main preview may otherwise hold its own separately requested lease.
- “Keep this expression camera on while chatting” is an additional session-only opt-in. Otherwise leaving its Settings panel stops it. It does not itself enable tone-cue sharing; that requires the separate local-only opt-in.
- No frames, face templates or expression results are intentionally persisted by this feature. Transient canvas pixels are cleared and transferred worker pixels are zeroed after use. Browser/OS memory behavior is outside this guarantee; secure physical erasure is not claimed.

## Licenses and deployment limitations

YuNet's preserved model-directory declaration is MIT. ProgressiveTeacherFER has an upstream Apache-2.0 directory/model-card declaration; the exact model-specific LICENSE retrieval was unavailable in the earlier provenance review. Preserved Apache text and `FER-license-declaration.md` do not resolve that checkpoint-specific evidence gap. ONNX Runtime Web is MIT and carries third-party notices. Preserve the entire included `licenses/` directory when redistributing; MIT and Apache-2.0 have notice obligations. See the included texts for their actual terms.

Exact training-data rights/provenance remain unresolved. No blanket commercial, military, procurement, biometric-privacy, export or operational clearance is claimed. These notes are a record of evidence, not legal clearance. An intended deployment needs its own competent review.

Visible-expression estimates do not establish internal emotions, mental health, intentions, truthfulness, personality or dangerousness. Model scores are not calibrated probabilities. No real-person accuracy, demographic fairness, medical suitability, security value or high-impact decision suitability is established. Do not use this feature for diagnosis, employment/educational or eligibility judgments, targeting, surveillance or security decisions. These are application use boundaries, distinct from upstream license terms.

## Build and verification

Apply `patches/expression/apply.py` after compatibility, GPU and compressed patches. It count-checks its integration anchors and rejects leftover general-purpose vision module identifiers. Call `package_assets(destination)` from that module to copy the exact whitelisted assets and notices into a new or cleaned release directory. Do not copy the old starter's assets or packs wholesale. For a directly opened HTML, select the supplied `assets` folder with the local-folder control. Alternatively, serve the complete folder over localhost or HTTPS. A lone HTML file does not contain the model/runtime sidecars. Regenerate the worker from the same source as the frozen HTML and verify its embedded size/hash; a historical worker is not interchangeable.

Focused checks:

- `node --test tests/expression_only.cjs` (set `NEXUS_EXPRESSION_HTML` to the final composed HTML if it is not `qa/expression_candidate.html`)
- `node tests/expression_runtime.mjs`

`qa/expression_only.tap` covers default-off DOM startup, consent/enable/load/capture independence, repeated actions, delayed capture cancellation, hidden-tab cleanup, hash rejection, cancelled load, state restoration, bounded score handling and excluded modules/assets. `qa/expression_runtime.json` records actual bundled WASM sessions loading both actual ONNX files, graph input/output shape checks, finite zero-tensor outputs and non-face abstention through the specialized adapter. These checks do not establish live-browser camera operation, real-face accuracy or GPU inference. The final focused audit `qa/adversarial_upgrade/final_integration/receipt.json` passes 37 tests against the frozen release HTML and regenerated worker, including exact source/worker bindings and actual native File clones through the bundled WASM worker path. Browser Blob-module import is adapted to Node, so it is not a browser execution pass. A real camera/browser smoke remains unrun; no browser was launched during this implementation.
