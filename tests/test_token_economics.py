from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from token_economics import enrich_events  # noqa: E402
from token_economics import event_cost_usd  # noqa: E402
from token_economics import load_price_book  # noqa: E402
from token_economics import read_jsonl  # noqa: E402
from token_economics import summarize  # noqa: E402
from token_economics import workflow_success  # noqa: E402


class TokenEconomicsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.price_book = load_price_book(ROOT / "configs" / "price_book.json")

    def test_event_cost_with_cached_tokens(self) -> None:
        event = {
            "model": "nvidia/nemotron-3-nano-30b-a3b",
            "prompt_tokens": 2450,
            "completion_tokens": 260,
            "reasoning_tokens": 0,
            "cached_tokens": 600,
        }
        self.assertAlmostEqual(event_cost_usd(event, self.price_book), 0.0006875)

    def test_summary_counts_retry_but_keeps_trace_successful(self) -> None:
        events = enrich_events(
            read_jsonl(ROOT / "sample_data" / "agent_trace_events.jsonl"),
            self.price_book,
        )
        success = workflow_success(events)
        self.assertEqual(success, {"run-001": True, "run-002": True})
        summary = summarize(events)
        self.assertEqual(summary["workflow_runs"], 2)
        self.assertEqual(summary["successful_runs"], 2)
        self.assertGreater(summary["retry_cost_usd"], 0)
        self.assertFalse(math.isnan(summary["avg_cost_per_success_usd"]))


if __name__ == "__main__":
    unittest.main()

