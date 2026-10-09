# NHD1 direct Q8 kernel contract

NHDMOD1 global header is 64 bytes: magic `NHDMOD1\0` at byte0, u64 manifest
offset at8, u64 length at16, SHA-256 manifest bytes24..55, reserved zero56..63.
The JSON manifest and per-region SHA fields are specified by `inspect()`.
Regions reconstruct the complete original GGUF byte layout. Only Restore does so.

Each NHD1 matrix packet begins with sixteen little-endian u32 words:

0 magic bytes `NHD1`; 1 version1; 2 rows; 3 columns; 4 Q8 block count;
5 scale mode (0 literal,1 dictionary); 6 fixed-width scale-ID bits;
7 scale entry count; 8 scale-u16 byte offset; 9 packed-ID byte offset;
10 quant mode (0 literal,1 anchor); 11 quant literal-byte offset;
12 packed-anchor byte offset; 13 original Q8 bytes; 14 stored packet bytes;
15 reserved zero. All section starts are 4-byte aligned; four tail bytes permit
bounded cross-word loads. Packed keys are least-significant-bit first.

Each scale dictionary entry retains the exact original fp16 bits. An anchor key
uses five bits for the omitted quant lane and one sign bit: 0 means +127, 1 means
-127 (byte129). Remaining31 bytes stay in original order. Literal quant mode uses
all32 bytes. The original Q8 block is never assembled in the shader.

Before upload, validate header, dimensions, sections, hashes and every scale ID.
The input is data only; use the fixed, reviewed shader shipped with the app.

`main`:
- binding0: compressed packet storage `array<u32>`
- binding1: input activation `array<f32>`
- binding2: output activation `array<f32>`
- dispatch exactly `rows` workgroups of256 invocations
- each lane accumulates columns `lane, lane+256, ...`; reduction strides128..1

`gather`:
- binding0: same compressed packet
- binding2: output embedding activation vector
- binding3: 16-byte uniform `[row, 0, 0, 0]`
- dispatch ceil(columns/256) workgroups

No reconstructed Q8 weight buffer, expanded matrix, compression-stream decoder,
or model-provided shader is permitted. Gathering an activation row is ordinary
inference output; tied output-head matvec reuses the compressed embedding packet.
