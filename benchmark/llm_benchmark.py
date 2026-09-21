import argparse
import csv
import hashlib
import os
import time
from concurrent.futures import ThreadPoolExecutor


def cpu_token_work(prompt, tokens):
    """
    Controlled CPU-intensive workload representing
    computation performed during an inference request.
    """

    data = prompt.encode()

    start = time.perf_counter()

    for _ in range(tokens):

        # Simulate computation for generating a token
        for _ in range(5000):
            data = hashlib.sha256(data).digest()

    end = time.perf_counter()

    return end - start


def process_request(request_id, prompt, tokens):

    start_time = time.perf_counter()

    cpu_work = cpu_token_work(
        prompt,
        tokens
    )

    end_time = time.perf_counter()

    return {
        "request_id": request_id,
        "pid": os.getpid(),
        "start_time": start_time,
        "end_time": end_time,
        "latency_s": end_time - start_time,
        "cpu_work_s": cpu_work,
        "tokens": tokens
    }


def main():

    parser = argparse.ArgumentParser(
        description="CPU-based LLM workload benchmark"
    )

    parser.add_argument(
        "--requests",
        type=int,
        default=8
    )

    parser.add_argument(
        "--tokens",
        type=int,
        default=32
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=4
    )

    parser.add_argument(
        "--output",
        default="data/baseline.csv"
    )

    args = parser.parse_args()

    prompts = [
        "Explain operating systems.",
        "Explain CPU scheduling.",
        "Explain memory management.",
        "Explain process synchronization.",
        "Explain deadlocks.",
        "Explain virtual memory.",
        "Explain Linux scheduling.",
        "Explain distributed systems."
    ]

    prompts = prompts[:args.requests]

    print()
    print("=" * 45)
    print("       CPU LLM WORKLOAD BENCHMARK")
    print("=" * 45)

    print(f"Requests : {len(prompts)}")
    print(f"Tokens   : {args.tokens}")
    print(f"Workers  : {args.workers}")
    print()

    overall_start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=args.workers
    ) as executor:

        futures = []

        for request_id, prompt in enumerate(prompts):

            future = executor.submit(
                process_request,
                request_id,
                prompt,
                args.tokens
            )

            futures.append(future)

        results = [
            future.result()
            for future in futures
        ]

    overall_end = time.perf_counter()

    total_time = (
        overall_end -
        overall_start
    )

    total_tokens = sum(
        result["tokens"]
        for result in results
    )

    throughput = (
        total_tokens / total_time
    )

    os.makedirs(
        os.path.dirname(args.output)
        or ".",
        exist_ok=True
    )

    with open(
        args.output,
        "w",
        newline=""
    ) as file:

        fieldnames = [
            "request_id",
            "pid",
            "start_time",
            "end_time",
            "latency_s",
            "cpu_work_s",
            "tokens"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(results)

    print("RESULTS")
    print("-" * 45)

    for result in results:

        print(
            f"Request {result['request_id']} "
            f"→ {result['latency_s']:.4f} s"
        )

    print()
    print(
        f"Total time : {total_time:.4f} s"
    )

    print(
        f"Throughput : {throughput:.2f} tokens/s"
    )

    print()
    print(
        f"Results saved to: {args.output}"
    )


if __name__ == "__main__":
    main()
