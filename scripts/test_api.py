"""Small reusable client for local, VM, Docker and Kubernetes demonstrations."""

import argparse
import json
from pathlib import Path
from urllib import error, request


def get_json(url: str) -> dict:
    with request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--request-file",
        type=Path,
        default=Path("sample_requests/high_risk_customer.json"),
    )
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    try:
        print("Health:", json.dumps(get_json(f"{base}/health"), indent=2))
        print("Ready:", json.dumps(get_json(f"{base}/ready"), indent=2))
        print("Model info:", json.dumps(get_json(f"{base}/model-info"), indent=2))
        payload = json.loads(args.request_file.read_text(encoding="utf-8"))
        print("Prediction:", json.dumps(post_json(f"{base}/predict", payload), indent=2))
    except error.HTTPError as exc:
        print(f"HTTP error {exc.code}: {exc.read().decode('utf-8')}")
        raise SystemExit(1) from exc
    except error.URLError as exc:
        print(f"Could not reach API: {exc.reason}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
