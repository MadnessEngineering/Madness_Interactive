### Lessons Learned (Updated)

#### Testing Best Practices
- Use `DEBUG=TRUE cargo test -- --nocapture | cat` for detailed debug output
- Avoid spawning threads in tests unless absolutely necessary
- Use proper locking mechanisms for shared state in tests
- Keep tests focused on single functionality
- Ensure proper cleanup after each test
- Use descriptive test names that indicate what's being tested
- Group related tests together for better organization
- Test error cases explicitly
- Avoid testing UI components directly in unit tests
- Use headless mode for testing when possible
- Ensure tests are deterministic and don't depend on timing

#### Component Architecture
- Split large managers into focused, independently borrowable components
- Use message passing between components to avoid mutex contention
- Implement RwLock for better concurrent read access
- Design components around single responsibility principle
- Use channels for inter-component communication
- Maintain clear ownership boundaries between components

#### Thread Safety
- Replace Arc<Mutex<T>> with Arc<RwLock<T>> where possible for better concurrency
- Design components to be independently borrowable
- Use message passing instead of shared state where possible
- Implement proper Drop traits for cleanup
- Use dedicated channels per component to prevent blocking
- Avoid spawning threads in tests to prevent race conditions
- Release locks before performing operations that might need them
- Use proper synchronization primitives in test code


## Lessons Learned

### AI Pair Programming
- Using git history in conversations helps AI understand and restore previously working code
- Maintaining a "Lessons Learned" file helps keep important details in focus during iterations
- When dealing with complex UI elements, instruct AI to comment out code instead of deleting
- Clean commits with clear messages improve AI's ability to reference past solutions. 1 line commits are best for git log --oneline, but detail is more important.
- Complex UI features require comprehensive test coverage to prevent unintended removal
- Git squashing can improve the usefulness of commit history in AI conversations

### WebView Management
- WebView instances should be owned by their respective tabs
- Strong references to parent windows must be maintained
- Proper display parameters are crucial for preventing frame issues
- IPC handlers need careful error handling and type checking
- Event handling should be bi-directional (UI ↔ Backend)
- UI state should be explicitly synced after backend operations
- Error handling should include user feedback
- WebView creation should be atomic (succeed completely or fail safely)
- Environment variables should be used for configurable defaults
- Tab bar construction should use proper encapsulation and initialization
- Window chrome integration requires careful coordination with native controls
- WebViews need explicit z-index management to prevent overlap issues
- Tab switching must properly handle WebView visibility and focus
- Content WebViews should be positioned relative to tab bar height
- Each tab's WebView should maintain its own state independently
- WebView cleanup must be explicit to prevent memory leaks
- Tab creation and closing operations need proper state synchronization
- Window resize events must update all WebView bounds correctly
- Tab bar visibility must be maintained during tab operations
- WebView bounds must be updated after tab operations to maintain layout
- Use !important CSS rules for critical UI elements that must stay visible
- Window and WebView visibility should be set explicitly during initialization
- Focus management is crucial for proper window interaction
- Loading states should provide clear visual feedback
- UI components should maintain visibility after bounds updates

### UI Design Best Practices
- Use CSS variables for consistent theming across components
- Implement loading indicators for better user feedback
- Add tooltips to improve button discoverability
- Provide visual feedback for all user interactions
- Handle both URL and search inputs intelligently
- Use transitions for smooth visual changes
- Maintain proper z-indexing for overlapping elements
- Implement proper error states and loading feedback
- Use modern design patterns for better user experience
- Keep UI responsive during background operations

### Event System Design
- Events should have clear success/failure feedback
- UI state must be kept in sync with backend state
- Error handling should be comprehensive and user-friendly
- Event handlers should be properly scoped and cleaned up
- Event propagation should be predictable and traceable
- Window visibility events require special attention
- Focus events should be handled appropriately
- Loading state changes should be propagated to UI

### Testing Best Practices
- Use DEBUG=TRUE cargo test -- --nocapture | cat for detailed debug output
- Test window creation and visibility explicitly
- Verify WebView initialization and visibility
- Check UI component interactions and state changes
- Test focus management and window interactions
- Validate loading states and animations
- Ensure proper cleanup after tests

### Code Organization
- Avoid circular dependencies by keeping related types in the same module
- Place commands and events together when they share common data structures
- Use public helper methods to encapsulate common state checks
- Keep template files in a dedicated directory with clear naming
- Maintain clear separation between UI and business logic

### Error Handling
- Convert WebView errors to String for consistent error handling
- Use map_err for error type conversion instead of custom match blocks
- Release locks before performing operations that might need them
- Handle all potential error cases in tab management
- Provide clear error messages for debugging
- Check lock acquisition success before using Mutex guards
