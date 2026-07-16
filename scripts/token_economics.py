from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


CSV_FIELDS = [
    "trace_id",
    "source",
    "stage",
    "event_type",
    "model",
    "prompt_tokens",
    "completion_tokens",
    "reasoning_tokens",
    "cached_tokens",
    "total_tokens",
    "latency_ms",
    "success",
    "retry",
    "cost_usd",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            rows.append(row)
    return rows


def load_price_book(path: Path) -> dict[str, dict[str, float]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("price book must be a JSON object")
    return raw


def as_int(value: Any) -> int:
    if value in (None, ""):
        return 0
    return int(value)


def event_cost_usd(event: dict[str, Any], price_book: dict[str, dict[str, float]]) -> float:
    model = event.get("model")
    if not model:
        return 0.0
    if model not in price_book:
        raise KeyError(f"missing price for model: {model}")

    rates = price_book[model]
    prompt_tokens = as_int(event.get("prompt_tokens"))
    completion_tokens = as_int(event.get("completion_tokens"))
    reasoning_tokens = as_int(event.get("reasoning_tokens"))
    cached_tokens = as_int(event.get("cached_tokens"))
    billable_prompt_tokens = max(prompt_tokens - cached_tokens, 0)

    return (
        billable_prompt_tokens * float(rates["prompt_per_million"])
        + completion_tokens * float(rates["completion_per_million"])
        + reasoning_tokens * float(rates["reasoning_per_million"])
        + cached_tokens * float(rates["cached_prompt_per_million"])
    ) / 1_000_000


def enrich_events(
    events: Iterable[dict[str, Any]],
    price_book: dict[str, dict[str, float]],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for event in events:
        row = dict(event)
        row["prompt_tokens"] = as_int(row.get("prompt_tokens"))
        row["completion_tokens"] = as_int(row.get("completion_tokens"))
        row["reasoning_tokens"] = as_int(row.get("reasoning_tokens"))
        row["cached_tokens"] = as_int(row.get("cached_tokens"))
        row["total_tokens"] = (
            row["prompt_tokens"] + row["completion_tokens"] + row["reasoning_tokens"]
        )
        row["cost_usd"] = event_cost_usd(row, price_book)
        enriched.append(row)
    return enriched


def group_sum(events: Iterable[dict[str, Any]], key: str, value: str) -> dict[str, float]:
    out: defaultdict[str, float] = defaultdict(float)
    for row in events:
        out[str(row.get(key) or "none")] += float(row.get(value) or 0.0)
    return dict(sorted(out.items(), key=lambda item: item[1], reverse=True))


def workflow_success(events: Iterable[dict[str, Any]]) -> dict[str, bool]:
    success_by_trace: defaultdict[str, bool] = defaultdict(lambda: True)
    for row in events:
        trace_id = str(row.get("trace_id") or "unknown")
        success_by_trace[trace_id]
        if row.get("success") is False and not row.get("retry"):
            success_by_trace[trace_id] = False
    return dict(success_by_trace)


def summarize(events: list[dict[str, Any]]) -> dict[str, Any]:
    trace_cost = group_sum(events, "trace_id", "cost_usd")
    trace_latency = group_sum(events, "trace_id", "latency_ms")
    success = workflow_success(events)
    successful_runs = sum(1 for ok in success.values() if ok)
    total_cost = sum(float(row.get("cost_usd") or 0.0) for row in events)
    total_tokens = sum(as_int(row.get("total_tokens")) for row in events)
    retry_cost = sum(float(row.get("cost_usd") or 0.0) for row in events if row.get("retry"))
    final_answer_tokens = sum(
        as_int(row.get("completion_tokens")) for row in events if row.get("stage") == "cfo_summary"
    )
    amplification_ratio = total_tokens / final_answer_tokens if final_answer_tokens else math.nan

    return {
        "workflow_runs": len(trace_cost),
        "successful_runs": successful_runs,
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 6),
        "avg_cost_per_run_usd": round(total_cost / len(trace_cost), 6) if trace_cost else 0.0,
        "avg_cost_per_success_usd": round(total_cost / successful_runs, 6)
        if successful_runs
        else math.nan,
        "retry_cost_usd": round(retry_cost, 6),
        "token_amplification_ratio": round(amplification_ratio, 2)
        if not math.isnan(amplification_ratio)
        else math.nan,
        "p50_latency_ms": round(statistics.median(trace_latency.values()), 1)
        if trace_latency
        else 0.0,
        "cost_by_stage": group_sum(events, "stage", "cost_usd"),
        "cost_by_model": group_sum(events, "model", "cost_usd"),
        "cost_by_source": group_sum(events, "source", "cost_usd"),
    }


def write_csv(path: Path, events: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in events:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def print_summary(summary: dict[str, Any]) -> None:
    print("Executive metrics")
    for key, value in summary.items():
        if isinstance(value, dict):
            continue
        print(f"  {key}: {value}")

    for section in ("cost_by_stage", "cost_by_model", "cost_by_source"):
        print(f"\n{section}")
        total = sum(float(v) for v in summary[section].values())
        for name, value in summary[section].items():
            share = (float(value) / total) if total else 0.0
            print(f"  {name:36} ${float(value):.6f}  {share:6.1%}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute token economics from normalized trace events.")
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--price-book", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    price_book = load_price_book(args.price_book)
    events = enrich_events(read_jsonl(args.events), price_book)
    write_csv(args.out, events)
    print_summary(summarize(events))
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

