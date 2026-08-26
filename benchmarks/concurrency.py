import asyncio
import math
import statistics
import time

import httpx

URL = "http://127.0.0.1:8000/items/1"
TOTAL_REQUESTS = 200
CONCURRENCY_LEVELS = [1, 10, 25, 50]
TRIALS = 5


def percentile(values, percent):
    values = sorted(values)
    index = math.ceil((percent / 100) * len(values)) - 1
    return values[index]


async def make_request(client, semaphore):
    async with semaphore:
        start = time.perf_counter()

        try:
            response = await client.get(URL)
            success = response.status_code == 200
        except httpx.RequestError:
            success = False

        latency_ms = (time.perf_counter() - start) * 1000
        return latency_ms, success


async def run_trial(concurrency):
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=5.0) as client:
        for _ in range(10):
            await client.get(URL)

        start = time.perf_counter()

        results = await asyncio.gather(
            *[
                make_request(client, semaphore)
                for _ in range(TOTAL_REQUESTS)
            ]
        )

        elapsed = time.perf_counter() - start

    latencies = [latency for latency, _ in results]
    successes = sum(success for _, success in results)

    return {
        "throughput": TOTAL_REQUESTS / elapsed,
        "average": statistics.mean(latencies),
        "p50": percentile(latencies, 50),
        "p95": percentile(latencies, 95),
        "p99": percentile(latencies, 99),
        "errors": TOTAL_REQUESTS - successes,
    }


async def run_benchmark(concurrency):
    trials = []

    print(f"\nConcurrency {concurrency}")
    print("=====================")

    for trial_number in range(1, TRIALS + 1):
        result = await run_trial(concurrency)
        trials.append(result)

        print(
            f"Trial {trial_number}: "
            f"{result['throughput']:.2f} req/s, "
            f"avg {result['average']:.2f} ms, "
            f"p95 {result['p95']:.2f} ms, "
            f"errors {result['errors']}"
        )

        await asyncio.sleep(0.5)

    print("\n5-run average")
    print("---------------------")
    print(
        f"Throughput:      "
        f"{statistics.mean(r['throughput'] for r in trials):.2f} req/s"
    )
    print(
        f"Average latency: "
        f"{statistics.mean(r['average'] for r in trials):.2f} ms"
    )
    print(
        f"p50 latency:     "
        f"{statistics.mean(r['p50'] for r in trials):.2f} ms"
    )
    print(
        f"p95 latency:     "
        f"{statistics.mean(r['p95'] for r in trials):.2f} ms"
    )
    print(
        f"p99 latency:     "
        f"{statistics.mean(r['p99'] for r in trials):.2f} ms"
    )
    print(
        f"Errors:          "
        f"{sum(r['errors'] for r in trials)}"
    )


async def main():
    for concurrency in CONCURRENCY_LEVELS:
        await run_benchmark(concurrency)


if __name__ == "__main__":
    asyncio.run(main())
    
