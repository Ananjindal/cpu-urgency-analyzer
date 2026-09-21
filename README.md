# CPU Urgency Analyzer

## Overview

This project studies how CPU contention affects the response time of a workload and uses Linux scheduler telemetry to estimate when a workload is experiencing increased CPU scheduling pressure.

The original project was planned around GPU-aware scheduling and vLLM. However, the available laptop environment did not provide usable NVIDIA GPU access. Therefore, the implementation was adapted into a **CPU-based scheduling analysis project** using Python, Linux `stress-ng`, and eBPF scheduler tracing.

The project measures:

- Workload latency under normal conditions
- Workload latency during CPU contention
- CPU scheduler wait time
- Change in scheduler wait time when CPU resources are constrained
- A project-defined CPU urgency score

---

## Project Objectives

The main objectives are:

1. Establish a baseline workload performance.
2. Introduce CPU contention using `stress-ng`.
3. Measure the effect of contention on workload latency.
4. Collect scheduler-level CPU wait-time information using eBPF.
5. Compare baseline and contention conditions.
6. Calculate a CPU urgency score from latency and scheduler wait-time changes.

---

## System Architecture

```text
                ┌─────────────────────┐
                │   Python Workload   │
                │   LLM Benchmark     │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Linux Scheduler   │
                └──────────┬──────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
    ┌────────────────┐          ┌────────────────┐
    │ Normal CPU     │          │ CPU Contention │
    │ Conditions     │          │ stress-ng      │
    └────────────────┘          └────────────────┘
             │                           │
             └─────────────┬─────────────┘
                           ▼
                ┌─────────────────────┐
                │ eBPF Scheduler      │
                │ Telemetry           │
                └──────────┬──────────┘
                           ▼
                ┌─────────────────────┐
                │ CPU Urgency Score   │
                └─────────────────────┘
