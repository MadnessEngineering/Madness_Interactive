# Prompt Management Makefile

PROMPTS_DIR := prompts
CURSOR_RULES := .cursorrules
BACKUP_DIR := $(PROMPTS_DIR)/.backups
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)

.PHONY: list-prompts set-prompt backup-current new-prompt help

help:
	@echo "Prompt Management Commands:"
	@echo "  make list-prompts     - List all available prompts"
	@echo "  make set-prompt P=name - Set specific prompt as active (e.g., make set-prompt P=default_rules)"
	@echo "  make backup-current   - Backup current .cursorrules"
	@echo "  make new-prompt N=name - Create new prompt file"

list-prompts:
	@echo "Available prompts:"
	@ls -1 $(PROMPTS_DIR) | grep -v '^\.backups$$'

set-prompt:
	@if [ -z "$(P)" ]; then \
		echo "Error: Please specify prompt name with P=name"; \
		exit 1; \
	fi
	@if [ ! -f "$(PROMPTS_DIR)/$(P)" ]; then \
		echo "Error: Prompt '$(P)' not found in $(PROMPTS_DIR)"; \
		exit 1; \
	fi
	@make backup-current
	@cp "$(PROMPTS_DIR)/$(P)" "$(CURSOR_RULES)"
	@echo "Activated prompt: $(P)"

backup-current:
	@mkdir -p "$(BACKUP_DIR)"
	@if [ -f "$(CURSOR_RULES)" ]; then \
		cp "$(CURSOR_RULES)" "$(BACKUP_DIR)/cursorrules_$(TIMESTAMP)"; \
		echo "Backed up current rules to $(BACKUP_DIR)/cursorrules_$(TIMESTAMP)"; \
	fi

new-prompt:
	@if [ -z "$(N)" ]; then \
		echo "Error: Please specify prompt name with N=name"; \
		exit 1; \
	fi
	@if [ -f "$(PROMPTS_DIR)/$(N)" ]; then \
		echo "Error: Prompt '$(N)' already exists"; \
		exit 1; \
	fi
	@cp "$(PROMPTS_DIR)/default_rules" "$(PROMPTS_DIR)/$(N)"
	@echo "Created new prompt '$(N)' from default template"
