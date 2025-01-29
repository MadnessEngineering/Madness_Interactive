# Madness Interactive

A collection of interconnected projects focused on building an ecosystem of AI-powered tools and agents for local development and automation.

## Core Projects

### Swarmonomicon

The central coordination system for our agent-based architecture. Swarmonomicon provides:

- Multi-agent system with centralized registry
- Async task coordination and processing
- Persistent state management
- Agent-to-agent communication
- Built-in agents for common tasks:
  - Git operations
  - Project initialization
  - Documentation generation
  - Task management
  - User interaction

### Omnispindle (In Development)

*Coming soon*

A distributed task execution and monitoring system that will:
- Coordinate between multiple agent instances
- Handle resource allocation and scheduling
- Provide real-time monitoring and metrics
- Support plugin-based extension
- Enable cross-project communication

### Event Systems

#### Original EventGhost Update
Modernizing the classic EventGhost automation tool with:
- Updated Python 3.x compatibility
- Modern UI/UX improvements
- Enhanced plugin system
- Better documentation

#### EventGhost-Rust
A complete rebuild of EventGhost in Rust, featuring:
- Native performance
- Modern async architecture
- Cross-platform support
- Enhanced security model
- Rust-based plugin system
- Integration with Swarmonomicon agents

### Tinker

A testing-oriented browser designed to work seamlessly with our event systems and agents:
- Headless and UI modes
- Event capture and replay
- Agent-based testing scenarios
- Integration with Swarmonomicon
- Cross-platform compatibility
- Plugin system for custom test scenarios

## Tools and Utilities

The `tools/` directory contains utilities for setting up and managing local AI pipelines:

- `git_assistant.py`: Git operations automation
- `project_agent.py`: Project management and initialization
- `project_init.py`: Project scaffolding and setup
- `setup_*.py`: Various setup scripts for:
  - RAG (Retrieval Augmented Generation)
  - Monitoring
  - Proxy configuration
  - API gateway
  - Knowledge base management
  - Model fine-tuning
  - Dataset preparation
  - Evaluation frameworks

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/madness_interactive.git
cd madness_interactive
```

2. Initialize submodules:
```bash
git submodule update --init --recursive
```

3. Set up the development environment:
```bash
# For Rust projects
cargo build

# For Python tools
pip install -r requirements.txt
```

## Project Structure

```
madness_interactive/
├── projects/
│   ├── common/
│   │   ├── Swarmonomicon/    # Agent coordination system
│   │   └── Omnispindle/      # Distributed task system
│   ├── rust/
│   │   ├── EventGhost-Rust/  # Rust rebuild of EventGhost
│   │   └── Tinker/           # Testing browser
│   └── python/
│       └── local-ai/         # Local AI pipeline tools
└── tools/                    # Utility scripts and tools
```

## Contributing

Each subproject maintains its own contribution guidelines. Please refer to the respective project directories for specific instructions.

## License

Each subproject may have its own license. Please refer to the individual project directories for license information.

## Roadmap

- [ ] Complete Swarmonomicon agent system
- [ ] Develop Omnispindle distributed task system
- [ ] Enhance EventGhost-Rust functionality
- [ ] Expand Tinker browser capabilities
- [ ] Improve local AI pipeline tools
- [ ] Create comprehensive documentation
- [ ] Develop integration tests across projects

## Contact

For questions, suggestions, or contributions, please:
1. Open an issue in the relevant project repository
2. Join our community discussions
3. Contact the maintainers directly

---
*"The only true wisdom is in knowing you know nothing." - Socrates*
