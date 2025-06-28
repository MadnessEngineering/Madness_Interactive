# Madness Interactive Makefile
# Comprehensive project management and submodule workflow

.PHONY: help new list-projects clean-all status centralize-cursor-rules list-cursor-rules restore-cursor-rules mindmap mindmap-interactive mindmap-svg mindmap-json mindmap-all mindmap-help

# Default target
help:
	@echo "Madness Interactive Project Manager"
	@echo ""
	@echo "Project Management:"
	@echo "  new NAME=<name> [TYPE=python|rust|typescript|lua|common] - Create new project"
	@echo "  list-projects  - List all submodules"
	@echo "  status         - Check submodule status"
	@echo "  clean-all      - Clean build artifacts"
	@echo ""
	@echo "Cursor Rules:"
	@echo "  list-cursor-rules      - Show projects with cursor rules"
	@echo "  centralize-cursor-rules - Move rules to central location"
	@echo "  restore-cursor-rules TARGET=<path> - Restore rules to project"

# Variables
NAME ?=
TYPE ?= python
DESC ?= A new project in the Madness Interactive ecosystem
PROJECTS_DIR = projects/common
DOCS_CHAT_DIR = /Users/d.edens/lab/madness_interactive/docs/cursor_chathistory
CURSOR_RULES_DIR = /Users/d.edens/lab/madness_interactive/cursor_rules
WORKSPACE_ROOT = /Users/d.edens/lab/madness_interactive

# Cursor Rules Management Targets

# List all submodules that have .cursor/rules/ directories
list-cursor-rules:
	@echo "Scanning for .cursor/rules/ directories in submodules..."
	@echo "=================================================="
	@for submodule in $$(git submodule foreach --quiet 'echo $$sm_path'); do \
		if [ -d "$$submodule/.cursor/rules" ]; then \
			echo "📁 $$submodule"; \
			echo "   Rules found: $$(ls -1 $$submodule/.cursor/rules/ 2>/dev/null | wc -l | tr -d ' ') files"; \
			ls -la "$$submodule/.cursor/rules/" | grep -E '\.(mdc|md)$$' | awk '{print "   - " $$9}' || true; \
			echo ""; \
		fi; \
	done
	@echo "Current centralized rules structure:"
	@echo "=================================================="
	@find $(CURSOR_RULES_DIR) -name "*.mdc" -o -name "*.md" | sed 's|$(CURSOR_RULES_DIR)/||' | sort

# Centralize all .cursor/rules/ directories from submodules
centralize-cursor-rules:
	@echo "Centralizing cursor rules from all submodules..."
	@echo "=================================================="
	@for submodule in $$(git submodule foreach --quiet 'echo $$sm_path'); do \
		if [ -d "$$submodule/.cursor/rules" ] && [ ! -L "$$submodule/.cursor/rules" ]; then \
			echo "🔄 Processing: $$submodule"; \
			PROJECT_NAME=$$(basename "$$submodule"); \
			DEST_DIR="$(CURSOR_RULES_DIR)/$$PROJECT_NAME"; \
			echo "   Moving $$submodule/.cursor/rules/ to $$DEST_DIR"; \
			mkdir -p "$$DEST_DIR"; \
			cp -r "$$submodule/.cursor/rules/"* "$$DEST_DIR/" 2>/dev/null || true; \
			rm -rf "$$submodule/.cursor/rules"; \
			echo "   Creating symlink: $$submodule/.cursor/rules -> $$DEST_DIR"; \
			mkdir -p "$$submodule/.cursor"; \
			ln -s "$$DEST_DIR" "$$submodule/.cursor/rules"; \
			echo "   ✅ Centralized $$PROJECT_NAME rules"; \
			echo ""; \
		elif [ -L "$$submodule/.cursor/rules" ]; then \
			echo "⏭️  Skipping $$submodule (already symlinked)"; \
		fi; \
	done
	@echo "Committing centralized rules..."
	cd $(CURSOR_RULES_DIR) && \
	git add . && \
	git commit -m "Centralize cursor rules from submodules - automated migration" && \
	git push
	@echo "🎉 Cursor rules centralization complete!"

# Restore rules from centralized location back to a specific submodule
restore-cursor-rules:
	@if [ -z "$(TARGET)" ]; then \
		echo "Error: TARGET parameter is required. Usage: make restore-cursor-rules TARGET=path/to/submodule"; \
		exit 1; \
	fi
	@if [ ! -d "$(TARGET)" ]; then \
		echo "Error: Target directory $(TARGET) does not exist"; \
		exit 1; \
	fi
	@PROJECT_NAME=$$(basename "$(TARGET)")
	@CENTRALIZED_DIR="$(CURSOR_RULES_DIR)/$$PROJECT_NAME"
	@if [ ! -d "$$CENTRALIZED_DIR" ]; then \
		echo "Error: No centralized rules found for $$PROJECT_NAME"; \
		exit 1; \
	fi
	@echo "Restoring cursor rules for $(TARGET)..."
	@if [ -L "$(TARGET)/.cursor/rules" ]; then \
		rm "$(TARGET)/.cursor/rules"; \
	fi
	@mkdir -p "$(TARGET)/.cursor/rules"
	@cp -r "$$CENTRALIZED_DIR/"* "$(TARGET)/.cursor/rules/"
	@echo "✅ Rules restored to $(TARGET)/.cursor/rules/"

# Create new project and add as submodule
new:
	@if [ -z "$(NAME)" ]; then \
		echo "Error: NAME parameter is required. Usage: make new NAME=project-name"; \
		exit 1; \
	fi
	@echo "Creating new $(TYPE) project: $(NAME)"
	@echo "Description: $(DESC)"

	# Create project directory
	mkdir -p $(PROJECTS_DIR)/$(TYPE)/$(NAME)
	cd $(PROJECTS_DIR)/$(TYPE)/$(NAME) && \
	git init && \
	echo "# $(NAME)" > README.md && \
	echo "" >> README.md && \
	echo "$(DESC)" >> README.md && \
	echo "" >> README.md && \
	echo "## Installation" >> README.md && \
	echo "" >> README.md && \
	echo "## Usage" >> README.md && \
	echo "" >> README.md && \
	echo "## Contributing" >> README.md && \
	echo "" >> README.md && \
	echo "## License" >> README.md && \
	echo "" >> README.md && \
	echo "MIT License - See LICENSE file for details" >> README.md

	# Create CHANGELOG.md
	cd $(PROJECTS_DIR)/$(TYPE)/$(NAME) && \
	echo "# Changelog" > CHANGELOG.md && \
	echo "" >> CHANGELOG.md && \
	echo "All notable changes to this project will be documented in this file." >> CHANGELOG.md && \
	echo "" >> CHANGELOG.md && \
	echo "## [Unreleased]" >> CHANGELOG.md && \
	echo "" >> CHANGELOG.md && \
	echo "### Added" >> CHANGELOG.md && \
	echo "- Initial project setup" >> CHANGELOG.md

	# Create docs directory
	cd $(PROJECTS_DIR)/$(TYPE)/$(NAME) && mkdir -p docs

	# Setup language-specific files
	$(MAKE) setup-$(TYPE)-project DIR=$(PROJECTS_DIR)/$(TYPE)/$(NAME) NAME=$(NAME)

	# Setup .specstory/history system
	cd $(PROJECTS_DIR)/$(TYPE)/$(NAME) && \
	mkdir -p .specstory/history && \
	echo "" > .specstory/history/.temp

	# Setup centralized cursor rules system
	$(MAKE) setup-cursor-rules DIR=$(PROJECTS_DIR)/$(TYPE)/$(NAME) NAME=$(NAME)

	# Initial git commit
	cd $(PROJECTS_DIR)/$(TYPE)/$(NAME) && \
	git add -A && \
	git commit -m "Initial project setup for $(NAME) - $(TYPE) project with docs, changelog, and language-specific configuration"

	# Create GitHub repository
	cd $(PROJECTS_DIR)/$(TYPE)/$(NAME) && \
	gh repo create $(NAME) --public --description "$(DESC)" --clone=false

	# Push to origin
	cd $(PROJECTS_DIR)/$(TYPE)/$(NAME) && \
	git branch -M main && \
	git remote add origin git@github.com:DanEdens/$(NAME).git && \
	git push --set-upstream origin main

	# Setup chat history symlink system
	$(MAKE) setup-chat-history DIR=$(PROJECTS_DIR)/$(TYPE)/$(NAME) NAME=$(NAME)

	# Add as submodule to main repo
	git submodule add git@github.com:DanEdens/$(NAME).git $(PROJECTS_DIR)/$(TYPE)/$(NAME)
	git add .gitmodules $(PROJECTS_DIR)/$(TYPE)/$(NAME)
	git commit -m "Add $(NAME) as submodule - $(DESC)"
	git push

	@echo "✅ Project $(NAME) created and added as submodule successfully!"

# Setup centralized cursor rules system for new projects
setup-cursor-rules:
	@echo "Setting up centralized cursor rules for $(NAME)..."
	@PROJECT_RULES_DIR="$(CURSOR_RULES_DIR)/$(NAME)"
	@mkdir -p "$$PROJECT_RULES_DIR"
	@cd $(DIR) && mkdir -p .cursor
	@echo "---" > "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "description: Project-specific rules for $(NAME)" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "globs:" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "alwaysApply: false" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "---" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "# $(NAME) Project Rules" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "## Project Overview" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "$(DESC)" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "## Development Guidelines" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "- Follow the established patterns from the madness_interactive ecosystem" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "- Integrate with MCP todo server for task management" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@echo "- Use jj for version control following the jj-mcp-workflow patterns" >> "$$PROJECT_RULES_DIR/project-rules.mdc"
	@cd $(DIR) && ln -s "$$PROJECT_RULES_DIR" .cursor/rules
	@echo "Cursor rules linked for $(NAME): .cursor/rules -> $$PROJECT_RULES_DIR"

	# Commit to cursor rules repo
	cd $(CURSOR_RULES_DIR) && \
	git add . && \
	git commit -m "Add initial cursor rules for $(NAME)" && \
	git push

# Setup chat history symlink system
setup-chat-history:
	@echo "Setting up chat history system for $(NAME)..."
	cd $(DIR) && \
	DEST_DIR="$(DOCS_CHAT_DIR)/$(NAME)" && \
	mv .specstory/history "$$DEST_DIR" && \
	ln -s "$$DEST_DIR" .specstory/history && \
	echo "Chat history moved to: $$DEST_DIR"

	# Commit chat history to main docs repo
	cd $(DOCS_CHAT_DIR) && \
	git add . && \
	git commit -m "Add chat history for $(NAME)" && \
	git push

# Language-specific project setup
setup-python-project:
	cd $(DIR) && \
	echo "# $(NAME) FastMCP Server" > Makefile && \
	echo "" >> Makefile && \
	echo ".PHONY: install run test coverage clean status" >> Makefile && \
	echo "" >> Makefile && \
	echo "install:" >> Makefile && \
	echo "	uv pip install -r requirements.txt" >> Makefile && \
	echo "	uv pip install -r requirements-dev.txt" >> Makefile && \
	echo "" >> Makefile && \
	echo "run:" >> Makefile && \
	echo "	python -m src.$(NAME)" >> Makefile && \
	echo "" >> Makefile && \
	echo "test:" >> Makefile && \
	echo "	pytest tests/" >> Makefile && \
	echo "" >> Makefile && \
	echo "coverage:" >> Makefile && \
	echo "	pytest --cov=src tests/" >> Makefile && \
	echo "" >> Makefile && \
	echo "clean:" >> Makefile && \
	echo "	find . -name '__pycache__' -exec rm -r {} +" >> Makefile && \
	echo "" && \
	echo "fastmcp" > requirements.txt && \
	echo "pytest" > requirements-dev.txt && \
	echo "pytest-cov" >> requirements-dev.txt && \
	mkdir -p src tests && \
	echo "from fastmcp import FastMCP" > src/__init__.py && \
	echo "" > tests/__init__.py && \
	echo "__pycache__/" > .gitignore && \
	echo "*.pyc" >> .gitignore && \
	echo ".coverage" >> .gitignore && \
	echo ".pytest_cache/" >> .gitignore

setup-rust-project:
	cd $(DIR) && \
	cargo init --name $(NAME) && \
	echo "target/" >> .gitignore && \
	echo "Cargo.lock" >> .gitignore

setup-typescript-project:
	cd $(DIR) && \
	npm init -y && \
	echo "node_modules/" > .gitignore && \
	echo "dist/" >> .gitignore && \
	echo "*.log" >> .gitignore && \
	mkdir -p src && \
	echo 'console.log("Hello from $(NAME)!");' > src/index.ts

setup-lua-project:
	cd $(DIR) && \
	echo "-- $(NAME) Lua Project" > init.lua && \
	echo "*.log" > .gitignore

setup-common-project:
	cd $(DIR) && \
	echo "# Common project - language agnostic" > README.md

# List all submodules
list-projects:
	@echo "Current submodules:"
	@git submodule foreach 'echo "  $$name"'

# Check status of all submodules
status:
	@echo "Checking status of all submodules..."
	git submodule foreach "echo '=== $$name ===' && git status --short"

# Clean all projects
clean-all:
	@echo "Cleaning all projects..."
	find $(PROJECTS_DIR) -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(PROJECTS_DIR) -name "*.pyc" -delete 2>/dev/null || true
	find $(PROJECTS_DIR) -name "target" -type d -exec rm -rf {} + 2>/dev/null || true
	find $(PROJECTS_DIR) -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

# Mind Map Generation
mindmap: ## Generate interactive HTML mind map
	@echo "🧠 Generating Madness Interactive Mind Map..."
	@python3 scripts/mindmap_generator.py --format html --interactive --output docs/mindmap.html
	@echo "✨ Mind map generated at docs/mindmap.html"

mindmap-interactive: mindmap ## Alias for interactive mind map

mindmap-svg: ## Generate SVG mind map
	@echo "🎨 Generating SVG mind map..."
	@python3 scripts/mindmap_generator.py --format svg --output docs/mindmap.svg
	@echo "✨ SVG mind map generated at docs/mindmap.svg"

mindmap-json: ## Generate JSON data export
	@echo "📄 Generating JSON mind map data..."
	@python3 scripts/mindmap_generator.py --format json --output docs/mindmap.json
	@echo "✨ JSON data generated at docs/mindmap.json"

mindmap-dot: ## Generate DOT/Graphviz mind map
	@echo "🎯 Generating DOT mind map..."
	@python3 scripts/mindmap_generator.py --format dot --output docs/mindmap.dot
	@echo "✨ DOT file generated at docs/mindmap.dot"
	@echo "   To render: dot -Tpng docs/mindmap.dot -o docs/mindmap.png"

mindmap-all: ## Generate all mind map formats
	@echo "🚀 Generating all mind map formats..."
	@make mindmap
	@make mindmap-svg
	@make mindmap-json
	@make mindmap-dot
	@echo "🎉 All mind maps generated in docs/ directory!"

mindmap-help: ## Show mind map generator help
	@python3 scripts/mindmap_generator.py --help
