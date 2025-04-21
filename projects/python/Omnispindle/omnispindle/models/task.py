"""
Task Model

This module provides the Task class for the Omnispindle distributed task system.
The Task represents a unit of work to be executed by a worker.
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class TaskStatus:
    """Constants for task status."""
    PENDING = "pending"     # Task is waiting to be executed
    CLAIMED = "claimed"     # Task has been claimed by a worker but not started
    RUNNING = "running"     # Task is currently running
    COMPLETED = "completed" # Task has completed successfully
    FAILED = "failed"       # Task has failed
    CANCELLED = "cancelled" # Task has been cancelled
    TIMEOUT = "timeout"     # Task has timed out


class Task:
    """
    Task represents a unit of work to be executed by a worker.
    
    Attributes:
        id: Unique identifier for the task
        task_type: Type of task to execute
        parameters: Parameters for the task
        priority: Task priority (higher is more important)
        status: Current status of the task
        claimed_by: ID of the worker that claimed the task
        result: Result of the task execution
        error: Error message if the task failed
        created_at: When the task was created
        claimed_at: When the task was claimed
        started_at: When the task was started
        completed_at: When the task was completed
        dependencies: List of task IDs this task depends on
        timeout: Task timeout in seconds
        retry_count: Number of retry attempts
        metadata: Additional metadata for the task
    """
    
    def __init__(
        self,
        task_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        dependencies: Optional[List[str]] = None,
        timeout: int = 3600,  # 1 hour in seconds
        metadata: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ):
        """
        Initialize a new Task.
        
        Args:
            task_type: Type of task to execute
            parameters: Parameters for the task
            priority: Task priority (higher is more important)
            dependencies: List of task IDs this task depends on
            timeout: Task timeout in seconds
            metadata: Additional metadata for the task
            task_id: Optional custom task ID
        """
        self.id = task_id or str(uuid.uuid4())
        self.task_type = task_type
        self.parameters = parameters or {}
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.claimed_by = None
        self.result = None
        self.error = None
        self.created_at = datetime.utcnow()
        self.claimed_at = None
        self.started_at = None
        self.completed_at = None
        self.dependencies = dependencies or []
        self.timeout = timeout
        self.retry_count = 0
        self.metadata = metadata or {}
        
        logger.debug(f"Task {self.id} created")
    
    def claim(self, worker_id: str) -> None:
        """
        Claim the task for execution by a worker.
        
        Args:
            worker_id: ID of the worker claiming the task
        """
        self.status = TaskStatus.CLAIMED
        self.claimed_by = worker_id
        self.claimed_at = datetime.utcnow()
        
        logger.debug(f"Task {self.id} claimed by worker {worker_id}")
    
    def start(self) -> None:
        """Mark the task as started."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()
        
        logger.debug(f"Task {self.id} started")
    
    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark the task as completed.
        
        Args:
            result: Optional result data
        """
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()
        
        logger.debug(f"Task {self.id} completed")
    
    def fail(self, error: Optional[str] = None) -> None:
        """
        Mark the task as failed.
        
        Args:
            error: Optional error message
        """
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()
        
        logger.debug(f"Task {self.id} failed: {error}")
    
    def cancel(self) -> None:
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        
        logger.debug(f"Task {self.id} cancelled")
    
    def timeout_task(self) -> None:
        """Mark the task as timed out."""
        self.status = TaskStatus.TIMEOUT
        self.error = "Task timed out"
        self.completed_at = datetime.utcnow()
        
        logger.debug(f"Task {self.id} timed out")
    
    def retry(self) -> None:
        """
        Prepare the task for retry.
        
        Resets the task status and increments the retry count.
        """
        self.status = TaskStatus.PENDING
        self.claimed_by = None
        self.claimed_at = None
        self.started_at = None
        self.completed_at = None
        self.retry_count += 1
        
        logger.debug(f"Task {self.id} set for retry ({self.retry_count})")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary representation.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            "id": self.id,
            "task_type": self.task_type,
            "parameters": self.parameters,
            "priority": self.priority,
            "status": self.status,
            "claimed_by": self.claimed_by,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "claimed_at": self.claimed_at.isoformat() if self.claimed_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "dependencies": self.dependencies,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create a task from a dictionary representation.
        
        Args:
            data: Dictionary representation of a task
            
        Returns:
            Task object
        """
        # Create a basic task
        task = cls(
            task_type=data["task_type"],
            parameters=data.get("parameters", {}),
            priority=data.get("priority", 0),
            dependencies=data.get("dependencies", []),
            timeout=data.get("timeout", 3600),
            metadata=data.get("metadata", {}),
            task_id=data["id"],
        )
        
        # Set additional fields
        task.status = data.get("status", TaskStatus.PENDING)
        task.claimed_by = data.get("claimed_by")
        task.result = data.get("result")
        task.error = data.get("error")
        task.retry_count = data.get("retry_count", 0)
        
        # Parse timestamps
        def parse_timestamp(timestamp_str):
            return datetime.fromisoformat(timestamp_str) if timestamp_str else None
        
        task.created_at = parse_timestamp(data.get("created_at"))
        task.claimed_at = parse_timestamp(data.get("claimed_at"))
        task.started_at = parse_timestamp(data.get("started_at"))
        task.completed_at = parse_timestamp(data.get("completed_at"))
        
        return task
    
    def process_dependency_results(self, tasks: Dict[str, 'Task']) -> None:
        """
        Process the results of dependencies.
        
        This method processes the results of dependencies and replaces
        placeholder values in the parameters with actual results.
        
        Args:
            tasks: Dictionary of task IDs to Task objects
        """
        if not self.dependencies:
            return
        
        # Recursively search for placeholders in the parameters
        def replace_placeholders(obj, dep_results):
            if isinstance(obj, dict):
                for key, value in list(obj.items()):
                    if isinstance(value, (dict, list)):
                        replace_placeholders(value, dep_results)
                    elif isinstance(value, str) and value.startswith("$DEPENDS."):
                        # Parse the placeholder
                        # Format: $DEPENDS.task_id.result_path
                        # Or: $DEPENDS.result_path (for any dependency)
                        parts = value[9:].split(".")
                        if len(parts) >= 2:
                            # Specific dependency
                            dep_id = parts[0]
                            result_path = parts[1:]
                            
                            if dep_id in dep_results:
                                obj[key] = get_nested_result(dep_results[dep_id], result_path)
                        else:
                            # Any dependency, use the first one with a result
                            result_path = parts
                            for dep_result in dep_results.values():
                                if dep_result is not None:
                                    obj[key] = get_nested_result(dep_result, result_path)
                                    break
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (dict, list)):
                        replace_placeholders(item, dep_results)
                    elif isinstance(item, str) and item.startswith("$DEPENDS."):
                        # Similar logic as above
                        parts = item[9:].split(".")
                        if len(parts) >= 2:
                            dep_id = parts[0]
                            result_path = parts[1:]
                            
                            if dep_id in dep_results:
                                obj[i] = get_nested_result(dep_results[dep_id], result_path)
                        else:
                            result_path = parts
                            for dep_result in dep_results.values():
                                if dep_result is not None:
                                    obj[i] = get_nested_result(dep_result, result_path)
                                    break
        
        def get_nested_result(result, path):
            """Get a nested value from a result dictionary using a path."""
            current = result
            for part in path:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            return current
        
        # Collect the results of dependencies
        dep_results = {}
        for dep_id in self.dependencies:
            if dep_id in tasks and tasks[dep_id].status == TaskStatus.COMPLETED:
                dep_results[dep_id] = tasks[dep_id].result
        
        # Replace placeholders in parameters
        replace_placeholders(self.parameters, dep_results)
    
    def __str__(self) -> str:
        """String representation of the task."""
        return f"Task(id={self.id}, type={self.task_type}, status={self.status})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the task."""
        return (
            f"Task(id={self.id}, type={self.task_type}, status={self.status}, "
            f"priority={self.priority}, claimed_by={self.claimed_by})"
        ) 