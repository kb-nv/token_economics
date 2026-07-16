# token_economics
Token economics observability prototype for NVIDIA NeMo Agent Toolkit and NeMo Relay, showing CFO-facing cost, latency, retry, and model-usage metrics across agentic workflows.


## Why This Exists

Agentic AI workflows can call multiple models, tools, retrievers, validators, and external services before producing one final answer. This repo shows how to measure the full economics of that pipeline: token usage, cost, latency, retries, model mix, and stage-level contribution.

## What It Measures

- Cost per workflow run
- Cost per successful run
- Cost by agent stage
- Cost by model
- Retry waste
- Token amplification ratio
- NAT vs Relay span contribution
- Monthly spend projection

## Architecture

NVIDIA NeMo Agent Toolkit provides the workflow and trace backbone. NeMo Relay-style ATOF events bring external or subprocess spans into the same economics view.

NAT / Relay telemetry -> normalized trace events -> token economics parser -> CFO-ready metrics

## Quick Start

Run the local demo:

```bash
python scripts/run_local_demo.py \
  --events sample_data/agent_trace_events.jsonl \
  --price-book configs/price_book.json \
  --out sample_data/token_economics_summary.csv
