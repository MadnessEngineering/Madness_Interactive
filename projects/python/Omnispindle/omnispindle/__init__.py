"""
Omnispindle - A lightweight, flexible distributed task execution system for Python.

Omnispindle provides a distributed task queue system with worker management,
task scheduling, and dependency resolution.
"""

__version__ = "0.1.0"

from .task_queue import TaskQueue, TaskQueueError, WorkerNotFoundError, TaskNotFoundError
from .client import TaskQueueClient, WorkerClient, OmnispindleClientError
from .models.task import Task, TaskStatus
from .models.worker import Worker, WorkerStatus

__all__ = [
    "TaskQueue",
    "TaskQueueError",
    "WorkerNotFoundError", 
    "TaskNotFoundError",
    "TaskQueueClient",
    "WorkerClient",
    "OmnispindleClientError",
    "Task",
    "TaskStatus",
    "Worker",
    "WorkerStatus",
] 