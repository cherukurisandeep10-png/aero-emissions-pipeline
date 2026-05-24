.PHONY: setup run dbt test dashboard all clean help

# Default shell
SHELL := /bin/bash

help:
	@echo "AeroStream Development Helper Commands:"
	@echo "  setup      - Install virtual environment & python requirements"
	@echo "  run        - Execute real-time data ingestion (bronze & silver)"
	@echo "  dbt        - Compile and run dbt models (gold)"
	@echo "  test       - Execute dbt quality tests"
	@echo "  dashboard  - Run Streamlit analytics dashboard"
	@echo "  all        - Run ingest, transform, test, and host dashboard"
	@echo "  clean      - Delete database, bronze caches, and compiled dbt files"

setup:
	python3 -m venv venv
	source venv/bin/activate && pip install -r requirements.txt

run:
	PYTHONPATH=. python src/ingest.py

dbt:
	cd dbt_project && dbt run --profiles-dir .

test:
	cd dbt_project && dbt test --profiles-dir .

dashboard:
	streamlit run dashboard/app.py

all: run dbt test dashboard

clean:
	rm -rf data/bronze/*
	rm -f data/lakehouse.db
	rm -rf dbt_project/target/
	rm -rf dbt_project/dbt_packages/
