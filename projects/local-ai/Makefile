.PHONY: all help rag proxy knowledge gateway monitoring dataset evaluation finetuning clean

help:
	@echo Available commands:
	@echo   make all            - Set up all tools
	@echo   make rag           - Set up the RAG system for document querying
	@echo   make proxy         - Set up the API proxy for content filtering
	@echo   make knowledge     - Set up the local knowledge base system
	@echo   make gateway       - Set up the model API gateway
	@echo   make monitoring    - Set up the monitoring system
	@echo   make dataset       - Set up the dataset preparation tools
	@echo   make evaluation    - Set up the model evaluation suite
	@echo   make finetuning    - Set up the model fine-tuning tools
	@echo   make clean         - Clean up generated files
	@echo   make help          - Show this help message

all: rag proxy knowledge gateway monitoring dataset evaluation finetuning

rag:
	python3 tools/setup_rag.py

proxy:
	python3 tools/setup_proxy.py

knowledge:
	python3 tools/setup_knowledge.py

gateway:
	python3 tools/setup_gateway.py

monitoring:
	python3 tools/setup_monitoring.py

dataset:
	python3 tools/setup_dataset.py

evaluation:
	python3 tools/setup_evaluation.py

finetuning:
	python3 tools/setup_finetuning.py

clean:
	if exist ".env" del /f ".env"
	if exist "__pycache__" rd /s /q "__pycache__"
	if exist "data" rd /s /q "data"
	if exist "*.log" del /f "*.log"
	if exist "*.db" del /f "*.db"
	if exist "*.sqlite" del /f "*.sqlite"
