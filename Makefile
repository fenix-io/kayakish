.PHONY: help install dev test lint format clean docker-build docker-up docker-down docker-logs docker-shell docker-backup docker-restore

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Kayakish - Hull Analysis Tool"
	@echo "=============================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development commands
install: ## Install dependencies in virtual environment
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

dev: ## Run development server with uvicorn
	.venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	.venv/bin/pytest test/

coverage: ## Run tests with coverage report
	.venv/bin/pytest --cov=src --cov-report=term-missing --cov-report=html test/

lint: ## Run linter (flake8)
	.venv/bin/flake8 src/ test/

format: ## Format code with black
	.venv/bin/black src/ test/

clean: ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache htmlcov .coverage

# Docker commands
docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start application in Docker
	docker-compose up -d

docker-down: ## Stop application in Docker
	docker-compose down

docker-restart: ## Restart Docker containers
	docker-compose restart

docker-logs: ## View Docker container logs
	docker-compose logs -f

docker-shell: ## Open shell in Docker container
	docker exec -it kayakish /bin/bash

docker-ps: ## Show running containers
	docker-compose ps

docker-rebuild: ## Rebuild and restart Docker containers
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

docker-backup: ## Backup data volume to backup/kayak_data_backup.tar.gz
	@mkdir -p backup
	docker run --rm -v kayak_data:/data -v $$(pwd)/backup:/backup alpine tar czf /backup/kayak_data_backup_$$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
	@echo "Backup created in backup/ directory"

docker-restore: ## Restore data from latest backup (use BACKUP_FILE=path/to/backup.tar.gz to specify)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		LATEST=$$(ls -t backup/kayak_data_backup_*.tar.gz 2>/dev/null | head -1); \
		if [ -z "$$LATEST" ]; then \
			echo "No backup files found in backup/ directory"; \
			exit 1; \
		fi; \
		echo "Restoring from $$LATEST"; \
		docker run --rm -v kayak_data:/data -v $$(pwd):/backup alpine tar xzf /backup/$$LATEST -C /data; \
	else \
		echo "Restoring from $(BACKUP_FILE)"; \
		docker run --rm -v kayak_data:/data -v $$(dirname $(BACKUP_FILE)):/backup alpine tar xzf /backup/$$(basename $(BACKUP_FILE)) -C /data; \
	fi
	@echo "Restore completed"

docker-clean: ## Remove Docker containers, images, and volumes
	docker-compose down -v
	docker rmi kayakish:latest 2>/dev/null || true
	@echo "Docker cleanup completed"

# Convenience shortcuts
build: docker-build ## Alias for docker-build
up: docker-up ## Alias for docker-up
down: docker-down ## Alias for docker-down
logs: docker-logs ## Alias for docker-logs
shell: docker-shell ## Alias for docker-shell
