# cli command to add a todo item for a new feature called Mad Tinker Mode

``` mcp call add_todo --params '{"description": "Implement the _mad_tinker_mode function to enable additional tooling and options for invention, as described in the mad_tinker_mode docstring.", "project": "omnispindle", "priority": "low", "metadata": {"notes": "starting on line 167: From user prompt: async def mad_tinker_mode(ctx: Context = None) -> str:\n    \"\"\"Receive a prompt to instill the mad mind of an unhinged Tinker in our workflow.\n    This will enable additional tooling and options for invention! Embrace the madness!\"\"\"\n    return await _mad_tinker_mode(ctx) # TODO: Implement this", "file": "tools.py", "function": "_mad_tinker_mode"}}' todo ```

```{"success": true, "agent_context": {"type": "todo", "entity": "todo:5628e23d-15ac-4e5e-96c9-9ce71d40b0e5"}, "data": {"todo_id": "5628e23d-15ac-4e5e-96c9-9ce71d40b0e5", "description": "Implement the _mad_tinker_mode function to enable additional", "project": "omnispindle"}, "message": "Todo created successfully"}```

## cli command for handshake with server and tool documentation

``` mcp tools todo ```

```add_todo(description:str, project:str, [metadata:obj], [priority:str], [target_agent:str])
     Creates a task in the specified project with the given priority and target agent. Returns a compact representation of the created todo with an ID for reference.

query_todos([ctx:str], [filter:obj], [limit:int], [projection:obj])
     Query todos with flexible filtering options. Searches the todo database using MongoDB-style query filters and projections.

update_todo(todo_id:str, updates:obj)
     Update a todo with the provided changes. Common fields to update: description, priority, status, metadata.

delete_todo(todo_id:str)
     Delete a todo by its ID.

get_todo(todo_id:str)
     Get a specific todo by ID.

mark_todo_complete(todo_id:str, [comment:str])
     Mark a todo as completed. Calculates the duration from creation to completion.

list_todos_by_status(status:str, [limit:int])
     List todos filtered by status ('initial', 'pending', 'completed'). Results are formatted for efficiency with truncated descriptions.

add_lesson(language:str, lesson_learned:str, topic:str, [tags:arr])
     Add a new lesson learned to the knowledge base.

get_lesson(lesson_id:str)
     Get a specific lesson by ID.

update_lesson(lesson_id:str, updates:obj)
     Update an existing lesson by ID.

delete_lesson(lesson_id:str)
     Delete a lesson by ID.

search_todos(query:str, [ctx:str], [fields:arr], [limit:int])
     Search todos with text search capabilities across specified fields. Special format: "project:ProjectName" to search by project.

grep_lessons(pattern:str, [limit:int])
     Search lessons with grep-style pattern matching across topic and content.

list_project_todos(project:str, [limit:int])
     List recent active todos for a specific project.

query_todo_logs([filter_type:str], [page:int], [page_size:int], [project:str])
     Query todo logs with filtering options.

list_projects([include_details:], [madness_root:str])
     List all valid projects from the centralized project management system. `include_details`: False (names only), True (full metadata), "filemanager" (for UI).

explain(topic:str)
     Provides a detailed explanation for a project or concept. For projects, it dynamically generates a summary with recent activity.

add_explanation(content:str, topic:str, [author:str], [kind:str])
     Add a new static explanation to the knowledge base.

list_lessons([limit:int])
     List all lessons, sorted by creation date.

search_lessons(query:str, [fields:arr], [limit:int])
     Search lessons with text search capabilities.
```
