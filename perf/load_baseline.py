import argparse
import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0

    sorted_values = sorted(values)
    index = int(round((pct / 100) * (len(sorted_values) - 1)))

    return sorted_values[index]


def run_request(client: httpx.Client, url: str) -> float:
    start = time.perf_counter()
    response = client.get(url)
    response.raise_for_status()

    return time.perf_counter() - start


def collect_latencies(
    base_url: str,
    path: str,
    requests: int,
    concurrency: int,
) -> list[float]:
    url = f"{base_url.rstrip('/')}{path}"
    latencies: list[float] = []

    with httpx.Client(timeout=10.0) as client:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [
                executor.submit(run_request, client, url)
                for _ in range(requests)
            ]

            for future in as_completed(futures):
                latencies.append(future.result())

    return latencies


def summarize(latencies: list[float], *, elapsed_seconds: float, target: str) -> dict:
    return {
        "target": target,
        "count": len(latencies),
        "total_seconds": round(elapsed_seconds, 2),
        "throughput_rps": round(len(latencies) / elapsed_seconds, 2)
        if elapsed_seconds
        else 0.0,
        "min_ms": round(min(latencies) * 1000, 2),
        "max_ms": round(max(latencies) * 1000, 2),
        "mean_ms": round(statistics.mean(latencies) * 1000, 2),
        "p50_ms": round(percentile(latencies, 50) * 1000, 2),
        "p95_ms": round(percentile(latencies, 95) * 1000, 2),
        "p99_ms": round(percentile(latencies, 99) * 1000, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lightweight local load baseline for HTTP endpoints.",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("API_BASE_URL", "http://api:8000"),
    )
    parser.add_argument("--path", default="/health")
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()

    started = time.perf_counter()
    latencies = collect_latencies(
        args.base_url,
        args.path,
        args.requests,
        args.concurrency,
    )
    elapsed_seconds = time.perf_counter() - started
    target = f"{args.base_url.rstrip('/')}{args.path}"

    print(
        json.dumps(
            summarize(latencies, elapsed_seconds=elapsed_seconds, target=target),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
