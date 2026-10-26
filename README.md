
# CPU Urgency Analyzer for Data-Center Workloads

## 1. Overview

CPU Urgency Analyzer is an Operating Systems project that investigates how CPU contention and workload intensity affect application latency and throughput.

The project combines Python-based CPU benchmarking, controlled CPU contention using `stress-ng`, Linux scheduler tracing using eBPF and `bpftrace`, and analysis of a 100,000-row datacenter telemetry dataset.

The original implementation explored GPU-aware scheduling and vLLM. Due to limited GPU availability in the development environment, the implementation was adapted into a CPU-based workload and scheduling analysis system.

**Important:** The benchmark simulates CPU-intensive inference-like computation using repeated SHA-256 hashing. It does not run a real large language model. The external datacenter dataset is synthetic/engineered telemetry, not verified production measurements.

## 2. Objectives

- Establish baseline CPU workload performance.
- Measure latency changes under controlled CPU contention.
- Compare low-, medium-, and high-work configurations.
- Analyze datacenter workload characteristics using a large dataset.
- Develop a transparent, heuristic CPU urgency score.
- Collect exploratory Linux scheduler wake-to-run telemetry using eBPF.
- Generate experiment summaries, CSV reports, and visualizations.

## 3. System Architecture

```text
       Datacenter Telemetry Dataset
              (100,000 rows)
                    |
                    v
       Data Cleaning and Analysis
                    |
                    v
        Representative Workloads
                    |
                    v
        Configurable CPU Benchmark
                    |
          +---------+---------+
          |                   |
          v                   v
     Baseline Run        CPU Contention
                          (stress-ng)
          |                   |
          +---------+---------+
                    |
                    v
       Latency and Throughput Analysis
                    |
          +---------+---------+
          |                   |
          v                   v
   Urgency Score       eBPF Scheduler
   and Comparison       Telemetry
          |                   |
          +---------+---------+
                    |
                    v
         CSV Reports and Plots
```

The urgency score is an analysis heuristic. This implementation does not modify the Linux scheduler or enforce priority-based scheduling.

## 4. Technologies Used

- Python
- pandas and NumPy
- Matplotlib
- Linux / WSL Ubuntu
- `stress-ng`
- `bpftrace` and eBPF
- Git and GitHub

## 5. Dataset

The project analyzes a datacenter telemetry dataset containing 100,000 records and 35 columns.

Selected features include:

- CPU, GPU, and memory utilization
- Workload intensity
- Network latency and throughput
- Disk I/O
- Virtual machine counts
- Power consumption and energy efficiency
- Failure-risk and energy-efficiency classifications

The analysis scripts validate relevant fields, calculate workload pressure scores, compare alternative heuristic formulas, and select representative workload profiles.

**Dataset limitation:** The dataset contains synthetic/engineered telemetry. Its results describe the supplied data and must not be interpreted as measurements from a real production datacenter.

The raw dataset is kept outside version control. Refer to the dataset's accompanying metadata and source information when citing it.

## 6. Experiments

The current experiment report compares five conditions:

1. **Baseline:** CPU benchmark without deliberately introduced contention.
2. **CPU Contention:** Benchmark running alongside `stress-ng`.
3. **Low Workload:** Lower computational work per request.
4. **Medium Workload:** Intermediate computational work per request.
5. **High Workload:** Higher computational work per request.

Each reported condition contains 20 requests.

The low-, medium-, and high-workload experiments vary the benchmark's configurable work factor. These labels refer to computational workload settings, not guaranteed CPU utilization percentages.

### Current Results

| Condition | Requests | Mean latency |
|---|---:|---:|
| Baseline | 20 | 55.77 ms |
| CPU Contention | 20 | 68.39 ms |
| Low Workload | 20 | 27.65 ms |
| Medium Workload | 20 | 56.26 ms |
| High Workload | 20 | 117.10 ms |

In the recorded baseline and contention runs, mean latency increased by approximately 22.62% during CPU contention. Individual runs can vary with system load and environment.

These are results from the current runs, not averages over repeated independent trials.

## 7. CPU Urgency Score

The project implements a heuristic urgency score based on measured latency changes. The score is used to categorize observed workload pressure for analysis.

The score is not a learned model, a validated universal urgency metric, or a mechanism that changes Linux scheduling decisions.

## 8. Scheduler Telemetry

The project uses `bpftrace` to observe Linux scheduler tracepoints, including task wake-ups and context switches. The tracing script estimates wake-to-run delay by measuring the time between a recorded wake-up and the task's next scheduled execution.

Exploratory system-wide telemetry has been collected successfully.

**Current limitation:** Scheduler events have not yet been reliably associated with the benchmark's process and worker thread. Consequently, the recorded scheduler-delay summary is system-wide exploratory data and is not used as verified benchmark-specific wait-time evidence.

## 9. Repository Structure

```text
.
├── analysis/
│   ├── analyze_datacenter_dataset.py
│   ├── compare_urgency_scores.py
│   ├── experiment_summary.py
│   ├── final_experiment_report.py
│   ├── plot_final_results.py
│   └── select_workload_scenarios.py
├── benchmark/
│   ├── llm_benchmark.py
│   └── vllm_benchmark_original.py
├── contention/
│   └── run_contention.sh
├── data/
│   ├── baseline.csv
│   ├── contention.csv
│   └── raw/                  # Excluded from Git
├── results/
│   ├── final_experiment_report.csv
│   ├── final_plots/
│   ├── low_workload.csv
│   ├── medium_workload.csv
│   ├── high_workload.csv
│   └── system_scheduler_summary.csv
├── telemetry/
│   ├── benchmark_trace.bt
│   └── scheduler_trace_csv.bt
├── urgency/
│   └── urgency_score.py
├── requirements.txt
└── README.md
```

## 10. Setup

Run the following commands in a Linux or WSL Ubuntu terminal.

```bash
git clone https://github.com/Ananjindal/Automated-Compiler-Optimizer.git
cd scx_gpu_urgent
```

The repository URL and project directory above may need to be adjusted to match the published repository name.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install `stress-ng` if it is not already installed:

```bash
sudo apt update
sudo apt install stress-ng bpftrace
```

## 11. Running the Benchmark

Run a baseline workload:

```bash
python benchmark/llm_benchmark.py \
  --requests 20 \
  --tokens 32 \
  --workers 1 \
  --work-factor 5000 \
  --output results/baseline_demo.csv
```

Run a workload while introducing CPU contention:

```bash
stress-ng --cpu 2 --timeout 15s --quiet &
STRESS_PID=$!
sleep 2

python benchmark/llm_benchmark.py \
  --requests 20 \
  --tokens 32 \
  --workers 1 \
  --work-factor 5000 \
  --output results/contention_demo.csv

wait "$STRESS_PID"
```

Run the experiment analysis:

```bash
python analysis/final_experiment_report.py
python analysis/plot_final_results.py
```

Analyze the datacenter dataset, provided its raw CSV has been placed at `data/raw/green_ai_datacenter.csv`:

```bash
python analysis/analyze_datacenter_dataset.py
python analysis/compare_urgency_scores.py
python analysis/select_workload_scenarios.py
```

Some analysis scripts require the dataset files to be present locally. The eBPF tracing scripts require a compatible Linux environment and appropriate privileges.

## 12. Results and Visualizations

The experiment analysis generates a CSV report containing request counts, mean and median latency, P95 latency, throughput, work duration, and changes relative to baseline.

Generated plots include:

- Mean latency comparison
- P95 latency comparison
- Throughput comparison

Dataset analysis generates workload summaries, pressure distributions, correlation data, and representative scenario profiles.

## 13. Limitations and Future Work

- Repeat experiments to measure variability and improve confidence in comparisons.
- Improve scheduler trace filtering to reliably associate events with benchmark threads.
- Compare workload urgency against verified benchmark-specific scheduler measurements.
- Investigate alternative urgency-score weights using independent evaluation data.
- Explore scheduling-policy integration only in a suitable test environment.
- Add clearer dataset provenance and reproducible dataset acquisition instructions.

## 14. Conclusion

CPU Urgency Analyzer combines controlled CPU benchmarking, contention experiments, datacenter dataset analysis, heuristic urgency scoring, and exploratory eBPF telemetry in an Operating Systems project.

It provides a practical foundation for investigating how workload intensity and CPU contention relate to latency and throughput while identifying the additional validation needed for reliable benchmark-specific scheduler analysis.
