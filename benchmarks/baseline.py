import asyncio
import math
import time

import httpx

URL = "http://127.0.0.1:8000/items/1"
TOTAL_REQUESTS = 200
CONCURRENCY = 10


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


async def main():
    semaphore = asyncio.Semaphore(CONCURRENCY)

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
    errors = TOTAL_REQUESTS - successes

    print("\nPostgreSQL Baseline")
    print("-------------------")
    print(f"Requests:          {TOTAL_REQUESTS}")
    print(f"Concurrency:       {CONCURRENCY}")
    print(f"Throughput:        {TOTAL_REQUESTS / elapsed:.2f} req/s")
    print(f"Average latency:   {sum(latencies) / len(latencies):.2f} ms")
    print(f"p50 latency:       {percentile(latencies, 50):.2f} ms")
    print(f"p95 latency:       {percentile(latencies, 95):.2f} ms")
    print(f"p99 latency:       {percentile(latencies, 99):.2f} ms")
    print(f"Errors:            {errors}")


if __name__ == "__main__":
    asyncio.run(main())
    