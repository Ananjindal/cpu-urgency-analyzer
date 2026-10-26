
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "green_ai_datacenter.csv"
OUT = ROOT / "results" / "datacenter_analysis"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)

features = [
    "cpu_utilization",
    "memory_utilization",
    "gpu_utilization",
    "workload_intensity",
    "network_latency_ms",
    "disk_io_iops",
]

if df[features].isna().any().any():
    raise ValueError("Scenario features contain missing values.")

# Define three groups using CPU utilization terciles.
low_cut, high_cut = df["cpu_utilization"].quantile([1/3, 2/3])

df["scenario"] = pd.cut(
    df["cpu_utilization"],
    bins=[-float("inf"), low_cut, high_cut, float("inf")],
    labels=["LOW_CPU", "MEDIUM_CPU", "HIGH_CPU"],
    include_lowest=True,
)

# Select the row closest to each group's feature medians.
# This produces representative profiles, not real-time telemetry.
selected = []

for scenario, group in df.groupby("scenario", observed=True):
    medians = group[features].median()
    scales = group[features].std().replace(0, 1).fillna(1)

    distances = (
        (group[features] - medians) / scales
    ).pow(2).sum(axis=1)

    row = group.loc[distances.idxmin()].copy()
    row["scenario"] = scenario
    row["records_in_group"] = len(group)
    selected.append(row)

profiles = pd.DataFrame(selected)
profiles.to_csv(OUT / "representative_scenarios.csv", index=False)

print("Representative dataset scenarios saved.")
print(f"Output: {OUT / 'representative_scenarios.csv'}")
print("\nCPU utilization thresholds:")
print(f"LOW_CPU:    <= {low_cut:.2f}%")
print(f"MEDIUM_CPU: {low_cut:.2f}% to {high_cut:.2f}%")
print(f"HIGH_CPU:   > {high_cut:.2f}%")

print("\nSelected profiles:")
print(
    profiles[
        ["scenario", "cpu_utilization", "memory_utilization",
         "gpu_utilization", "workload_intensity", "records_in_group"]
    ].to_string(index=False)
)
