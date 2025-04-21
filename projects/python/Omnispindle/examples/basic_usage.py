#!/usr/bin/env python
"""
Omnispindle Basic Usage Example

This example demonstrates how to use the Omnispindle distributed task system
with a local queue, task submission, and worker execution.
"""

import time
import random
import logging
from typing import Dict, Any

from omnispindle.task_queue import TaskQueue
from omnispindle.client import TaskQueueClient, WorkerClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("omnispindle_example")


def math_task_executor(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Example executor for math tasks."""
    task_params = task_data.get("parameters", {})
    operation = task_params.get("operation")
    values = task_params.get("values", [])
    
    logger.info(f"Executing math task: {operation} on {values}")
    
    # Simulate work
    time.sleep(random.uniform(0.5, 2.0))
    
    # Perform operation
    if operation == "sum":
        result = sum(values)
    elif operation == "multiply":
        result = 1
        for val in values:
            result *= val
    elif operation == "average":
        result = sum(values) / len(values) if values else 0
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
    return {"result": result}


def text_task_executor(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Example executor for text processing tasks."""
    task_params = task_data.get("parameters", {})
    operation = task_params.get("operation")
    text = task_params.get("text", "")
    
    logger.info(f"Executing text task: {operation} on text of length {len(text)}")
    
    # Simulate work
    time.sleep(random.uniform(1.0, 3.0))
    
    # Perform operation
    if operation == "count_words":
        result = len(text.split())
    elif operation == "count_chars":
        result = len(text)
    elif operation == "uppercase":
        result = text.upper()
    elif operation == "lowercase":
        result = text.lower()
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
    return {"result": result}


def error_task_executor(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Example executor that simulates errors."""
    task_params = task_data.get("parameters", {})
    error_probability = task_params.get("error_probability", 0.5)
    
    logger.info(f"Executing error task with probability {error_probability}")
    
    # Simulate work
    time.sleep(random.uniform(0.5, 1.5))
    
    # Randomly fail
    if random.random() < error_probability:
        raise RuntimeError("Random task failure")
    
    return {"result": "Success!"}


def run_example():
    """Run the example."""
    # Create a task queue
    task_queue = TaskQueue(
        max_retries=2,
        worker_timeout=60,
    )
    
    # Create a client for the queue
    client = TaskQueueClient(local_queue=task_queue)
    
    # Create workers for different task types
    math_worker = WorkerClient(
        local_queue=task_queue,
        capabilities=["math"],
        capacity=2,
        metadata={"type": "math_processor"},
    )
    
    text_worker = WorkerClient(
        local_queue=task_queue,
        capabilities=["text"],
        capacity=1,
        metadata={"type": "text_processor"},
    )
    
    error_worker = WorkerClient(
        local_queue=task_queue,
        capabilities=["error"],
        capacity=1,
        metadata={"type": "error_simulator"},
    )
    
    # Register task executors
    math_worker.register_task_executor("math", math_task_executor)
    text_worker.register_task_executor("text", text_task_executor)
    error_worker.register_task_executor("error", error_task_executor)
    
    # Start workers in separate threads
    import threading
    
    math_thread = threading.Thread(target=math_worker.start)
    text_thread = threading.Thread(target=text_worker.start)
    error_thread = threading.Thread(target=error_worker.start)
    
    math_thread.daemon = True
    text_thread.daemon = True
    error_thread.daemon = True
    
    math_thread.start()
    text_thread.start()
    error_thread.start()
    
    try:
        # Submit some tasks
        logger.info("Submitting tasks...")
        
        # Math tasks
        sum_task_id = client.submit_task(
            task_type="math",
            parameters={"operation": "sum", "values": [1, 2, 3, 4, 5]},
            priority=5,
        )
        
        multiply_task_id = client.submit_task(
            task_type="math",
            parameters={"operation": "multiply", "values": [2, 3, 4]},
            priority=3,
        )
        
        # Text tasks
        word_count_task_id = client.submit_task(
            task_type="text",
            parameters={
                "operation": "count_words",
                "text": "The quick brown fox jumps over the lazy dog",
            },
            priority=4,
        )
        
        uppercase_task_id = client.submit_task(
            task_type="text",
            parameters={
                "operation": "uppercase",
                "text": "Hello, Omnispindle!",
            },
            priority=2,
        )
        
        # Error task
        error_task_id = client.submit_task(
            task_type="error",
            parameters={"error_probability": 0.7},
            priority=1,
        )
        
        # Wait for all tasks to complete
        logger.info("Waiting for tasks to complete...")
        
        sum_result = client.wait_for_task(sum_task_id)
        multiply_result = client.wait_for_task(multiply_task_id)
        word_count_result = client.wait_for_task(word_count_task_id)
        uppercase_result = client.wait_for_task(uppercase_task_id)
        
        # Error task might fail, so we handle it separately
        try:
            error_result = client.wait_for_task(error_task_id, timeout=10)
            logger.info(f"Error task completed with status: {error_result['status']}")
        except Exception as e:
            logger.warning(f"Error waiting for error task: {e}")
        
        # Print results
        logger.info(f"Sum task result: {sum_result.get('result', {}).get('result')}")
        logger.info(f"Multiply task result: {multiply_result.get('result', {}).get('result')}")
        logger.info(f"Word count task result: {word_count_result.get('result', {}).get('result')}")
        logger.info(f"Uppercase task result: {uppercase_result.get('result', {}).get('result')}")
        
        # Print queue statistics
        stats = client.get_queue_stats()
        logger.info(f"Queue statistics: {stats}")
        
        # Submit a batch of tasks
        logger.info("Submitting a batch of tasks...")
        
        batch_tasks = [
            {
                "task_type": "math",
                "parameters": {"operation": "average", "values": [10, 20, 30, 40, 50]},
                "priority": 5,
            },
            {
                "task_type": "text",
                "parameters": {
                    "operation": "lowercase",
                    "text": "OMNISPINDLE IS AWESOME",
                },
                "priority": 4,
            },
        ]
        
        batch_task_ids = client.submit_batch(batch_tasks)
        
        # Wait for the batch to complete
        batch_results = client.wait_for_batch(batch_task_ids)
        
        # Print batch results
        for i, result in enumerate(batch_results):
            logger.info(f"Batch task {i+1} result: {result.get('result', {}).get('result')}")
        
        # Let's demonstrate task dependencies
        logger.info("Demonstrating task dependencies...")
        
        # First task: calculate the sum
        step1_task_id = client.submit_task(
            task_type="math",
            parameters={"operation": "sum", "values": [5, 10, 15]},
            priority=10,
        )
        
        # Second task: multiply the result by 2
        # This task depends on the first task and will use its result
        step2_task_id = client.submit_task(
            task_type="math",
            parameters={
                "operation": "multiply",
                "values": [2, "$DEPENDS.result.result"],  # Placeholder for dependency result
            },
            dependencies=[step1_task_id],
            priority=10,
        )
        
        # Wait for both tasks to complete
        step1_result = client.wait_for_task(step1_task_id)
        step2_result = client.wait_for_task(step2_task_id)
        
        # Get the results
        step1_value = step1_result.get('result', {}).get('result')
        step2_value = step2_result.get('result', {}).get('result')
        
        logger.info(f"Step 1 (sum) result: {step1_value}")
        logger.info(f"Step 2 (multiply by 2) result: {step2_value}")
        
        # Print final queue statistics
        final_stats = client.get_queue_stats()
        logger.info(f"Final queue statistics: {final_stats}")
        
    except KeyboardInterrupt:
        logger.info("Interrupted, shutting down...")
    finally:
        # Stop workers
        math_worker.stop()
        text_worker.stop()
        error_worker.stop()
        
        # Shutdown the task queue
        task_queue.shutdown()


if __name__ == "__main__":
    run_example() 