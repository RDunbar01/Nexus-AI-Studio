# Release packaging plan and integrity gates

This plan does not publish or upload anything. The requested deliverable is a local **`NexusAI.html` plus offline expression `assets/` folder**, with notices and a separate reproducible source/test/documentation package. Check [RELEASE_STATUS.md](RELEASE_STATUS.md) before treating a directory or ZIP as final.

## 1. Freeze before promotion

- Integrate all approved feature patches and finish current scoped QA.
- Freeze `src/NexusAI_compressed_candidate.html`; record its full SHA-256 and size.
- Run the final aggregate/component checks against that exact snapshot, recording failures/skips and narrow evidence scope.
- Regenerate the expression worker from the same patch source. Verify its bytes/hash equal the worker spec embedded in the frozen HTML, and verify every manifest-listed runtime/model asset.
- Only after the integrator explicitly freezes the candidate, copy those exact bytes to the release's `NexusAI.html`. Never copy the historical root HTML as the new release.
- Compare candidate/promoted hashes, then create the release manifest. A runtime edit or source rebuild after this point requires a fresh freeze and affected tests.

## 2. Runtime layout

- `NexusAI.html` — final promoted candidate
- `README.md`, `docs/`, and a concise release-status/evidence summary (keep local documentation links usable)
- `assets/pretrained_manifest.json`
- `assets/workers/expression_worker.js` — regenerated exact worker
- `assets/models/face_detection_yunet_2023mar.onnx`
- `assets/models/facial_expression_recognition_mobilefacenet_2022july.onnx`
- `assets/runtime/ort.wasm.min.mjs`
- `assets/runtime/ort-wasm-simd-threaded.mjs`
- `assets/runtime/ort-wasm-simd-threaded.wasm`
- `licenses/` — exact six expression/runtime notices and license-evidence declaration
- A generated inventory/checksum file with relative paths, byte sizes and SHA-256 values

Use the strict `package_assets(destination)` helper in `patches/expression/apply.py`, then verify the result. A clean staging directory must contain no old scene/identity packs or extra executable sidecars. Keep the folder structure intact when unzipping. Direct-file use selects the supplied `assets` folder explicitly; localhost is an alternative for browsers with file-origin restrictions. Neither route is represented as physically browser-tested here.

The two small expression checkpoints are the only bundled pretrained weights. No language-model GGUF/Safetensors, downloaded 7B/14B/20B/24B/27B/120B weights, original compression proof models, private user models, or automatic model download is part of the runtime release.

## 3. Reproducible source/test/documentation package

Include the exact source needed to rebuild the HTML, with the runtime asset bundle supplied alongside it or included if it fits the delivery limit. Aim for a source/QA ZIP below 25 MB without weakening the retained evidence. The source package contains:

- `src/`, `patches/`, `scripts/`, and required provenance inputs
- `tests/`, checked-in deterministic/synthetic fixtures, and their generators
- `package.json` / lockfile and test-dependency metadata
- `docs/`, source locks/identities, and a fresh source manifest
- Final hash-bound release receipts plus a clearly labeled selection of component evidence and source provenance

Exclude `node_modules`, virtual environments, `.git`, caches, scratch logs, temporary transport/native-helper environments, duplicate historical HTML snapshots, unrelated projects, and unneeded large generated logit/weight arrays. Public tokenizer/configuration fixtures are metadata, not model weights; include only what the retained tests/generators need and preserve applicable source/license notices.

Tiny generated numeric GGUF fixtures may be included solely as clearly labeled synthetic test data when required by retained tests. Do not mistake a real checkpoint/header prefix containing weight bytes for a synthetic fixture. The real Gemma checkpoint prefix `patches/gemma/upstream/gemma3_27b_qat_header.bin` is explicitly excluded: tensor data starts at byte 6,563,008, so its 8 MiB prefix contains 1,825,600 actual weight bytes. Also exclude `qa/gemma/target_tokenizer_only.gguf`: its zero-tensor directory does not remove the original payload suffix from its bytes. Keep `qa/gemma/target_meta.json`, `target_directory.json`, the metadata receipt, provenance and schema references instead. The retained normal geometry/router tests use `qa/gemma/metadata_fixtures.cjs` with recorded metadata/directory JSON and a synthetic Smol directory. The optional raw-header comparison requires an explicit external `NEXUS_GEMMA_HEADER`; document that narrower step as unrun without the input, rather than silently downloading it. Other large real-file proof fixtures remain external, named by their public model identity/hash in the tests, and their missing tests must skip or explain their dependency. A source archive must not silently claim those absent real-model tests were reproduced by extracting it.

For a smaller source archive, omit the generated `src/NexusAI_compressed_candidate.html` (recreated by the build) and generator-only full upstream tokenizer copies under `patches/mistral/upstream`, while retaining required ordinary-test metadata and the wrong-order Jinja fixture. Keep `input/NexusAI_a59480b7.html`: the normal compressed-host test checks teacher-byte preservation against it. These omissions must not break the clean-extraction build or normal release suite; a larger archive or separate source parts is preferable to dropping essential inputs. Document optional reference/generator inputs separately and never fetch them automatically.

Keep package paths relative and generic. Do not include user workspace backups, conversation/memory stores, credentials, machine inventories, personal model-folder screenshots, or private filenames. Inspect receipts and copied test logs for local user paths before inclusion. When producing a shareable receipt derived from a raw receipt, preserve the original evidence identity and explicitly label any path-only redaction; never silently alter a source-bound raw receipt and retain its old hash.

## 4. Package verification

1. List every archive entry, reject traversal/absolute paths, duplicates and unexpected weight/pack files.
2. Compare extracted byte sizes/SHA-256 values with the inventory. Check the promoted HTML equals the frozen candidate and the worker equals its embedded spec.
3. Rebuild from a clean extraction using declared dependencies and verify identical output where the builder is deterministic. Run the retained core/host/lifecycle checks against the extracted final HTML, not a worktree fallback.
4. Check every relative README/doc link and required script/fixture input. A missing optional external reference dependency is documented; a missing required shipped file blocks packaging.
5. Record final ZIP size and SHA-256, the included checks and their outcomes, and explicit omissions/unrun browser/hardware/model qualification.

Do not invent a download URL. Do not publish, push, upload, create remote releases, accept new model licenses, or download language-model weights as part of this plan. Artifact delivery/publication requires the parent task's authorized workflow.

## 5. License statement

Application code currently declares `UNLICENSED`; this packaging step grants no new free/open-source/commercial license. Existing MIT/Apache texts apply only to their corresponding components and do not automatically clear checkpoint training data, biometric deployment, procurement, export, or every commercial use. Preserve the FER model-specific license-evidence caveat and unresolved exact training-data rights/provenance. Choose an application license separately before public source publication.
