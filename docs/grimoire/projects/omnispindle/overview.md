# OMNISPINDLE: THE THREADS THAT WEAVE REALITY ITSELF
*"A distributed task management engine that shall bend tasks to our will!"*

`#omnispindle` `#todo` `#python` `#mongodb` `#mqtt`

## ESSENCE OF THE MECHANISM

The Omnispindle (formerly known as FastMCP Todo Server) is a distributed task management system that serves as the neural network connecting all projects within the mad laboratory. It receives, processes, and distributes tasks across our ecosystem, ensuring that no brilliant idea is forgotten and no critical task is overlooked.

![Omnispindle Conceptual Diagram](../../../assets/images/omnispindle_concept.png) *(TODO: Create this mechanical diagram)*

## CORE FUNCTIONALITIES

### 📋 TASK MANAGEMENT
- **Todo Creation and Tracking**: The lifeblood of our operations
  - Priority-based task organization
  - Project assignment and categorization
  - Status tracking through task lifecycle
  - Deadline management and notifications
- **Implementation**: Python with MongoDB persistence

### 🧠 AI-ENHANCED TASK PROCESSING
- **Task Enhancement**: Using the dark arts of AI to improve tasks
  - Automatic priority suggestions
  - Deadline recommendations
  - Task similarity detection
  - Intelligent task grouping
- **Status**: Fully operational with continual improvements

### 📡 MQTT INTEGRATION
- **Real-time Communication**: The psychic network connecting our systems
  - Topic-based message distribution
  - Event-driven architecture
  - Retained message support for late subscribers
  - QoS levels for critical messages
- **Status**: Complete with full publish/subscribe capabilities

### 🔌 FASTMCP FOUNDATION
- **Tool-Based Architecture**: The skeletal structure of our system
  - Function registration and discovery
  - Parameter validation
  - Result formatting
  - Error handling
- **Status**: Fully implemented with extensive API

### 🔄 CROSS-PROJECT SYNCHRONIZATION
- **Project Integration**: The connective tissue binding our mad creations
  - Standardized project field
  - Cross-referencing capabilities
  - Task assignment to specific agents
  - Metadata preservation
- **Status**: Recently implemented, continually evolving

## SYSTEM ARCHITECTURE

### 🏗️ CORE COMPONENTS

#### Todo Server
- Receives and processes todo requests
- Stores tasks in MongoDB
- Handles CRUD operations for todos
- Implements AI enhancement

#### API Interface
- REST endpoints for todo management
- Authentication and authorization
- Rate limiting
- Documentation

#### MQTT Client
- Publishes task updates
- Subscribes to command topics
- Handles message formatting
- Manages connection state

#### Database Layer
- MongoDB connection management
- Schema definition and validation
- Query optimization
- Indexing strategy

### 🔧 SUPPORTING TOOLS

The Omnispindle comes equipped with various tools:

- **Task Manipulation**: Create, read, update, delete
- **Search Capabilities**: Text search across todos
- **Filtering System**: By status, priority, project
- **Suggestion Engine**: AI-powered task insights
- **Timeline Planning**: Deadline and schedule suggestions
- **MQTT Publication**: Send messages to other systems
- **Lesson Management**: Store and retrieve learned insights

## GETTING STARTED

### Prerequisites
- Python 3.11 or later
- MongoDB 4.4 or later
- MQTT broker (Mosquitto recommended)
- Local LLM (optional, for AI enhancements)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/DanEdens/madness_interactive.git
cd madness_interactive/projects/python/Omnispindle
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the server:
```bash
python -m src.Omnispindle
```

### Configuration

The Omnispindle is configured through environment variables:

- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DB`: Database name
- `MONGODB_COLLECTION`: Collection name for todos
- `MQTT_BROKER`: MQTT broker address
- `MQTT_PORT`: MQTT broker port
- `MQTT_USERNAME`: MQTT authentication username (optional)
- `MQTT_PASSWORD`: MQTT authentication password (optional)
- `AI_ENDPOINT`: URL of AI service for enhancements (optional)

## API REFERENCE

### Todo Management

- `add_todo_tool`: Create a new todo
- `query_todos_tool`: Search for todos
- `update_todo_tool`: Modify an existing todo
- `delete_todo_tool`: Remove a todo
- `mark_todo_complete_tool`: Mark a todo as completed
- `list_todos_by_status_tool`: List todos with specific status
- `search_todos_tool`: Full-text search across todos

### Lesson Management

- `add_lesson_tool`: Record a new lesson learned
- `get_lesson_tool`: Retrieve a specific lesson
- `update_lesson_tool`: Modify an existing lesson
- `delete_lesson_tool`: Remove a lesson
- `list_lessons_tool`: Get all lessons
- `search_lessons_tool`: Full-text search across lessons

### AI-Powered Suggestions

- `get_todo_suggestions_tool`: Get AI-powered insights
- `get_specific_todo_suggestions_tool`: Analyze a specific todo
- `suggest_deadline_tool`: Recommend optimal deadline
- `suggest_time_slot_tool`: Recommend time for completing a task
- `generate_daily_schedule_tool`: Create an optimized daily plan

### MQTT Integration

- `mqtt_publish_tool`: Send a message to an MQTT topic
- `mqtt_get_tool`: Retrieve the last message from a topic

## CURRENT STATUS

The Omnispindle is under active development with the following components:

### Completed Features ✅
1. MongoDB integration
2. MQTT communication
3. Basic todo CRUD operations
4. REST API endpoints
5. Search functionality
6. Project field integration
7. AI-powered enhancement

### In Progress 🔄
1. Enhanced suggestion algorithms
2. Performance optimizations
3. Better error handling
4. Improved documentation
5. Advanced filtering capabilities
6. Timeline visualization

## RELATED DOCUMENTS

- [Omnispindle Architecture](../../arcana/omnispindle_architecture.md)
- [Omnispindle Changelog](../../chronicles/omnispindle_changelog.md)
- [MQTT Communication](../../arcana/communication_patterns.md#mqtt-communion)
- [Python Patterns](../../incantations/python_patterns.md)

---

*"The Omnispindle turns the chaos of ideas into the order of execution, without losing the chaotic spark that ignites innovation."* - Task Keeper 
