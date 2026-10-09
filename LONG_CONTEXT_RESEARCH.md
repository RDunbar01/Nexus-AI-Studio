# Guarded long-context validation status

Updated after the original plan: all host/mock steps and separate native attention/RoPE/KV boundary fixtures passed. Production v2.1 now permits explicitly requested contexts128/512/2048; default and benchmark context remain128. Model metadata context8192 and the350MiB explicit-buffer budget are guarded. Contexts above2048 are rejected. Full-model beyond128, JavaScript browser and Radeon execution remain unperformed. See validation/guarded_context_tests.json and validation/native_long_attention_fixtures.json.

The following original plan is retained as historical review evidence.

# Separate long-context validation plan

The 128-position production cap is a deliberate tested-host contract, not a hard limit of the attention or matvec shader algorithms. The frozen before/after PPL protocol and v1 remain unchanged.

Candidate contexts: 512 and 2048. Promotion requires all items below and an explicit versioned change; current graph rejects positions above 127.

1. Host candidate allocates K/V and scores using requested context, bounded to model metadata, adapter limits and the 350 MiB explicit-buffer budget. Step positions are integer, sequential, non-repeated and below context. No wraparound, silent truncation or old KV reuse.
2. Compare every uploaded FP32 RoPE coefficient at positions 0 through 2047 with independent Python FP64 angle/trig rounded to FP32; no change to theta, pairing, scaling or norm settings.
3. Mock attention dispatch/binding checks at positions 0, 127, 128, 255, 256, 511 and 2047. Confirm last valid addresses and rejection at context; no GPU claims from mocks.
4. Reconcile exact ledgers: K+V across 30 layers occupy 23,040 bytes per context token; scores occupy 36 bytes per context token. Relative to 128, context 512 adds 8,861,184 bytes and context 2048 adds 44,305,920 bytes. Largest raw F16 path would use 281,353,248 and 316,797,984 explicit bytes respectively, including readback.
5. Ask the native GPU validator to run bounded attention/RoPE fixtures at those boundaries, plus a raw/direct same-backend numerical check, without interrupting the frozen full PPL run. Use original F16 and recovered Q8 kernel identities separately.
6. Preserve the distinction between native fixture coverage, JavaScript/browser execution, Radeon execution and a full longer-context PPL evaluation. Only enable larger chat context after the required fixtures pass. No full-corpus benchmark claim follows from longer buffers.

No production higher-context option has been enabled by this plan.
