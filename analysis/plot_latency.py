import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/experiment_summary.csv")

df = df.dropna(subset=["Average Latency (s)"])

plt.figure(figsize=(8, 5))

plt.bar(
    df["Condition"],
    df["Average Latency (s)"]
)

plt.xlabel("Experiment Condition")
plt.ylabel("Average Latency (seconds)")
plt.title("LLM Request Latency Under CPU Conditions")

plt.tight_layout()

plt.savefig("data/latency_comparison.png", dpi=300)

print("Graph saved to: data/latency_comparison.png")
