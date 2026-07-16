# Validation Checklist

## Local Repo Checks

- `python scripts/validate_repo.py`
- `python -m unittest discover -s tests`
- `python scripts/run_local_demo.py --events sample_data/agent_trace_events.jsonl --price-book configs/price_book.json --out sample_data/token_economics_summary.csv`
- Confirm `sample_data/token_economics_summary.csv` includes `cost_usd`.

## NAT Runtime Checks

- Install `nvidia-nat` with observability extras.
- Confirm `nat --help` and `nat --version`.
- Confirm tracing components with `nat info components -t tracing`.
- Run the starter workflow with a tiny prompt.
- Confirm telemetry includes function spans, LLM spans, latency, and token usage.

## Relay Checks

- Collect ATOF JSONL from the external process.
- Run `scripts/parse_relay_atof.py`.
- Confirm normalized Relay events join to the same workflow run or trace id.
- If NAT is installed, test `nat.experimental.relay_telemetry_bridge`.

## Financial Readout Checks

- Replace demo prices with approved rates.
- Confirm cached-token and reasoning-token billing rules.
- Count retry events separately.
- Run at least 50 representative CFO prompts.
- Compare quality and cost together before claiming savings.

