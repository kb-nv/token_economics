# Upstream NVIDIA Foundation

This repo is intentionally a small implementation layer on top of NVIDIA NeMo Agent Toolkit.

## Primary Upstream

- GitHub: https://github.com/NVIDIA/NeMo-Agent-Toolkit
- Docs: https://docs.nvidia.com/nemo/agent-toolkit/latest/index.html

## Relevant NVIDIA Areas

- Workflow construction and agent execution.
- LLM, tool, retriever, and workflow configuration.
- `nat run` and `nat eval` execution paths.
- Observability exporters for Phoenix, OpenTelemetry, file output, and custom exporters.
- Profiling and performance monitoring.
- Token usage data models.
- Relay ATOF bridge through `nat.experimental.relay_telemetry_bridge`.

## Why This Repo Exists

NAT provides the workflow and trace backbone. This repo adds a thin economics layer:

- A normalized span schema.
- A price-book based cost model.
- NAT and Relay trace aggregation.
- CFO-ready summary outputs.
- Sample data and validation checks.

## Suggested GitHub Relationship

Keep this repo as an application repo, not a fork. Add the NVIDIA repo as an upstream reference in docs or as an optional submodule only if you need local examples:

```bash
git submodule add https://github.com/NVIDIA/NeMo-Agent-Toolkit vendor/NeMo-Agent-Toolkit
```

