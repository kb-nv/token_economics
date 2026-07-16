from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def normalize_atof_event(event: dict[str, Any]) -> dict[str, Any]:
    token_usage = event.get("token_usage") or event.get("usage") or {}
    if not isinstance(token_usage, dict):
        token_usage = {}

    return {
        "trace_id": event.get("trace_id")
        or event.get("trajectory_id")
        or event.get("run_id")
        or "unknown",
        "source": "relay",
        "stage": event.get("name") or event.get("stage") or event.get("event_type") or "relay_event",
        "event_type": event.get("event_type") or event.get("type") or "UNKNOWN",
        "model": event.get("model") or token_usage.get("model"),
        "prompt_tokens": token_usage.get("prompt_tokens", event.get("prompt_tokens", 0)),
        "completion_tokens": token_usage.get(
            "completion_tokens", event.get("completion_tokens", 0)
        ),
        "reasoning_tokens": token_usage.get("reasoning_tokens", event.get("reasoning_tokens", 0)),
        "cached_tokens": token_usage.get("cached_tokens", event.get("cached_tokens", 0)),
        "latency_ms": event.get("duration_ms") or event.get("latency_ms") or 0,
        "success": event.get("success", True),
        "retry": event.get("retry", False),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Relay ATOF JSONL into economics events.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    events = [normalize_atof_event(row) for row in read_jsonl(args.input)]
    write_jsonl(args.out, events)
    print(f"Wrote {len(events)} normalized events to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

