
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "green_ai_datacenter.csv"
OUT = ROOT / "results" / "datacenter_analysis"

OUT.mkdir(parents=True, exist_ok=True)

# Load the full dataset.
df = pd.read_csv(DATA)

required = [
    "workload_intensity",
    "cpu_utilization",
    "memory_utilization",
    "gpu_utilization",
    "network_latency_ms",
    "disk_io_iops",
    "failure_risk_level",
]

missing_columns = [c for c in required if c not in df.columns]
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# Check the core numeric inputs.
numeric = [
    "workload_intensity",
    "cpu_utilization",
    "memory_utilization",
    "gpu_utilization",
    "network_latency_ms",
    "disk_io_iops",
]

df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce")

if df[numeric].isna().any().any():
    raise ValueError("Core numeric features contain missing or invalid values.")

if not df["cpu_utilization"].between(0, 100).all():
    raise ValueError("CPU utilization is outside the expected 0–100 range.")

for col in ["memory_utilization", "gpu_utilization"]:
    if not df[col].between(0, 100).all():
        raise ValueError(f"{col} is outside the expected 0–100 range.")

if not df["workload_intensity"].between(0, 1).all():
    raise ValueError("Workload intensity is outside the expected 0–1 range.")

# Preserve rows with missing region; region is not required for scoring.
df["datacenter_region"] = (
    df["datacenter_region"].fillna("Unknown")
)

# A transparent initial pressure score, scaled from 0 to 100.
# Workload intensity and CPU utilization are strongly correlated,
# so workload intensity receives a smaller weight.
df["workload_pressure_score"] = (
    0.50 * df["cpu_utilization"]
    + 0.20 * (df["memory_utilization"])
    + 0.10 * df["gpu_utilization"]
    + 0.20 * (100 * df["workload_intensity"])
).clip(0, 100)

df["pressure_level"] = pd.cut(
    df["workload_pressure_score"],
    bins=[-0.01, 40, 70, 100],
    labels=["LOW", "MEDIUM", "HIGH"],
)

# Save scored rows and quality/statistical summaries.
df.to_csv(OUT / "scored_workloads.csv", index=False)

df[numeric].describe().T.to_csv(OUT / "numeric_summary.csv")
df[numeric].corr().to_csv(OUT / "correlation_matrix.csv")

df["pressure_level"].value_counts().reindex(
    ["LOW", "MEDIUM", "HIGH"], fill_value=0
).rename_axis("pressure_level").to_csv(
    OUT / "pressure_distribution.csv"
)

summary = [
    "CPU Urgency Analyzer - Dataset Analysis",
    f"Rows processed: {len(df)}",
    f"Columns: {len(df.columns)}",
    f"Duplicate rows: {df.duplicated().sum()}",
    f"Missing regions retained as Unknown: "
    f"{(df['datacenter_region'] == 'Unknown').sum()}",
    "",
    "Initial workload-pressure score:",
    "50% CPU + 20% memory + 10% GPU + 20% workload intensity",
    "This is a heuristic, not a measured scheduler-wait prediction.",
    "",
    "Pressure distribution:",
    df["pressure_level"].value_counts().to_string(),
]

(OUT / "summary.txt").write_text(
    "\n".join(summary) + "\n", encoding="utf-8"
)

# Plot CPU utilization versus workload intensity.
plt.figure(figsize=(8, 5))
sample = df.sample(min(3000, len(df)), random_state=42)
plt.scatter(
    sample["workload_intensity"],
    sample["cpu_utilization"],
    alpha=0.35,
    s=8,
)
plt.xlabel("Workload intensity")
plt.ylabel("CPU utilization (%)")
plt.title("Workload Intensity vs CPU Utilization")
plt.tight_layout()
plt.savefig(OUT / "workload_cpu_relationship.png", dpi=160)
plt.close()

# Plot the score distribution.
plt.figure(figsize=(8, 5))
plt.hist(df["workload_pressure_score"], bins=40)
plt.xlabel("Workload pressure score")
plt.ylabel("Number of records")
plt.title("Workload Pressure Score Distribution")
plt.tight_layout()
plt.savefig(OUT / "pressure_distribution.png", dpi=160)
plt.close()

print("Dataset analysis completed successfully.")
print(f"Rows analyzed: {len(df)}")
print(f"Outputs saved to: {OUT.relative_to(ROOT)}")
print("\nPressure levels:")
print(df["pressure_level"].value_counts().to_string())
