import pandas as pd
from pathlib import Path

CONDITIONS = {
    "Baseline": "data/baseline.csv",
    "CPU Contention": "data/contention.csv",
}

rows = []

for condition, path in CONDITIONS.items():
    df = pd.read_csv(path)

    elapsed = df["end_time"].max() - df["start_time"].min()
    total_tokens = int(df["tokens"].sum())

    rows.append({
        "Condition": condition,
        "Requests": len(df),
        "Mean Latency (s)": df["latency_s"].mean(),
        "Median Latency (s)": df["latency_s"].median(),
        "P95 Latency (s)": df["latency_s"].quantile(0.95),
        "Throughput (tokens/s)": total_tokens / elapsed,
        "Total Recorded Work Duration (s)": df["cpu_work_s"].sum(),
    })

result = pd.DataFrame(rows)

baseline_latency = result.loc[
    result["Condition"] == "Baseline", "Mean Latency (s)"
].iloc[0]

baseline_throughput = result.loc[
    result["Condition"] == "Baseline", "Throughput (tokens/s)"
].iloc[0]

result["Mean Latency Change (%)"] = (
    result["Mean Latency (s)"] / baseline_latency - 1
) * 100

result["Throughput Change (%)"] = (
    result["Throughput (tokens/s)"] / baseline_throughput - 1
) * 100

Path("data").mkdir(exist_ok=True)
result.to_csv("data/experiment_summary.csv", index=False)

print(result.round(4).to_string(index=False))
print("\nSaved to data/experiment_summary.csv")
