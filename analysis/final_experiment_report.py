from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "Baseline": ROOT / "data" / "baseline.csv",
    "CPU Contention": ROOT / "data" / "contention.csv",
    "Low Workload": ROOT / "results" / "low_workload.csv",
    "Medium Workload": ROOT / "results" / "medium_workload.csv",
    "High Workload": ROOT / "results" / "high_workload.csv",
}

rows = []

for condition, path in FILES.items():
    if not path.exists():
        raise FileNotFoundError(f"Missing experiment file: {path}")

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(f"Experiment file is empty: {path}")

    elapsed = df["end_time"].max() - df["start_time"].min()
    if elapsed <= 0:
        raise ValueError(f"Invalid elapsed time in {path}")

    total_tokens = int(df["tokens"].sum())

    rows.append({
        "Condition": condition,
        "Requests": len(df),
        "Tokens": total_tokens,
        "Mean Latency (ms)": df["latency_s"].mean() * 1000,
        "Median Latency (ms)": df["latency_s"].median() * 1000,
        "P95 Latency (ms)": df["latency_s"].quantile(0.95) * 1000,
        "Throughput (tokens/s)": total_tokens / elapsed,
        "Total Work Duration (s)": df["cpu_work_s"].sum(),
    })

report = pd.DataFrame(rows)

baseline_latency = report.loc[
    report["Condition"] == "Baseline", "Mean Latency (ms)"
].iloc[0]

baseline_throughput = report.loc[
    report["Condition"] == "Baseline", "Throughput (tokens/s)"
].iloc[0]

report["Latency Change vs Baseline (%)"] = (
    report["Mean Latency (ms)"] / baseline_latency - 1
) * 100

report["Throughput Change vs Baseline (%)"] = (
    report["Throughput (tokens/s)"] / baseline_throughput - 1
) * 100

out = ROOT / "results" / "final_experiment_report.csv"
report.to_csv(out, index=False)

print("\nFINAL EXPERIMENT COMPARISON")
print("=" * 105)
print(report.round(2).to_string(index=False))
print(f"\nSaved to: {out}")
