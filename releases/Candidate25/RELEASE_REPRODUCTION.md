# Candidate25 reproduction and continuation

Start with this complete source package. Candidate24 Library version18 was the baseline. Its browser benchmark-save correction and CPU Q8/F32 optimization were preserved.

## Build prerequisites

An existing C++17 compiler is required. CPU executable:

```text
python native/Nexus.cpp/scripts/build.py --backend cpu
```

Linux CPU shared library for independent C ABI tests:

```text
g++ -O3 -std=c++17 -fPIC -shared -DNEXUS_SHARED=1 -DNEXUS_BUILDING_LIBRARY=1 -Inative/Nexus.cpp/include native/Nexus.cpp/src/c_api.cpp native/Nexus.cpp/src/gguf.cpp native/Nexus.cpp/src/cpu.cpp -o native/Nexus.cpp/build/libnexus_c.so
```

On Windows use the supplied native CMake project and its supported platform compiler settings. The regression runner uses `NEXUS_SHARED_LIBRARY` if set. HIP build, explicitly:

```text
python native/Nexus.cpp/scripts/build.py --backend hip
```

HIP source changes in this release require target-platform compilation and execution qualification. No new kernel throughput or hardware success is asserted by the CPU checks.

## Source and distribution verification

`RELEASE_SOURCE_SHA256.json` inventories the shipped files other than itself. These hashes detect changes relative to this package; they are not a digital signature or proof of publisher identity. `RELEASE_VALIDATION.json` identifies the current receipts. Earlier qualification folders are historical evidence only.

`python tools/release_check.py --verify-only --output identity-check` checks this inventory without executing the application. Runtime state and installed local binaries are intentionally outside the source inventory. Running some numerical tests regenerates their synthetic evidence JSON; restore the packaged evidence before checking original source identity again.

`python packaging.py . ../distribution` builds the split-data installer in a new directory outside the source tree. Add the Word guide, license files, readiness/reproduction documents and current validation receipt to the outer ZIP. The payload manifest hashes each file and each data part. Data parts are at most 10,000,000 bytes; every shipped component and the final ZIP must be below 20,000,000 bytes. Never include state, models, credentials, environments, dependency caches or compiled development binaries.

## Completed implementation

Protocol3 conversation caching and cooperative cancellation; session-scoped New Chat; min-p and repetition controls; actual native-capability UI; continuing rotating server diagnostics; bounded native metrics/export; durable registry writes/recovery; new-runtime installer detection; regression and real-model qualification commands.

## Continuation priority

1. Run the target-platform gates in ENTERPRISE_READINESS.md. Fix actual failures before adding further optimizations. Supply each exact GGUF name/hash, quantization, context, backend/device, compiler/driver version, diagnostic export and qualification receipt.
2. Implement true native matrix-batch prefill with scalar/full-logit reference parity at multiple prompt lengths and quantizations. A numeric batch setting alone is insufficient.
3. Implement and independently validate native Flash Attention and reduced-precision KV storage. Establish tolerances before performance measurement, then test actual gfx1100 memory pressure and long-context behavior.
4. Reduce host sampling/readback costs only after preserving the declared sampler order and seeded behavior. Evaluate throughput and first-token latency separately.
5. Scope the intended enterprise deployment. Shared serving requires identity/authorization, per-user state isolation, remote transport security and operational controls beyond this desktop design.

Do not mark the release enterprise-ready, Windows-qualified or Radeon-qualified until the corresponding evidence exists. Do not replace the independent engine with a third-party inference wrapper or change the license as part of a continuation.
