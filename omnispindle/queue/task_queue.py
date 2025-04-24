"""
Task Queue

This module provides a task queue for the Omnispindle distributed task system.
It handles task scheduling, assignment, and worker management.
"""

import time
import asyncio
import heapq
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Callable, Awaitable, Union

from ..models.task import Task, TaskStatus
from ..models.worker import Worker, WorkerStatus


class TaskPriorityQueue:
    """Priority queue for tasks based on priority and scheduled time."""
    
    def __init__(self):
        self._queue: List[Tuple[int, datetime, str]] = []
        self._task_ids: Set[str] = set()
        
    def add_task(self, task: Task) -> None:
        """
        Add a task to the priority queue.
        
        Args:
            task: Task to add to the queue
        """
        if task.id in self._task_ids:
            return
        
        # Invert priority so that higher priority values are processed first
        # Use scheduled_at as secondary sort key
        scheduled_at = task.scheduled_at or datetime.utcnow()
        entry = (-task.priority, scheduled_at, task.id)
        heapq.heappush(self._queue, entry)
        self._task_ids.add(task.id)
    
    def remove_task(self, task_id: str) -> None:
        """
        Remove a task from the priority queue.
        
        Args:
            task_id: ID of the task to remove
        """
        if task_id in self._task_ids:
            # Mark the task as removed from the set
            self._task_ids.remove(task_id)
            # Note: The entry will be skipped when popping from the queue
            
    def get_next_task_id(self) -> Optional[str]:
        """
        Get the ID of the next task in the queue without removing it.
        
        Returns:
            The ID of the next task, or None if the queue is empty
        """
        # Clean out any tasks that have been removed
        while self._queue and self._queue[0][2] not in self._task_ids:
            heapq.heappop(self._queue)
            
        if not self._queue:
            return None
            
        # Return the task ID (third element of the tuple)
        return self._queue[0][2]
        
    def pop_next_task_id(self) -> Optional[str]:
        """
        Remove and return the ID of the next task in the queue.
        
        Returns:
            The ID of the next task, or None if the queue is empty
        """
        task_id = self.get_next_task_id()
        if task_id is not None:
            heapq.heappop(self._queue)
            self._task_ids.remove(task_id)
        return task_id
        
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if the queue has no tasks, False otherwise
        """
        return len(self._task_ids) == 0
        
    def __len__(self) -> int:
        """
        Get the number of tasks in the queue.
        
        Returns:
            Number of tasks in the queue
        """
        return len(self._task_ids)
        

class TaskQueue:
    """
    Task queue that manages tasks and workers in the distributed system.
    """
    
    def __init__(self):
        # Task storage
        self._tasks: Dict[str, Task] = {}
        self._ready_queue = TaskPriorityQueue()
        
        # Worker storage
        self._workers: Dict[str, Worker] = {}
        
        # Task type queues for quick lookup
        self._tasks_by_type: Dict[str, Set[str]] = {}
        
        # Task dependency tracking
        self._dependent_tasks: Dict[str, Set[str]] = {}  # task_id -> set of task_ids waiting on it
        
        # Callback handlers for various events
        self._on_task_claimed: Optional[Callable[[str, str], Awaitable[None]]] = None
        self._on_task_completed: Optional[Callable[[str, Any], Awaitable[None]]] = None
        self._on_task_failed: Optional[Callable[[str, str], Awaitable[None]]] = None
        
    # Task management methods
    
    def add_task(self, task: Task) -> None:
        """
        Add a task to the queue.
        
        Args:
            task: Task to add
        """
        self._tasks[task.id] = task
        
        # Add to task type index
        if task.type not in self._tasks_by_type:
            self._tasks_by_type[task.type] = set()
        self._tasks_by_type[task.type].add(task.id)
        
        # Handle dependencies
        if task.depends_on:
            task_ready = True
            for dep_id in task.depends_on:
                if dep_id not in self._tasks or self._tasks[dep_id].status != TaskStatus.COMPLETED:
                    task_ready = False
                    # Register this task as dependent on the dependency
                    if dep_id not in self._dependent_tasks:
                        self._dependent_tasks[dep_id] = set()
                    self._dependent_tasks[dep_id].add(task.id)
            
            if not task_ready:
                return  # Don't add to ready queue yet
        
        # If task is ready (no dependencies or all dependencies met)
        if task.status == TaskStatus.PENDING:
            self._ready_queue.add_task(task)
            
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            The task, or None if not found
        """
        return self._tasks.get(task_id)
        
    def remove_task(self, task_id: str) -> Optional[Task]:
        """
        Remove a task from the queue.
        
        Args:
            task_id: ID of the task to remove
            
        Returns:
            The removed task, or None if not found
        """
        if task_id not in self._tasks:
            return None
            
        task = self._tasks.pop(task_id)
        
        # Remove from ready queue if present
        self._ready_queue.remove_task(task_id)
        
        # Remove from task type index
        if task.type in self._tasks_by_type and task_id in self._tasks_by_type[task.type]:
            self._tasks_by_type[task.type].remove(task_id)
            
        # Remove dependencies
        if task_id in self._dependent_tasks:
            # Tasks depending on this one can no longer be satisfied
            for dependent_id in self._dependent_tasks[task_id]:
                if dependent_id in self._tasks:
                    dependent = self._tasks[dependent_id]
                    if dependent.status == TaskStatus.PENDING:
                        # Mark as failed due to dependency removal
                        dependent.fail("Dependency was removed")
            del self._dependent_tasks[task_id]
            
        return task
        
    async def update_task_status(
        self, 
        task_id: str, 
        status: str, 
        worker_id: Optional[str] = None,
        result: Optional[Any] = None,
        message: Optional[str] = None
    ) -> Optional[Task]:
        """
        Update the status of a task.
        
        Args:
            task_id: ID of the task to update
            status: New status of the task
            worker_id: ID of the worker that updated the task
            result: Optional result data for completed tasks
            message: Optional status message
            
        Returns:
            The updated task, or None if not found
        """
        if task_id not in self._tasks:
            return None
            
        task = self._tasks[task_id]
        
        if status == TaskStatus.CLAIMED:
            if worker_id and worker_id in self._workers:
                task.claim(worker_id)
                self._workers[worker_id].claim_task(task_id)
                if self._on_task_claimed:
                    await self._on_task_claimed(task_id, worker_id)
                    
        elif status == TaskStatus.RUNNING:
            if worker_id and worker_id in self._workers:
                task.start()
                
        elif status == TaskStatus.COMPLETED:
            task.complete(result)
            if worker_id and worker_id in self._workers:
                self._workers[worker_id].release_task(task_id, success=True)
                
            # Check if any tasks were waiting on this one
            await self._process_dependent_tasks(task_id)
            
            if self._on_task_completed:
                await self._on_task_completed(task_id, result)
                
        elif status == TaskStatus.FAILED:
            task.fail(message or "Task failed")
            if worker_id and worker_id in self._workers:
                self._workers[worker_id].release_task(task_id, success=False)
                
            if self._on_task_failed:
                await self._on_task_failed(task_id, message or "Task failed")
                
        elif status == TaskStatus.CANCELLED:
            task.cancel(message or "Task cancelled")
            if worker_id and worker_id in self._workers:
                self._workers[worker_id].release_task(task_id, success=False)
                
        return task
        
    async def _process_dependent_tasks(self, completed_task_id: str) -> None:
        """
        Process tasks that depend on a completed task.
        
        Args:
            completed_task_id: ID of the completed task
        """
        if completed_task_id not in self._dependent_tasks:
            return
            
        dependents = self._dependent_tasks.pop(completed_task_id)
        
        for task_id in dependents:
            if task_id not in self._tasks:
                continue
                
            task = self._tasks[task_id]
            
            # Check if all dependencies are now satisfied
            all_deps_satisfied = True
            for dep_id in task.depends_on:
                if dep_id not in self._tasks or self._tasks[dep_id].status != TaskStatus.COMPLETED:
                    all_deps_satisfied = False
                    break
                    
            if all_deps_satisfied and task.status == TaskStatus.PENDING:
                # Add to the ready queue
                self._ready_queue.add_task(task)
                
    # Worker management methods
    
    def register_worker(self, worker: Worker) -> None:
        """
        Register a worker with the queue.
        
        Args:
            worker: Worker to register
        """
        self._workers[worker.id] = worker
        worker.heartbeat(status=WorkerStatus.IDLE)
        
    def unregister_worker(self, worker_id: str) -> Optional[Worker]:
        """
        Unregister a worker from the queue.
        
        Args:
            worker_id: ID of the worker to unregister
            
        Returns:
            The unregistered worker, or None if not found
        """
        if worker_id not in self._workers:
            return None
            
        worker = self._workers.pop(worker_id)
        
        # Reassign tasks that were assigned to this worker
        for task_id in worker.current_tasks:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                if task.status in (TaskStatus.CLAIMED, TaskStatus.RUNNING):
                    # Reset to pending and add back to the queue
                    task.fail(f"Worker {worker_id} disconnected")
                    self._ready_queue.add_task(task)
                    
        return worker
        
    def update_worker_heartbeat(
        self, 
        worker_id: str, 
        status: Optional[str] = None,
        resources: Optional[Dict[str, Any]] = None
    ) -> Optional[Worker]:
        """
        Update a worker's heartbeat.
        
        Args:
            worker_id: ID of the worker to update
            status: Optional new status for the worker
            resources: Optional updated resource usage information
            
        Returns:
            The updated worker, or None if not found
        """
        if worker_id not in self._workers:
            return None
            
        worker = self._workers[worker_id]
        worker.heartbeat(status, resources)
        return worker
        
    # Task assignment methods
    
    def find_worker_for_task(self, task_id: str) -> Optional[str]:
        """
        Find a suitable worker for a task.
        
        Args:
            task_id: ID of the task to assign
            
        Returns:
            ID of a suitable worker, or None if no worker is available
        """
        if task_id not in self._tasks:
            return None
            
        task = self._tasks[task_id]
        
        # Find eligible workers
        eligible_workers = []
        for worker_id, worker in self._workers.items():
            if (worker.has_capacity() and 
                worker.capabilities.can_handle_task_type(task.type)):
                eligible_workers.append(worker_id)
                
        if not eligible_workers:
            return None
            
        # Simple selection: pick the worker with the fewest current tasks
        return min(
            eligible_workers,
            key=lambda wid: len(self._workers[wid].current_tasks)
        )
        
    async def assign_next_task(self) -> Optional[Tuple[str, str]]:
        """
        Assign the next available task to a suitable worker.
        
        Returns:
            Tuple of (task_id, worker_id) if a task was assigned, or None
            if no tasks could be assigned
        """
        if self._ready_queue.is_empty():
            return None
            
        task_id = self._ready_queue.get_next_task_id()
        if not task_id or task_id not in self._tasks:
            self._ready_queue.pop_next_task_id()  # Remove invalid task
            return None
            
        worker_id = self.find_worker_for_task(task_id)
        if not worker_id:
            return None  # No worker available
            
        # Assign the task
        task_id = self._ready_queue.pop_next_task_id()
        await self.update_task_status(task_id, TaskStatus.CLAIMED, worker_id)
        
        return task_id, worker_id
        
    # Utility methods
    
    def get_pending_tasks_count(self) -> int:
        """
        Get the number of pending tasks.
        
        Returns:
            Number of pending tasks
        """
        return len(self._ready_queue)
        
    def get_active_workers_count(self) -> int:
        """
        Get the number of active workers.
        
        Returns:
            Number of active workers
        """
        return sum(1 for worker in self._workers.values() if worker.is_alive())
        
    # Event handlers
    
    def set_task_claimed_handler(
        self, 
        handler: Callable[[str, str], Awaitable[None]]
    ) -> None:
        """
        Set a handler for task claimed events.
        
        Args:
            handler: Async function that takes (task_id, worker_id)
        """
        self._on_task_claimed = handler
        
    def set_task_completed_handler(
        self,
        handler: Callable[[str, Any], Awaitable[None]]
    ) -> None:
        """
        Set a handler for task completed events.
        
        Args:
            handler: Async function that takes (task_id, result)
        """
        self._on_task_completed = handler
        
    def set_task_failed_handler(
        self,
        handler: Callable[[str, str], Awaitable[None]]
    ) -> None:
        """
        Set a handler for task failed events.
        
        Args:
            handler: Async function that takes (task_id, error_message)
        """
        self._on_task_failed = handler
        
    # Stats and debugging
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the task queue.
        
        Returns:
            Dictionary of statistics
        """
        task_counts = {
            TaskStatus.PENDING: 0,
            TaskStatus.CLAIMED: 0, 
            TaskStatus.RUNNING: 0,
            TaskStatus.COMPLETED: 0,
            TaskStatus.FAILED: 0,
            TaskStatus.CANCELLED: 0,
            TaskStatus.TIMEOUT: 0
        }
        
        for task in self._tasks.values():
            if task.status in task_counts:
                task_counts[task.status] += 1
                
        worker_counts = {
            WorkerStatus.ONLINE: 0,
            WorkerStatus.OFFLINE: 0,
            WorkerStatus.BUSY: 0,
            WorkerStatus.IDLE: 0,
            WorkerStatus.PAUSED: 0,
            WorkerStatus.ERROR: 0
        }
        
        for worker in self._workers.values():
            if worker.status in worker_counts:
                worker_counts[worker.status] += 1
                
        return {
            "tasks": {
                "total": len(self._tasks),
                "pending_in_queue": len(self._ready_queue),
                "by_status": task_counts,
                "by_type": {
                    task_type: len(task_ids)
                    for task_type, task_ids in self._tasks_by_type.items()
                }
            },
            "workers": {
                "total": len(self._workers),
                "active": self.get_active_workers_count(),
                "by_status": worker_counts
            }
        } 