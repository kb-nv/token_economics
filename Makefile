.PHONY: demo validate test

demo:
	python scripts/run_local_demo.py --events sample_data/agent_trace_events.jsonl --price-book configs/price_book.json --out sample_data/token_economics_summary.csv

validate:
	python scripts/validate_repo.py

test:
	python -m unittest discover -s tests

