import pandas as pd

data = {
    "Condition": [
        "Baseline",
        "CPU Contention",
        "Pinned CPU"
    ],
    "Average Latency (s)": [
        0.2035,
        0.2369,
        None
    ],
    "Average CPU Wait (us)": [
        11.31,
        11.34,
        15.48
    ]
}

df = pd.DataFrame(data)

baseline_latency = df.loc[0, "Average Latency (s)"]
baseline_wait = df.loc[0, "Average CPU Wait (us)"]

df["Latency Increase (%)"] = (
    (df["Average Latency (s)"] - baseline_latency)
    / baseline_latency * 100
)

df["Wait Increase (%)"] = (
    (df["Average CPU Wait (us)"] - baseline_wait)
    / baseline_wait * 100
)

df.to_csv("data/experiment_summary.csv", index=False)

print("\n========== EXPERIMENT SUMMARY ==========\n")
print(df.to_string(index=False))
print("\nSaved to: data/experiment_summary.csv")
