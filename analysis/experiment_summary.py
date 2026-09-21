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

# Calculate latency increase only where latency data is available
df["Latency Increase (%)"] = (
    (df["Average Latency (s)"] - baseline_latency)
    / baseline_latency * 100
)

# Calculate scheduler wait increase for all conditions
df["Wait Increase (%)"] = (
    (df["Average CPU Wait (us)"] - baseline_wait)
    / baseline_wait * 100
)

# Pinned CPU latency was not measured
df.loc[df["Condition"] == "Pinned CPU", "Latency Increase (%)"] = None

# Save the summary
df.to_csv("data/experiment_summary.csv", index=False)

# Display a cleaner version
display_df = df.copy()
display_df["Latency Increase (%)"] = display_df["Latency Increase (%)"].apply(
    lambda x: "N/A" if pd.isna(x) else f"{x:.2f}"
)
display_df["Wait Increase (%)"] = display_df["Wait Increase (%)"].apply(
    lambda x: f"{x:.2f}"
)

print("\n========== EXPERIMENT SUMMARY ==========\n")
print(display_df.to_string(index=False))
print("\nSaved to: data/experiment_summary.csv")
