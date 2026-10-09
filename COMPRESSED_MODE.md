# Direct compressed mode

Choose Model representation → Experimental direct compressed, then choose the matching local compressed file produced by Nexus ZLC. The frozen F16 baseline currently admits exactly the reference model identified in the shared backend, under a128-position context limit. Default reply length is32 tokens; prompt plus reply must fit. Longer chat and other models are not inferred from the bounded validation.

Static application WGSL reads numerical dictionary/reference packets in GPU memory. The tokenizer receives only the original GGUF metadata prefix. Attempts to read an expanded weight tensor fail. No full restored matrix buffer is created by this path. Small original norm vectors may be reconstructed. Current allocation reports separate owned buffers from unmeasured physical VRAM.

The original GGUF/NHSC route remains available. NHSC's existing host decoding does not satisfy the direct compressed representation claim; select the explicit experimental mode for that path. Mode changes unload current model state. The embedded teacher remains byte-identical to the recovered baseline and refuses compressed model files.

Output-head extraction/training, sequence-adapter training and learned-adapter generation reject explicitly in experimental compressed mode. Saved feedback, checkpoints, participant galleries and the encrypted vault are not deleted. Return to Original mode for the established learning flows. Base-model before/after PPL in Nexus ZLC has adapters, sampling and logit filters disabled.

Recovery identity: this is a newly reconstructed build with new hashes and fresh tests, not byte-exact restoration of the lost d06/52fe release. No browser execution, Radeon performance, sustained speed or general numerical-parity claim is made. Model files contain data only and cannot provide executable kernels.

Q8 direct chat and PPL remain disabled in this staged build. Q8 compression/restore is available in Nexus ZLC, and native scalar/matvec/gather kernel checks passed, but the agreed promotion gate requires a fresh actual full-model graph/output-head comparison. A later gate change needs a new artifact hash and fresh composed checks. The shared graph has separately tested 512/2048 context guards and native attention fixtures; this application intentionally remains capped at 128 until broader full-model qualification.
