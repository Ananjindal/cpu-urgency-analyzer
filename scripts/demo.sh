#!/bin/bash
set -e

echo "=========================================="
echo "       CPU URGENCY ANALYZER DEMO"
echo "=========================================="

echo
echo "1. Running CPU workload benchmark..."
python benchmark/llm_benchmark.py \
    --requests 20 \
    --tokens 32 \
    --workers 1 \
    --work-factor 5000 \
    --output results/demo_workload.csv

echo
echo "2. Comparing repeated baseline and contention experiments..."
python analysis/repeated_run_comparison.py

echo
echo "3. Checking generated experiment results..."
python - <<'PY'
import pandas as pd

path = "results/demo_workload.csv"
df = pd.read_csv(path)

print("Requests completed:", len(df))
print(f"Mean latency: {df['latency_s'].mean() * 1000:.2f} ms")
print(f"P95 latency: {df['latency_s'].quantile(0.95) * 1000:.2f} ms")
print(f"Total tokens: {df['tokens'].sum()}")

print("\nExisting result files:")
for file in [
    "results/repeated_run_comparison.csv",
    "results/final_experiment_report.csv",
    "results/final_plots/mean_latency.png",
    "results/final_plots/p95_latency.png",
    "results/final_plots/throughput.png",
]:
    from pathlib import Path
    print(("OK  " if Path(file).exists() else "MISSING  ") + file)
PY

echo
echo "DEMO COMPLETED"
