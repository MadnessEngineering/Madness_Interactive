.PHONY: all help setup clean rag proxy knowledge gateway monitoring dataset evaluation finetuning

help:
	@echo Available commands:
	@echo   make all                       - Set up all tools
	@echo   make setup NAME=<target>      - Set up a specific tool (e.g., rag, proxy)
	@echo   make <target>                 - Set up a specific tool directly (e.g., rag, proxy)
	@echo   make clean                    - Clean up generated files

all: rag proxy knowledge gateway monitoring dataset evaluation finetuning

# Generic setup target using NAME variable
setup:
	@# Ensure NAME is provided
	@if [ -z "$(NAME)" ]; then \
		echo "Error: NAME variable is not set. Usage: make setup NAME=<target>"; \
		exit 1; \
	fi
	python3.11 tools/setup_$(NAME).py

# Pattern rule to handle individual targets
%:
	@# Check if the corresponding setup script exists
	@if [ ! -f tools/setup_$@.py ]; then \
		echo "Error: tools/setup_$@.py does not exist."; \
		exit 1; \
	fi
	python3.11 tools/setup_$@.py

clean:
	if exist ".env" del /f ".env" && \
	if exist "__pycache__" rd /s /q "__pycache__" && \
	if exist "data" rd /s /q "data" && \
	if exist "*.log" del /f "*.log" && \
	if exist "*.db" del /f "*.db" && \
	if exist "*.sqlite" del /f "*.sqlite"
