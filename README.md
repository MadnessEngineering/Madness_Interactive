# Madness Interactive

A collection of interconnected projects focused on building an ecosystem of AI-powered tools and agents for local development and automation.


## Core Projects

### Swarmonomicon

![Cover Art](projects/common/Swarmonomicon/docs/assets/Cover-Art.jpeg)

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
│   ├── python/
│   │   ├── ai_interface/ [README](projects/python/ai_interface/README.md)
│   │   ├── mcp_server/ [README](projects/python/mcp_server/README.md)
│   │   ├── EventGhost/ [README](projects/python/EventGhost/README.md)
│   │   ├── simple-mqtt-server-agent/ [README](projects/python/simple-mqtt-server-agent/README.md)
│   │   ├── mqtt-get-var/ [README](projects/python/mqtt-get-var/README.md)
│   │   ├── local-ai/ [README](projects/python/local-ai/README.md)
│   │   ├── dvtTestKit/ [README](projects/python/dvtTestKit/README.md)
│   │   ├── SeleniumPageUtilities/ [README](projects/python/SeleniumPageUtilities/README.md)
│   │   ├── MqttLogger/ [README](projects/python/MqttLogger/README.md)
│   │   ├── LegoScry/ [README](projects/python/LegoScry/README.md)
│   │   └── games/
│   ├── powershell/
│   │   └── WinSystemSnapshot/ [README](projects/powershell/WinSystemSnapshot/README.md)
│   ├── lua/
│   │   ├── hammerspoon/ [README](projects/lua/hammerspoon/README.md)
│   │   └── LGS_script_template/ [README](projects/lua/LGS_script_template/README.md)
│   ├── rust/
│   │   ├── Tinker/ [README](projects/rust/Tinker/README.md)
│   │   └── EventGhost-Rust/ [README](projects/rust/EventGhost-Rust/README.md)
│   ├── common/
│   └── OS/
├── templates/
│   ├── python/
│   ├── rust/
│   └── [future-languages]/
├── docs/
│   ├── python/
│   └── rust/
├── scripts/
│   ├── init_python_project.sh
│   └── init_rust_project.sh
├── theming/
├── prompts/
└── README.md
```

## Subprojects

### Python Projects

#### [EventGhost](projects/python/EventGhost/README.md)
An advanced, yet easy-to-use extensible automation tool for Windows. Users can create macros entirely through the GUI to be triggered by events from any device, program or source with a corresponding plugin.

#### AI Interface & MCP Server
A modern AI-powered control system for EventGhost:
- [**ai_interface**](projects/python/ai_interface/README.md): Constructs and sends Events, Actions and Macros to EventGhost via XML
- [**mcp_server**](projects/python/mcp_server/README.md): Socket server that forwards commands from AI interface to EventGhost

#### MQTT Tools
- [**simple-mqtt-server-agent**](projects/python/simple-mqtt-server-agent/README.md): Lightweight MQTT server with agent capabilities
- [**mqtt-get-var**](projects/python/mqtt-get-var/README.md): Tool for retrieving variables via MQTT
- [**MqttLogger**](projects/python/MqttLogger/README.md): Logging system built on MQTT protocol

#### Testing & Automation
- [**dvtTestKit**](projects/python/dvtTestKit/README.md): Device validation testing toolkit
- [**SeleniumPageUtilities**](projects/python/SeleniumPageUtilities/README.md): Helper utilities for Selenium page testing
- [**LegoScry**](projects/python/LegoScry/README.md): Computer vision tools for LEGO brick recognition
- [**local-ai**](projects/python/local-ai/README.md): Local AI model integration tools

### Rust Projects

#### [EventGhost-Rust](projects/rust/EventGhost-Rust/README.md)
A modern, fast, and extensible reimplementation of EventGhost in Rust. Currently focusing on:
- Robust plugin system architecture
- Win32 API integration
- Core event system
- Plugin manifest format
- Dynamic library loading

#### [Tinker](projects/rust/Tinker/README.md)
A Madness engineered browser built for tinkerers and test enthusiasts:
- MQTT-powered control mechanisms
- Universal Workbench API
- Built-in diagnostic dashboard
- Test blueprint management
- Session versioning and comparison
- Precision event engineering

### PowerShell Projects

#### [WinSystemSnapshot](projects/powershell/WinSystemSnapshot/README.md)
Tools for capturing and analyzing Windows system state:
- System configuration snapshots
- Change detection
- State comparison tools
- Automated reporting

### Lua Projects

#### [Hammerspoon](projects/lua/hammerspoon/README.md)
Custom Hammerspoon configurations and extensions:
- Window management
- Application control
- System automation
- Custom spoons

#### [LGS Script Template](projects/lua/LGS_script_template/README.md)
Logitech Gaming Software script templates:
- Macro definitions
- Profile management
- Device configurations
- Event handlers

### Common & OS Projects
Shared utilities and OS-specific tools used across projects:
- Cross-project utilities
- System integration helpers
- Platform-specific implementations
- Shared configurations

## Features

- 📁 Organized template structure for multiple languages
- 🔧 Project initialization scripts
- 📝 Comprehensive documentation templates
- 🧪 Testing frameworks setup
- 🚀 CI/CD configurations
- 📊 Project management tools

## Getting Started

### Creating a New Project

1. Choose a language template:
   ```bash
   # For Python projects
   ./scripts/init_python_project.sh [template-name] [project-name]

   # For Rust projects
   ./scripts/init_rust_project.sh [template-name] [project-name]
   ```

2. Follow the template-specific README for additional setup steps

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
