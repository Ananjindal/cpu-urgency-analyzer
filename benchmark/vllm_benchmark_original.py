#!/usr/bin/env python3
"""
Module 1 — LLM inference benchmark (vLLM)
==========================================
scx_gpu_urgent — Review 2 prototype.

Runs a batch of prompts through vLLM offline inference and records, per
request: TTFT (time to first token), TPOT (time per output token), total
latency, and aggregate throughput. Results are written to a CSV so they can
be compared across experiments (no contention / low contention / high
contention) in later modules.

This intentionally uses vLLM's offline `LLM.generate()` API rather than
standing up a server — simplest thing that gives us real, per-request
timing via `RequestOutput.metrics`.

Usage:
    python3 vllm_benchmark.py --model Qwen/Qwen2.5-1.5B-Instruct \
        --num-prompts 20 --max-tokens 128 --tag baseline --out data/baseline.csv
"""

import argparse
import csv
import os
import sys
import time

DEFAULT_PROMPTS = [
    "Explain the difference between a process and a thread in one paragraph.",
    "Write a short summary of how virtual memory works.",
    "What is the CAP theorem? Explain briefly.",
    "Describe how a CPU scheduler decides which task to run next.",
    "Summarize the producer-consumer problem and one way to solve it.",
    "What causes GPU idle time during LLM inference serving?",
    "Explain what a context switch is and why it has overhead.",
    "Give a short overview of the Linux completely fair scheduler.",
    "What is tail latency and why does it matter for online services?",
    "Explain the difference between throughput and latency with an example.",
]


def build_prompts(num_prompts: int) -> list[str]:
    prompts = []
    i = 0
    while len(prompts) < num_prompts:
        prompts.append(DEFAULT_PROMPTS[i % len(DEFAULT_PROMPTS)])
        i += 1
    return prompts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True, help="HF model id or local path")
    ap.add_argument("--num-prompts", type=int, default=20)
    ap.add_argument("--max-tokens", type=int, default=128)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--tag", required=True,
                     help="experiment label, e.g. baseline / low_contention / high_contention")
    ap.add_argument("--out", required=True, help="output CSV path")
    ap.add_argument("--gpu-memory-utilization", type=float, default=0.85)
    args = ap.parse_args()

    try:
        from vllm import LLM, SamplingParams
    except ImportError:
        print("ERROR: vllm is not installed. `pip install -r requirements.txt` first.",
              file=sys.stderr)
        sys.exit(1)

    prompts = build_prompts(args.num_prompts)

    print(f"[vllm_benchmark] loading model: {args.model}")
    llm = LLM(model=args.model, gpu_memory_utilization=args.gpu_memory_utilization,
              seed=args.seed)

    sampling_params = SamplingParams(
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    print(f"[vllm_benchmark] running {len(prompts)} prompts (tag={args.tag})")
    wall_start = time.time()
    outputs = llm.generate(prompts, sampling_params)
    wall_end = time.time()
    wall_elapsed = wall_end - wall_start

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    rows = []
    total_output_tokens = 0
    for idx, output in enumerate(outputs):
        metrics = output.metrics
        num_out_tokens = len(output.outputs[0].token_ids)
        total_output_tokens += num_out_tokens

        arrival = metrics.arrival_time
        first_token = getattr(metrics, "first_token_time", None)
        finished = getattr(metrics, "finished_time", None) or wall_end

        ttft = (first_token - arrival) if first_token else None
        total_latency = finished - arrival
        if ttft is not None and num_out_tokens > 1:
            tpot = (total_latency - ttft) / (num_out_tokens - 1)
        else:
            tpot = None

        rows.append({
            "tag": args.tag,
            "request_idx": idx,
            "prompt_len_chars": len(prompts[idx]),
            "output_tokens": num_out_tokens,
            "ttft_s": round(ttft, 4) if ttft is not None else "",
            "tpot_s": round(tpot, 4) if tpot is not None else "",
            "total_latency_s": round(total_latency, 4),
        })

    throughput_tok_s = total_output_tokens / wall_elapsed if wall_elapsed > 0 else 0

    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) + ["run_throughput_tok_s"])
        writer.writeheader()
        for r in rows:
            r["run_throughput_tok_s"] = round(throughput_tok_s, 2)
            writer.writerow(r)

    print(f"[vllm_benchmark] done. wall_time={wall_elapsed:.2f}s "
          f"throughput={throughput_tok_s:.1f} tok/s")
    print(f"[vllm_benchmark] wrote {len(rows)} rows -> {args.out}")


if __name__ == "__main__":
    main()
