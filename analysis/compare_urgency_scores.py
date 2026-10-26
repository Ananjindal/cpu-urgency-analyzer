
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "green_ai_datacenter.csv"
OUT = ROOT / "results" / "datacenter_analysis"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)

cpu = df["cpu_utilization"]
memory = df["memory_utilization"]
gpu = df["gpu_utilization"]
workload = df["workload_intensity"] * 100

df["score_current"] = (
    0.50 * cpu + 0.20 * memory
    + 0.10 * gpu + 0.20 * workload
)

df["score_reduced_redundancy"] = (
    0.65 * cpu + 0.20 * memory
    + 0.10 * gpu + 0.05 * workload
)

def classify(score):
    return pd.cut(
        score,
        bins=[-0.01, 40, 70, 100],
        labels=["LOW", "MEDIUM", "HIGH"],
    )

for name in ["score_current", "score_reduced_redundancy"]:
    df[name + "_level"] = classify(df[name])

summary = df[
    ["score_current", "score_reduced_redundancy"]
].describe().T
summary.to_csv(OUT / "score_comparison_summary.csv")

counts = pd.DataFrame({
    "current": df["score_current_level"].value_counts(),
    "reduced_redundancy":
        df["score_reduced_redundancy_level"].value_counts(),
}).reindex(["LOW", "MEDIUM", "HIGH"])
counts.to_csv(OUT / "score_comparison_levels.csv")

correlations = pd.DataFrame({
    "score_current": df["score_current"],
    "score_reduced_redundancy": df["score_reduced_redundancy"],
    "cpu_utilization": cpu,
    "workload_intensity": workload,
    "memory_utilization": memory,
    "gpu_utilization": gpu,
}).corr()
correlations.to_csv(OUT / "score_comparison_correlations.csv")

df.to_csv(OUT / "score_comparison_records.csv", index=False)

counts.plot(kind="bar", figsize=(8, 5))
plt.ylabel("Number of records")
plt.title("Urgency Category Comparison")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUT / "score_comparison.png", dpi=160)
plt.close()

print("=== SCORE SUMMARY ===")
print(summary.round(2).to_string())

print("\n=== CATEGORY COUNTS ===")
print(counts.to_string())

print("\n=== FEATURE CORRELATIONS ===")
print(correlations.round(3).to_string())

print(f"\nResults saved in {OUT.relative_to(ROOT)}")
