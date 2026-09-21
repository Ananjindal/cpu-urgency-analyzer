import pandas as pd

baseline = pd.read_csv("data/baseline.csv")
contention = pd.read_csv("data/contention.csv")

print("\n========== CPU URGENCY ANALYSIS ==========\n")

base_avg = baseline["latency_s"].mean()
cont_avg = contention["latency_s"].mean()

base_max = baseline["latency_s"].max()
cont_max = contention["latency_s"].max()

base_throughput = baseline["tokens"].sum() / baseline["latency_s"].sum()
cont_throughput = contention["tokens"].sum() / contention["latency_s"].sum()

increase = ((cont_avg - base_avg) / base_avg) * 100

print("BASELINE")
print(f"Average latency : {base_avg:.4f} s")
print(f"Maximum latency : {base_max:.4f} s")
print(f"Throughput     : {base_throughput:.2f} tokens/s")

print("\nCPU CONTENTION")
print(f"Average latency : {cont_avg:.4f} s")
print(f"Maximum latency : {cont_max:.4f} s")
print(f"Throughput     : {cont_throughput:.2f} tokens/s")

print("\nCOMPARISON")
print(f"Latency increase: {increase:.2f}%")

# Simple urgency score
urgency_score = min(100, max(0, increase))

print(f"Urgency Score   : {urgency_score:.2f}/100")

if urgency_score >= 50:
    level = "HIGH"
elif urgency_score >= 20:
    level = "MEDIUM"
else:
    level = "LOW"

print(f"Urgency Level   : {level}")

print("\n==========================================")
