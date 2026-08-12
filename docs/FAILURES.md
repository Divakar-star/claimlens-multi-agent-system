# Failures

Real problems hit while building this, what caused them, and whether they are
fixed. Entries are added as they happen, not reconstructed afterwards.

---

## 1. The Docker image was 9.34 GB

**Status:** fixed

**What happened.** The first successful `make docker-build` produced a 9.34 GB
image for a project whose own code is under 100 KB. Build time was roughly 25
minutes, with 807s in the single `pip install -r requirements.txt` layer.

**Why.** `sentence-transformers` depends on `torch`, and the default PyPI torch
wheel for Linux bundles the full CUDA runtime -- cuDNN, cuBLAS, NCCL and
friends -- as `nvidia-*` transitive dependencies. That is multiple gigabytes of
GPU libraries in a project that embeds 12 short documents on CPU and has "no
GPU dependencies" as an explicit non-goal. Two smaller contributors: the
`build-essential` toolchain stayed in the final image, and wheel-internal test
suites and C headers were never removed.

**What changed.** Dockerfile is now two-stage. The builder installs
`torch==2.13.0` from `download.pytorch.org/whl/cpu` *before* the rest of
requirements, so the CUDA-flavoured wheel is never selected; the runtime stage
copies only the finished virtualenv, leaving the compiler behind. Wheel test
directories, `.pyc`, `.h` and `.a` files are stripped from the venv.

**Measured result.** 9.34 GB -> 1.83 GB, an 80% reduction, on the same
machine with the same pinned versions. Rebuild time also dropped sharply, since
the CUDA wheels were most of the 807s spent in the install layer.

**What remains.** 1.83 GB is still dominated by torch plus onnxruntime (a
chromadb dependency). Getting below ~1 GB would mean dropping
sentence-transformers for a smaller embedding path, which changes retrieval
quality and is not worth it at this corpus size.

**What this cost.** Nothing but time, but it is a good illustration of a
transitive dependency quietly deciding your deployment story. Nothing in
`requirements.txt` mentions CUDA.
