
import pandas as pd
from pathlib import Path

BASELINE_FILE = "data/baseline.csv"
CONTENTION_FILE = "data/contention.csv"

def load_metrics(path):
    df = pd.read_csv(path)

    if df.empty or "latency_s" not in df.columns:
        raise ValueError(f"Missing or empty benchmark data: {path}")

    return {
        "requests": len(df),
        "mean_latency": df["latency_s"].mean(),
        "median_latency": df["latency_s"].median(),
        "p95_latency": df["latency_s"].quantile(0.95),
    }

baseline = load_metrics(BASELINE_FILE)
contention = load_metrics(CONTENTION_FILE)

if baseline["mean_latency"] <= 0:
    raise ValueError("Baseline latency must be positive.")

latency_increase = (
    (contention["mean_latency"] - baseline["mean_latency"])
    / baseline["mean_latency"]
) * 100

# Experimental latency-based score, capped to a 0–100 range.
# This is a heuristic, not a validated scheduler priority.
urgency_score = max(0.0, min(100.0, latency_increase))

if urgency_score < 10:
    level = "LOW"
elif urgency_score < 25:
    level = "MEDIUM"
else:
    level = "HIGH"

print("========== CPU URGENCY ANALYSIS ==========")
print(f"Baseline requests  : {baseline['requests']}")
print(f"Contention requests: {contention['requests']}")
print(f"Baseline mean      : {baseline['mean_latency']:.4f} s")
print(f"Contention mean    : {contention['mean_latency']:.4f} s")
print(f"Baseline P95       : {baseline['p95_latency']:.4f} s")
print(f"Contention P95     : {contention['p95_latency']:.4f} s")
print(f"Latency increase   : {latency_increase:.2f}%")
print(f"Urgency score      : {urgency_score:.2f}/100")
print(f"Urgency level      : {level}")
print("------------------------------------------")
print("Note: Heuristic based on measured latency change.")
print("Scheduler wait time is not included.")
print("==========================================")

Path("results").mkdir(exist_ok=True)
pd.DataFrame([{
    "baseline_mean_latency_s": baseline["mean_latency"],
    "contention_mean_latency_s": contention["mean_latency"],
    "latency_increase_percent": latency_increase,
    "latency_urgency_score": urgency_score,
    "urgency_level": level,
}]).to_csv("results/urgency_score.csv", index=False)

print("Saved to results/urgency_score.csv")
