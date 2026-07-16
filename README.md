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

```text
NAT / Relay telemetry -> normalized trace events -> token economics parser -> CFO-ready metrics
```

## Repo Layout

```text
.
├── configs/
│   ├── otelcollectorconfig.yaml
│   ├── price_book.json
│   └── workflow.yml
├── docs/
│   ├── architecture.md
│   ├── upstream_nvidia.md
│   └── validation_checklist.md
├── notebooks/
│   └── nat_relay_token_economics_poc.ipynb
├── sample_data/
│   ├── agent_trace_events.jsonl
│   ├── relay_atof_events.jsonl
│   └── token_economics_summary.csv
├── scripts/
│   ├── finance_tools.py
│   ├── parse_relay_atof.py
│   ├── run_local_demo.py
│   ├── token_economics.py
│   └── validate_repo.py
└── tests/
    └── test_token_economics.py
```

## Quick Start

Run the local economics demo:

```bash
python scripts/run_local_demo.py \
  --events sample_data/agent_trace_events.jsonl \
  --price-book configs/price_book.json \
  --out sample_data/token_economics_summary.csv
```

Validate the repo:

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests
```

Open the notebook:

```bash
jupyter notebook notebooks/nat_relay_token_economics_poc.ipynb
```

## NVIDIA Runtime Path

Install NVIDIA NeMo Agent Toolkit with observability extras:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install "nvidia-nat[opentelemetry,phoenix,profiler]"
nat --help
```

Run the workflow:

```bash
export NVIDIA_API_KEY=<set_me>
nat run --config_file configs/workflow.yml \
  --input "Explain the CFO-level cost and operational risk from this month's invoice and collections metrics."
```

Use Phoenix or OpenTelemetry to collect traces, then normalize token usage into the schema used by `scripts/token_economics.py`.

## Relay Path

Relay-style ATOF events can be normalized with:

```bash
python scripts/parse_relay_atof.py \
  --input sample_data/relay_atof_events.jsonl \
  --out sample_data/relay_normalized_events.jsonl
```

When NAT is installed, the same integration point can use `nat.experimental.relay_telemetry_bridge` to fold Relay ATOF events into NAT intermediate steps.

## Upstream References

- NVIDIA NeMo Agent Toolkit: https://github.com/NVIDIA/NeMo-Agent-Toolkit
- NVIDIA NAT docs: https://docs.nvidia.com/nemo/agent-toolkit/latest/index.html
- NAT observability: https://docs.nvidia.com/nemo/agent-toolkit/latest/run-workflows/observe/observe.html
- Relay telemetry bridge: https://docs.nvidia.com/nemo/agent-toolkit/latest/api/nat/experimental/relay_telemetry_bridge/index.html

## Important Notes

- `configs/price_book.json` contains placeholder demo prices. Replace them with approved pricing before using the numbers for a financial readout.
- The workflow config is a starter shape. Confirm component names against the installed NAT version with `nat info components`.
- The notebook defaults to `RUN_COMMANDS = True` for the local economics simulation.
- Live infrastructure commands are controlled separately with `RUN_LIVE_NVIDIA_COMMANDS` and `RUN_INFRA_COMMANDS`.
