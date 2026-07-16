from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "configs/workflow.yml",
    "configs/otelcollectorconfig.yaml",
    "configs/price_book.json",
    "docs/architecture.md",
    "docs/upstream_nvidia.md",
    "docs/validation_checklist.md",
    "notebooks/nat_relay_token_economics_poc.ipynb",
    "sample_data/agent_trace_events.jsonl",
    "sample_data/relay_atof_events.jsonl",
    "sample_data/token_economics_summary.csv",
    "scripts/token_economics.py",
    "scripts/run_local_demo.py",
    "scripts/parse_relay_atof.py",
    "tests/test_token_economics.py",
]


def assert_exists() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f"Missing required files: {missing}")


def assert_jsonl(path: Path) -> None:
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{path}:{line_number}: invalid JSON") from exc


def assert_notebook(path: Path) -> None:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    if notebook.get("nbformat") != 4:
        raise AssertionError(f"{path}: expected nbformat 4")
    if not notebook.get("cells"):
        raise AssertionError(f"{path}: notebook has no cells")


def assert_wording() -> None:
    restricted = "cli" + "ent"
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if path.is_dir() or ".git" in path.parts:
            continue
        if path.suffix in {".pyc", ".zip"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if restricted in text.lower():
            hits.append(str(path.relative_to(ROOT)))
    if hits:
        raise AssertionError(f"Restricted wording found in: {hits}")


def main() -> int:
    assert_exists()
    assert_jsonl(ROOT / "sample_data/agent_trace_events.jsonl")
    assert_jsonl(ROOT / "sample_data/relay_atof_events.jsonl")
    assert_notebook(ROOT / "notebooks/nat_relay_token_economics_poc.ipynb")
    assert_wording()
    print("repo validation ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
