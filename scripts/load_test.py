"""Very small standard-library concurrency demonstration; not a benchmark."""

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib import request


def send(url: str, body: bytes) -> float:
    started = time.perf_counter()
    req = request.Request(url, data=body, method="POST", headers={"Content-Type":"application/json"})
    with request.urlopen(req, timeout=10) as response:
        response.read()
    return (time.perf_counter() - started) * 1000


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/predict")
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()
    payload = Path("sample_requests/high_risk_customer.json").read_bytes()

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(send, args.url, payload) for _ in range(args.requests)]
        latencies = [future.result() for future in as_completed(futures)]
    elapsed = time.perf_counter() - started
    print(f"Completed: {len(latencies)}")
    print(f"Elapsed seconds: {elapsed:.2f}")
    print(f"Requests/second: {len(latencies)/elapsed:.2f}")
    print(f"Average latency ms: {sum(latencies)/len(latencies):.2f}")
    print("This is a teaching demonstration, not a rigorous performance benchmark.")


if __name__ == "__main__":
    main()
