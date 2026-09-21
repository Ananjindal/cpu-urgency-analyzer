import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/experiment_summary.csv")

plt.figure(figsize=(8, 5))

plt.bar(
    df["Condition"],
    df["Average CPU Wait (us)"]
)

plt.xlabel("Experiment Condition")
plt.ylabel("Average CPU Scheduling Wait (µs)")
plt.title("CPU Scheduling Wait Across Experiments")

plt.tight_layout()

plt.savefig("data/cpu_wait_comparison.png", dpi=300)

print("Graph saved to: data/cpu_wait_comparison.png")
