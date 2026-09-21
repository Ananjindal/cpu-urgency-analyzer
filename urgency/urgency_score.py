import pandas as pd

BASELINE_LATENCY = 0.2035
CONTENTION_LATENCY = 0.2369

BASELINE_WAIT = 11.31
CONTENTION_WAIT = 15.48

latency_increase = (
    (CONTENTION_LATENCY - BASELINE_LATENCY)
    / BASELINE_LATENCY
) * 100

wait_increase = (
    (CONTENTION_WAIT - BASELINE_WAIT)
    / BASELINE_WAIT
) * 100

urgency_score = (
    0.60 * latency_increase +
    0.40 * wait_increase
)

if urgency_score < 20:
    level = "LOW"
elif urgency_score < 50:
    level = "MEDIUM"
else:
    level = "HIGH"

print("========== CPU URGENCY SCORE ==========")
print(f"Latency increase : {latency_increase:.2f}%")
print(f"Wait increase    : {wait_increase:.2f}%")
print(f"Urgency Score    : {urgency_score:.2f}/100")
print(f"Urgency Level    : {level}")
print("=======================================")
