from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "results" / "repeated_runs"
OUTPUT = ROOT / "results" / "repeated_run_comparison.csv"

records = []

for condition in ["baseline", "contention"]:
    for run in range(1, 4):
        path = RUNS / f"{condition}_{run}.csv"

        if not path.exists():
            raise FileNotFoundError(f"Missing experiment file: {path}")

        df = pd.read_csv(path)

        records.append({
            "Condition": condition.title(),
            "Run": run,
            "Requests": len(df),
            "Mean Latency (ms)": df["latency_s"].mean() * 1000,
            "Median Latency (ms)": df["latency_s"].median() * 1000,
            "P95 Latency (ms)": df["latency_s"].quantile(0.95) * 1000,
            "Throughput (tokens/s)": (
                df["tokens"].sum()
                / (df["end_time"].max() - df["start_time"].min())
            ),
        })

report = pd.DataFrame(records)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
report.to_csv(OUTPUT, index=False, float_format="%.4f")

print("\nREPEATED EXPERIMENT COMPARISON")
print("=" * 75)
print(report.round(2).to_string(index=False))

summary = report.groupby("Condition").mean(numeric_only=True)
baseline = summary.loc["Baseline"]
contention = summary.loc["Contention"]

print("\nAVERAGE ACROSS THREE RUNS")
print("-" * 40)

for metric in [
    "Mean Latency (ms)",
    "Median Latency (ms)",
    "P95 Latency (ms)",
    "Throughput (tokens/s)",
]:
    change = (
        (contention[metric] - baseline[metric])
        / baseline[metric] * 100
    )
    print(
        f"{metric}: baseline={baseline[metric]:.2f}, "
        f"contention={contention[metric]:.2f}, "
        f"change={change:+.2f}%"
    )

print(f"\nSaved report: {OUTPUT.relative_to(ROOT)}")
