from __future__ import annotations

import argparse
from pathlib import Path

from token_economics import enrich_events
from token_economics import load_price_book
from token_economics import print_summary
from token_economics import read_jsonl
from token_economics import summarize
from token_economics import write_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local token economics demo.")
    parser.add_argument("--events", type=Path, default=Path("sample_data/agent_trace_events.jsonl"))
    parser.add_argument("--price-book", type=Path, default=Path("configs/price_book.json"))
    parser.add_argument("--out", type=Path, default=Path("sample_data/token_economics_summary.csv"))
    args = parser.parse_args()

    price_book = load_price_book(args.price_book)
    events = enrich_events(read_jsonl(args.events), price_book)
    write_csv(args.out, events)
    print_summary(summarize(events))
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

