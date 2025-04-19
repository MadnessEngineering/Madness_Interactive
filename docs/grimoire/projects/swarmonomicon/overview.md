# SWARMONOMICON: THE GRIMOIRE THAT BINDS THEM ALL
*"A central nervous system for our agents of chaos, designed to coordinate the madness!"*

`#swarmonomicon` `#agents` `#rust` `#ai`

## ESSENCE OF THE BEAST

The Swarmonomicon is the central intelligence system of our mad laboratory, coordinating a diverse hive of specialized agents to perform various tasks like git operations, project initialization, and creative content generation. Built with Rust for maximum performance and stability, it represents the pinnacle of our agent-based architecture.

![Swarmonomicon Conceptual Diagram](../../../assets/images/swarmonomicon_concept.png) *(TODO: Create this arcane diagram)*

## CORE FUNCTIONALITIES

### 🧠 AGENT SYSTEM
- **Base Agent Trait**: Defines the fundamental abilities all agents must possess
  - Message processing
  - Tool handling
  - State management
  - Configuration
  - Todo list integration
- **Implementation**: Async-first with proper error handling and resource management

### 📚 REGISTRY SYSTEM
- **Global Registry**: Maintains references to all available agents
  - Thread-safe access via `Arc<RwLock<AgentRegistry>>`
  - Dynamic agent registration
  - Agent lookup by name
  - Feature-gated agent loading
- **Status**: Fully implemented with proper concurrency control

### 🔄 TRANSFER SERVICE
- **State Machine**: Manages transitions between agents
  - Basic and complex workflow transitions
  - State validation
  - State persistence
- **Message Routing**: Directs messages to appropriate agents
  - Proper locking for concurrent access
  - Error handling for missing agents
  - Message metadata preservation
- **Context Preservation**: Maintains context across agent transfers

### 🤖 AI COMMUNICATION LAYER
- **Centralized AI Client**: Manages all LLM interactions
  - Configurable endpoint (default: local LM Studio)
  - Consistent message formatting
  - Conversation history management
  - System prompt handling
  - Model configuration
  - Rate limiting and resource protection
  - GPT-4 Batch Processing

### 📋 TASK PROCESSING SYSTEM
- **Todo List**: Manages tasks across agents
  - Task persistence
  - Concurrent access handling
  - Priority-based processing
  - Task status tracking
  - AI-powered task enhancement

## SPECIALIZED AGENTS

### 🔧 GIT ASSISTANT AGENT
- Handles git operations
- Generates commit messages using AI
- Manages branches and merges
- Status: ✅ Complete with testing

### 🏗️ PROJECT INIT AGENT
- Creates new project structures
- Sets up configuration files
- Initializes git repositories
- Status: 🔄 Partially implemented

### 📝 HAIKU AGENT
- Generates creative content
- Integration with git
- Status: 🔄 Basic implementation complete

### 👋 GREETER AGENT
- Entry point for user interaction
- Command routing
- Help system
- AI-powered conversation management
- Status: ✅ Well implemented with testing

### 🌐 BROWSER AGENT
- Handles browser automation tasks
- Status: 🔄 Partially implemented

### 🎮 RL AGENT
- Reinforcement Learning capabilities
- Basic implementation with Flappy Bird environment
- Q-Learning implementation
- Status: 🔄 Under development

## TOOL SYSTEM

The Swarmonomicon comes equipped with various tools for agent use:

- **Git operations**: Commit, branch, merge
- **Todo management**: Create, update, and track tasks
- **Project setup**: Initialize new projects with templates
- **GPT-4 batch processing**: Efficient handling of large prompts
- **YOLO object detection**: Identify objects in images
- **Goose performance testing**: Stress test systems
- **Screenshot detection**: Analyze screen contents

## GETTING STARTED

### Prerequisites
- Rust 1.75 or later
- Local LLM (Ollama recommended)
- MongoDB for task storage
- MQTT broker for communication

### Installation

1. Clone the repository:
```bash
git clone https://github.com/DanEdens/madness_interactive.git
cd madness_interactive/projects/common/Swarmonomicon
```

2. Build the project:
```bash
cargo build
```

3. Run the main application:
```bash
cargo run
```

### Configuration

The Swarmonomicon is configured through environment variables:

- `AI_ENDPOINT`: URL of the AI provider (default: `http://localhost:1234/v1`)
- `AI_MODEL`: Model to use (default: `gpt-3.5-turbo`)
- `MONGODB_URI`: MongoDB connection string
- `MQTT_BROKER`: MQTT broker address
- `LOG_LEVEL`: Logging verbosity

## ARCHITECTURE DETAILS

The project is organized into several key modules:

- `src/agents/`: Different agent implementations
- `src/types/`: Core type definitions
- `src/tools/`: Tool implementations
- `src/api/`: REST endpoints and WebSocket handler
- `src/config/`: Configuration management
- `src/ai/`: AI client implementation
- `src/state/`: State machine definitions

For a more detailed architecture overview, see [Swarmonomicon Architecture](../../arcana/swarmonomicon_architecture.md).

## CURRENT STATUS

The Swarmonomicon is under active development with the following components:

### Completed Features ✅
1. Centralized AI client
2. Thread-safe agent registry
3. Async-first architecture
4. WebSocket-based real-time communication
5. Modular agent system
6. Concurrent task processing
7. Resource management
8. Task processing system
9. GPT-4 batch processing

### In Progress 🔄
1. State machine improvements
2. Enhanced context preservation
3. Better error handling
4. Improved conversation history management
5. Agent-specific tool support
6. Browser agent enhancements
7. RL training infrastructure

## RELATED DOCUMENTS

- [Swarmonomicon Architecture](../../arcana/swarmonomicon_architecture.md)
- [Swarmonomicon Changelog](../../chronicles/swarmonomicon_changelog.md)
- [Agent Transfer Protocol](../../arcana/communication_patterns.md#agent-transfer-protocol)
- [Rust Patterns](../../incantations/rust_patterns.md)

---

*"In the pantheon of distributed systems, the Swarmonomicon stands as both creator and destroyer, orchestrating chaos with surprising elegance."* - Keeper of the Code 
