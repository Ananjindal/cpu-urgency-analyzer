# scx_gpu_urgent

**GPU-Urgency-Aware Host CPU Scheduling for Multi-Tenant LLM Inference via Linux sched_ext**

## Status: Review 2 — Prototype Pipeline

This review does **not** implement the final research system. It establishes a working
experimental pipeline that will later be extended into a full GPU-urgency-aware
`sched_ext` scheduler.

```
vLLM inference  →  CPU contention (stress-ng)  →  CPU telemetry (eBPF/tracing)
      →  GPU monitoring (nvidia-smi/NVML)  →  CPU/GPU correlation
      →  basic rule-based GPU Urgency Score  →  preliminary results
```

## Review 2 modules

| # | Module | Path | Status |
|---|--------|------|--------|
| 1 | LLM inference (vLLM) | `benchmark/vllm_benchmark.py` | ✅ implemented |
| 2 | CPU contention (stress-ng) | `contention/run_contention.sh` | pending |
| 3 | CPU telemetry (eBPF/tracing) | `telemetry/cpu_monitor.py` | pending |
| 4 | GPU monitoring (NVML) | `telemetry/gpu_monitor.py` | pending |
| 5 | CPU/GPU correlation | `analysis/correlate.py` | pending |
| 6 | Basic urgency score (rule-based) | `urgency/urgency_score.py` | pending |
| 7 | Basic sched_ext prototype (if kernel supports it) | `scheduler/` | pending |

Modules are added incrementally, one at a time, and each is runnable and verifiable on its own
before the next is built.

## Experiments (Review 2 minimum)

1. vLLM, no background CPU contention (baseline)
2. vLLM + low CPU contention
3. vLLM + medium/high CPU contention

Each experiment records, per request: TTFT, TPOT, total latency, throughput (if practical),
CPU scheduling/wait info, GPU utilization, GPU idle/activity — saved as CSV under `data/` and
`results/`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Requires a Linux machine with an NVIDIA GPU and a CUDA-compatible PyTorch/vLLM install.

## Module 1 — vLLM benchmark (implemented)

Runs offline batched inference over a set of prompts with a small/medium HF model,
using vLLM's per-request `RequestMetrics` (`arrival_time`, `first_token_time`,
`finished_time`) to compute TTFT and TPOT without needing a separate server process.

```bash
python3 benchmark/vllm_benchmark.py \
    --model Qwen/Qwen2.5-1.5B-Instruct \
    --num-prompts 20 \
    --max-tokens 128 \
    --tag baseline \
    --out data/baseline.csv
```

Pick a model size that fits the available GPU memory — swap `--model` for anything
HF/vLLM-compatible (e.g. a 1B–3B instruct model for smaller GPUs).

See the table above for what's next — we add one module at a time.
