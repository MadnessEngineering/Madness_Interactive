# Omnispindle

**A lightweight, flexible distributed task execution system for Python.**

![Omnispindle Logo](https://via.placeholder.com/150x150?text=Omnispindle)

## Features

✨ **Distributed Task Execution** - Run tasks across multiple workers
🔄 **Dynamic Worker Registration** - Workers can join and leave the system at any time
⚖️ **Intelligent Task Scheduling** - Prioritize tasks and match them to capable workers
🔗 **Task Dependencies** - Create complex workflows with dependencies
⏱️ **Automatic Retries** - Failed tasks are automatically retried
🔍 **Worker Health Monitoring** - Detect and handle worker failures
🧩 **Flexible Worker Capabilities** - Match tasks to workers based on capabilities
📊 **Comprehensive Metrics** - Track system performance and task execution

## Installation

```bash
pip install omnispindle
```

## Quick Start

Here's a simple example to get you started:

```python
from omnispindle.task_queue import TaskQueue
from omnispindle.client import TaskQueueClient, WorkerClient

# Create a task queue
task_queue = TaskQueue()

# Create a client
client = TaskQueueClient(local_queue=task_queue)

# Register a worker
worker = WorkerClient(
    local_queue=task_queue,
    capabilities=["math"],
)

# Define a task executor
def math_executor(task_data):
    operation = task_data["parameters"]["operation"]
    values = task_data["parameters"]["values"]
    
    if operation == "sum":
        result = sum(values)
    elif operation == "multiply":
        result = 1
        for val in values:
            result *= val
    
    return {"result": result}

# Register the executor
worker.register_task_executor("math", math_executor)

# Start the worker (in a separate thread in a real application)
import threading
worker_thread = threading.Thread(target=worker.start)
worker_thread.daemon = True
worker_thread.start()

# Submit a task
task_id = client.submit_task(
    task_type="math",
    parameters={
        "operation": "sum",
        "values": [1, 2, 3, 4, 5]
    }
)

# Wait for the result
result = client.wait_for_task(task_id)
print(f"Result: {result['result']['result']}")  # Output: Result: 15

# Shutdown
worker.stop()
task_queue.shutdown()
```

## Architecture

Omnispindle consists of several key components:

1. **TaskQueue** - The central component that manages task scheduling and worker coordination
2. **Task** - Represents a unit of work to be executed
3. **Worker** - Represents a node that can execute tasks
4. **TaskQueueClient** - Client interface for submitting and managing tasks
5. **WorkerClient** - Client interface for worker nodes

The system is designed to be flexible and scalable, with support for both local (in-process) and remote (distributed) execution.

## Task Lifecycle

1. **Submission** - Tasks are submitted to the queue with a type, parameters, and optional priority and dependencies
2. **Scheduling** - The queue schedules tasks based on priority and worker availability
3. **Claiming** - Workers claim tasks they can execute
4. **Execution** - Workers execute tasks and report results
5. **Completion** - The queue records the task result and schedules dependent tasks

## Worker Capabilities

Workers register with the system declaring their capabilities - the types of tasks they can execute. The task queue matches tasks to workers with the appropriate capabilities, ensuring that tasks are only assigned to workers that can handle them.

## Error Handling

Omnispindle provides robust error handling:

- Automatic retries for failed tasks
- Dead worker detection
- Task timeout monitoring
- Exception propagation

## Advanced Features

### Task Dependencies

Tasks can depend on other tasks, creating complex workflows:

```python
# First task: calculate the sum
step1_id = client.submit_task(
    task_type="math",
    parameters={"operation": "sum", "values": [1, 2, 3]}
)

# Second task: multiply the result
step2_id = client.submit_task(
    task_type="math",
    parameters={"operation": "multiply", "values": [10]},
    dependencies=[step1_id]
)
```

### Batch Processing

Submit multiple tasks as a batch:

```python
batch_tasks = [
    {
        "task_type": "math",
        "parameters": {"operation": "sum", "values": [1, 2, 3]}
    },
    {
        "task_type": "math",
        "parameters": {"operation": "multiply", "values": [4, 5, 6]}
    }
]

batch_ids = client.submit_batch(batch_tasks)
batch_results = client.wait_for_batch(batch_ids)
```

### State Persistence

TaskQueue can persist its state to disk for recovery:

```python
task_queue = TaskQueue(persistence_path="/path/to/state.json")

# Later, recover state
task_queue.load_state()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## TODOs

- [ ] Implement Redis-based distributed queue
- [ ] Add support for task cancellation propagation
- [ ] Develop a web dashboard for monitoring
- [ ] Add support for streaming results
- [ ] Implement worker auto-scaling
- [ ] Add task prioritization strategies
- [ ] Develop load balancing improvements

## LESSONS LEARNED

1. Ensure thread safety with proper locking mechanisms when dealing with shared state.
2. Design for both local and distributed operation from the beginning.
3. Implement robust error handling for various failure scenarios in distributed systems.
4. Consider the overhead of task serialization and parameter size in distributed environments.
5. Monitoring worker health is critical for reliable distributed task execution. 