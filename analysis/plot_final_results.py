from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "final_experiment_report.csv"
OUT = ROOT / "results" / "final_plots"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)

# Plot 1: Mean latency
plt.figure(figsize=(10, 6))
plt.bar(df["Condition"], df["Mean Latency (ms)"])
plt.ylabel("Mean latency (ms)")
plt.title("Mean Request Latency Across Experiment Conditions")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(OUT / "mean_latency.png", dpi=200)
plt.close()

# Plot 2: P95 latency
plt.figure(figsize=(10, 6))
plt.bar(df["Condition"], df["P95 Latency (ms)"])
plt.ylabel("P95 latency (ms)")
plt.title("P95 Request Latency Across Experiment Conditions")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(OUT / "p95_latency.png", dpi=200)
plt.close()

# Plot 3: Throughput
plt.figure(figsize=(10, 6))
plt.bar(df["Condition"], df["Throughput (tokens/s)"])
plt.ylabel("Throughput (tokens/s)")
plt.title("Benchmark Throughput Across Experiment Conditions")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(OUT / "throughput.png", dpi=200)
plt.close()

print("Charts generated:")
for path in sorted(OUT.glob("*.png")):
    print(path)
