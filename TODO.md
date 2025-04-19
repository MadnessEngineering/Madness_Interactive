# TODO List

## High Priority

### Fix Agent Registration System
1. [x] Update `AgentRegistry` implementation
   - [x] Review internal storage type (`Arc<Box<dyn Agent + Send + Sync>>`)
   - [x] Consider if we need both `Arc` and `Box`
   - [x] Document the wrapping pattern decisions

2. [x] Fix `TransferService` implementation
   - [x] Review how it interacts with `AgentRegistry`
   - [x] Consider if we need `Arc<RwLock<AgentRegistry>>` or if `Arc<AgentRegistry>` is sufficient
   - [x] Update methods to handle concurrent access correctly

3. [x] Update agent registration in `swarm.rs`
   - [x] Remove direct `Arc<RwLock>` wrapping of agents
   - [x] Let `AgentRegistry::register` handle the wrapping
   - [x] Update the test cases to match this pattern

4. [x] Fix type mismatches
   - [x] Update `get_agent` to return correct type
   - [x] Fix `registry.read()` vs `registry.write()` usage
   - [x] Ensure consistent agent access patterns

### AI Integration
1. [x] Implement centralized AI client
   - [x] Add configurable endpoint support
   - [x] Add model selection support
   - [x] Implement conversation history
   - [x] Add system prompt handling

2. [x] Update agents to use AI client
   - [x] Update GreeterAgent
   - [x] Update GitAssistantAgent
   - [x] Add conversation history support
   - [x] Implement proper error handling

3. [x] Enhance AI communication
   - [x] Add retry mechanism for failed requests
   - [x] Implement request timeout handling
   - [x] Add rate limiting
   - [x] Improve error messages
   - [x] Implement GPT-4 batch processing with pooling

### Current Issues to Fix
1. [ ] Fix lifetime issue in `AgentWrapper::get_mut`
   ```rust
   // Current issue:
   pub fn get_mut(&mut self) -> Option<&mut (dyn Agent + Send + Sync + '_)>
   ```

2. [ ] Fix trait method access in `routes.rs`
   - [ ] Import `Agent` trait where needed
   - [ ] Ensure proper trait bounds on generic parameters

3. [ ] Review locking patterns in `TransferService`
   - [x] Consider if we need write locks for read-only operations
   - [ ] Add timeouts to prevent deadlocks
   - [ ] Handle lock poisoning cases

### Error Handling
1. [x] Refactor error handling to use custom Error type
   - [x] Define custom Error enum in src/error.rs
   - [x] Implement From trait for conversions
   - [x] Replace usage of std::error::Error with custom Error
   - [x] Update function signatures and return types

2. [x] Resolve compilation errors related to dyn Error
   - [x] Refactor main() to return Result<(), Box<dyn std::error::Error>>
   - [x] Introduce run() function returning Result<(), Error>
   - [x] Map custom Error to Box<dyn std::error::Error> in main()

3. [x] Update tests to use custom Error type
   - [x] Fix test_haiku_git_integration return type
   - [x] Update other test functions as needed

### Test Coverage
1. [ ] Fix failing integration tests
   - [ ] Review `test_haiku_git_integration`
   - [ ] Ensure proper cleanup in tests
   - [ ] Add more granular test cases

2. [ ] Add unit tests
   - [x] Test agent registration
   - [x] Test message routing
   - [ ] Test state transitions
   - [x] Test AI client functionality

### Fix Failing Tests
1. [ ] Fix `test_invalid_transfer` in `agents::greeter`
   - [ ] Review the expected behavior for invalid transfers
   - [ ] Update the test to match the current implementation
   - [ ] Consider if the failure is due to a bug or outdated test

2. [ ] Fix `test_haiku_generation` in `agents::haiku`
   - [ ] Investigate the overflow error
   - [ ] Review the haiku generation logic for potential bugs
   - [ ] Update the test to handle edge cases

3. [ ] Fix `test_state_transitions` in `agents::haiku`
   - [ ] Review the assertion failure
   - [ ] Ensure the state is properly initialized
   - [ ] Update the test to match the expected state transitions

4. [ ] Fix `test_agent_workflow` in `agents`
   - [ ] Investigate the overflow error
   - [ ] Review the agent workflow logic for potential bugs
   - [ ] Update the test to handle edge cases

5. [ ] Fix `test_agent_transfer` in `agents::transfer`
   - [ ] Review the assertion failure
   - [ ] Ensure the transfer logic is properly implemented
   - [ ] Update the test to match the expected behavior

## Medium Priority

### Documentation
1. [x] Add inline documentation for public APIs
2. [x] Create usage examples
3. [x] Document concurrency patterns
4. [x] Document AI integration
5. [x] Update Architecture.md with current state of the project
6. [ ] Improve API documentation

### Features
1. [ ] Implement proper error handling for agent transfers
2. [ ] Add timeout mechanism for long-running operations
3. [ ] Implement agent state persistence
4. [ ] Add configuration file support
5. [ ] Improve Browser Agent functionality
6. [ ] Enhance RL Agent's training infrastructure

### Tool System Enhancements
1. [x] Implement YOLO object detection tool
2. [x] Implement screenshot detection tool
3. [x] Add Goose performance testing tool
4. [x] Enhance GPT-4 batch processing tool
5. [ ] Improve error handling in tool execution
6. [ ] Add more sophisticated tool chaining capabilities

### Implement Missing Features
1. [ ] Identify any unimplemented features
   - [ ] Review the project requirements
   - [ ] Create a list of missing features
   - [ ] Prioritize the implementation based on dependencies

2. [ ] Implement the missing features
   - [ ] Follow the existing code patterns
   - [ ] Write unit tests for the new features
   - [ ] Ensure proper error handling and edge case coverage

## Low Priority

### Improvements
1. [ ] Add metrics collection
2. [ ] Implement more comprehensive logging system
3. [ ] Add health checks for agents
4. [ ] Create admin interface
5. [ ] Implement MQTT logging for log agent

### Technical Debt
1. [ ] Reduce code duplication in agent implementations
2. [ ] Optimize lock patterns
3. [ ] Implement proper shutdown sequence
4. [ ] Add proper error types instead of using Box<dyn Error>

### Refactor and Optimize
1. [ ] Review the codebase for potential refactoring
   - [ ] Identify any code duplication
   - [ ] Look for opportunities to improve performance
   - [ ] Consider improving the code organization and modularity

2. [ ] Perform the identified refactorings
   - [ ] Create separate branches for each refactoring
   - [ ] Ensure the tests pass after each refactoring
   - [ ] Update the documentation if necessary

### Enhance Test Coverage
1. [ ] Review the existing test coverage
   - [ ] Identify any missing test cases
   - [ ] Consider adding more edge case scenarios
   - [ ] Look for opportunities to improve test organization

2. [ ] Implement the identified test enhancements
   - [ ] Write new test cases
   - [ ] Refactor existing tests if necessary
   - [ ] Ensure all tests pass consistently

## Completed
- [x] Create initial agent system
- [x] Implement basic message routing
- [x] Add git operations support
- [x] Add haiku generation
- [x] Implement project initialization
- [x] Create `AgentWrapper` to handle type complexity
- [x] Update `AgentRegistry` to use wrapper type
- [x] Update agent registration to use new pattern
- [x] Implement centralized AI client
- [x] Add conversation history support
- [x] Update agents to use AI client
- [x] Fix concurrent access patterns
- [x] Refactor error handling to use custom Error type
- [x] Resolve compilation errors related to dyn Error
- [x] Update tests to use custom Error type
- [x] Enhanced todo system with TodoTool integration and AI-powered todo enhancement
- [x] Fixed GitAssistantAgent initialization in swarm.rs
- [x] Implement basic Browser Agent functionality
- [x] Implement initial RL Agent with Flappy Bird environment
- [x] Add YOLO object detection and screenshot detection tools
- [x] Implement GPT-4 batch processing with request pooling
- [x] Implement model serialization/deserialization for RL agents
- [x] Add checkpoint system for interrupted training
- [x] Implement model versioning support for Q-learning models

## Next Steps
1. Prioritize fixing the failing tests to ensure the existing functionality is working as expected.
2. Complete the Browser Agent and RL Agent implementations with better error handling and state management.
3. Implement the MQTT logging system for the log agent.
4. Enhance the AI communication layer with better prompt management and model fallback strategies.
5. Improve documentation and test coverage.

## Todo Worker and Multi-Agent Integration
1. [ ] Integrate task injection for the todo worker:
   - [ ] Update src/bin/todo_worker.rs to actively fetch and process tasks from the shared TodoList.
   - [ ] Connect MQTT callbacks to add new tasks into the TodoList.
   - [ ] Ensure that agents (e.g., GreeterAgent) can submit tasks to the TodoList.
   - [ ] Implement proper error handling for task processing (e.g., timeouts, retries, logging failures).
   - [ ] Write unit and integration tests to simulate multi-source task injection and processing.

## Known Issues
- Several test failures in git assistant, haiku generation, and agent transfer components need investigation
- Todo list API endpoints tests failing
- Goose tool tests failing

# Reinforcement Learning Implementation Plan

## Phase 1: Core Infrastructure
- [x] Implement basic RL traits (State, Action, Environment)
- [x] Implement Q-Learning agent
- [x] Create basic Flappy Bird environment
- [x] Add visualization capabilities using a simple graphics library
  - [x] Research and choose between: ggez, pixels, minifb
  - [x] Implement basic rendering of bird and pipes
  - [x] Add frame-by-frame visualization option
  - [x] Add training progress visualization

## Phase 2: Training Infrastructure
- [x] Implement model serialization/deserialization
  - [x] Add serde support for Q-tables
  - [x] Add save/load functionality for Q-tables
  - [x] Create checkpoint system for interrupted training
  - [x] Add model versioning support
- [ ] Implement experience replay
  - [ ] Create a replay buffer data structure
  - [ ] Add sampling functionality
  - [ ] Integrate with Q-learning update
- [ ] Improve exploration strategies
  - [ ] Implement epsilon-greedy with decay
  - [ ] Add Boltzmann exploration
  - [ ] Add Upper Confidence Bound exploration

## Phase 3: Advanced Algorithms
- [ ] Implement Deep Q-Network (DQN)
  - [ ] Add neural network model support
  - [ ] Implement target network
  - [ ] Add batch training
- [ ] Implement Double DQN
- [ ] Implement Dueling DQN

## Phase 4: Multi-Agent Support
- [ ] Implement multi-agent environment
- [ ] Add agent communication
- [ ] Implement competitive and cooperative scenarios 
