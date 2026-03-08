.PHONY: help install test lint clean run setup

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make setup      - Complete setup (install + pull model)"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make clean      - Clean temporary files"
	@echo "  make run        - Run web application"

install:
	pip install -r requirements.txt

setup: install
	ollama pull llama2
	mkdir -p audio_segments final_podcasts

test:
	python -m pytest tests/ -v --cov=. --cov-report=term-missing

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	black --check .

format:
	black .

clean:
	rm -rf __pycache__ .pytest_cache .coverage
	rm -rf audio_segments/* final_podcasts/*
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python web_podcast_ollama.py

dev:
	FLASK_ENV=development python web_podcast_ollama.py
