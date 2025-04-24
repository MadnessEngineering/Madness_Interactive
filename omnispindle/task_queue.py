"""
Task Queue

This module provides the TaskQueue class for the Omnispindle distributed task system.
The TaskQueue manages tasks and workers, handling task scheduling, distribution, and execution.
"""

import uuid
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable, Tuple, Union

from .models.task import Task, TaskStatus
from .models.worker import Worker, WorkerStatus

# Configure logging
logger = logging.getLogger(__name__)


class TaskQueueError(Exception):
    """Base exception for TaskQueue errors."""
    pass


class WorkerNotFoundError(TaskQueueError):
    """Raised when a worker is not found."""
    pass


class TaskNotFoundError(TaskQueueError):
    """Raised when a task is not found."""
    pass


class NoAvailableWorkersError(TaskQueueError):
    """Raised when no workers are available to process a task."""
    pass


class TaskQueue:
    """
    TaskQueue manages the distribution and execution of tasks across workers.
    
    Features:
    - Task submission and scheduling
    - Worker registration and management
    - Task-to-worker matching based on capabilities
    - Priority-based task scheduling
    - Task dependency resolution
    - Automatic retry for failed tasks
    - Dead worker detection
    - Task timeout monitoring
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        default_timeout: int = 3600,  # 1 hour in seconds
        worker_timeout: int = 90,     # 1.5 minutes in seconds
        persistence_path: Optional[str] = None,
        persistence_interval: int = 60,  # 1 minute in seconds
    ):
        """
        Initialize the TaskQueue.
        
        Args:
            max_retries: Maximum number of retry attempts for failed tasks
            default_timeout: Default task timeout in seconds
            worker_timeout: Timeout for workers to be considered dead in seconds
            persistence_path: Optional path to persist queue state
            persistence_interval: How often to persist state in seconds
        """
        # Configuration
        self.max_retries = max_retries
        self.default_timeout = default_timeout
        self.worker_timeout = worker_timeout
        self.persistence_path = persistence_path
        self.persistence_interval = persistence_interval
        
        # Task storage
        self.tasks: Dict[str, Task] = {}
        self.pending_tasks: Dict[int, Set[str]] = {}  # Priority -> Task IDs
        self.running_tasks: Set[str] = set()
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        
        # Worker storage
        self.workers: Dict[str, Worker] = {}
        self.worker_by_capability: Dict[str, Set[str]] = {}  # Capability -> Worker IDs
        
        # Task callback registry
        self.task_callbacks: Dict[str, List[Callable[[Task], None]]] = {}
        
        # Locks for thread safety
        self.task_lock = threading.RLock()
        self.worker_lock = threading.RLock()
        
        # Monitoring threads
        self.monitor_running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.persistence_thread: Optional[threading.Thread] = None
        
        # Performance metrics
        self.metrics = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_retried": 0,
            "workers_registered": 0,
            "workers_lost": 0,
            "avg_task_duration": 0.0,
            "avg_queue_time": 0.0,
        }
        
        # Start monitoring
        self._start_monitoring()
    
    def submit_task(
        self,
        task_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        timeout: Optional[int] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ) -> str:
        """
        Submit a task to the queue.
        
        Args:
            task_type: Type of task to execute
            parameters: Parameters for the task
            priority: Task priority (higher is more important)
            timeout: Task timeout in seconds
            dependencies: List of task IDs this task depends on
            metadata: Additional metadata for the task
            task_id: Optional custom task ID
            
        Returns:
            Task ID
        """
        with self.task_lock:
            # Create task
            task = Task(
                task_id=task_id,
                task_type=task_type,
                parameters=parameters,
                priority=priority,
                timeout=timeout or self.default_timeout,
                dependencies=dependencies,
                metadata=metadata,
            )
            
            # Store task
            self.tasks[task.id] = task
            
            # Add to pending queue if no dependencies or all dependencies completed
            if self._can_start_task(task):
                self._add_to_pending_queue(task)
            
            # Update metrics
            self.metrics["tasks_submitted"] += 1
            
            logger.info(f"Task submitted: {task.id} (type: {task_type}, priority: {priority})")
            
            # Try to schedule tasks immediately
            self._schedule_tasks()
            
            return task.id
    
    def register_worker(
        self,
        capabilities: Optional[List[str]] = None,
        capacity: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        worker_id: Optional[str] = None,
        heartbeat_interval: int = 30,
    ) -> str:
        """
        Register a worker with the queue.
        
        Args:
            capabilities: List of task types this worker can execute
            capacity: Number of concurrent tasks this worker can execute
            metadata: Additional metadata for the worker
            worker_id: Optional custom worker ID
            heartbeat_interval: Heartbeat interval in seconds
            
        Returns:
            Worker ID
        """
        with self.worker_lock:
            # Create worker
            worker = Worker(
                worker_id=worker_id,
                capabilities=capabilities,
                capacity=capacity,
                metadata=metadata,
                heartbeat_interval=heartbeat_interval,
            )
            
            # Store worker
            self.workers[worker.id] = worker
            
            # Index worker by capabilities
            for capability in worker.capabilities:
                if capability not in self.worker_by_capability:
                    self.worker_by_capability[capability] = set()
                self.worker_by_capability[capability].add(worker.id)
            
            # Update metrics
            self.metrics["workers_registered"] += 1
            
            logger.info(f"Worker registered: {worker.id} (capabilities: {worker.capabilities})")
            
            # Set worker as online
            worker.set_status(WorkerStatus.ONLINE, "Worker registered")
            
            # Try to schedule tasks immediately
            self._schedule_tasks()
            
            return worker.id
    
    def worker_heartbeat(
        self,
        worker_id: str,
        status: Optional[str] = None,
        resources: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update worker heartbeat.
        
        Args:
            worker_id: ID of the worker
            status: Optional new status for the worker
            resources: Optional resource metrics
            
        Raises:
            WorkerNotFoundError: If worker not found
        """
        with self.worker_lock:
            worker = self._get_worker(worker_id)
            
            if status:
                worker.set_status(status)
                
            worker.heartbeat(resources)
            
            logger.debug(f"Worker heartbeat: {worker_id}")
    
    def claim_task(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Claim a task for a worker.
        
        Args:
            worker_id: ID of the worker claiming a task
            
        Returns:
            Task data dictionary or None if no tasks available
            
        Raises:
            WorkerNotFoundError: If worker not found
        """
        with self.task_lock, self.worker_lock:
            worker = self._get_worker(worker_id)
            
            # Check if worker can accept more tasks
            if not worker.has_capacity():
                logger.debug(f"Worker {worker_id} has no capacity for more tasks")
                return None
            
            # Find suitable task
            task_id = self._find_task_for_worker(worker)
            if not task_id:
                logger.debug(f"No suitable tasks for worker {worker_id}")
                return None
            
            # Get task
            task = self.tasks[task_id]
            
            # Update task status
            task.claim(worker_id)
            
            # Update worker
            worker.claim_task(task_id)
            
            # Update running tasks set
            self._remove_from_pending_queue(task)
            self.running_tasks.add(task_id)
            
            logger.info(f"Task {task_id} claimed by worker {worker_id}")
            
            # Return task data
            return task.to_dict()
    
    def start_task(self, worker_id: str, task_id: str) -> None:
        """
        Mark a task as started by a worker.
        
        Args:
            worker_id: ID of the worker
            task_id: ID of the task
            
        Raises:
            WorkerNotFoundError: If worker not found
            TaskNotFoundError: If task not found
        """
        with self.task_lock:
            task = self._get_task(task_id)
            
            # Verify worker owns this task
            if task.claimed_by != worker_id:
                raise TaskQueueError(f"Task {task_id} not claimed by worker {worker_id}")
            
            # Update task status
            task.start()
            
            logger.info(f"Task {task_id} started by worker {worker_id}")
    
    def complete_task(
        self,
        worker_id: str,
        task_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Mark a task as completed by a worker.
        
        Args:
            worker_id: ID of the worker
            task_id: ID of the task
            result: Optional task result data
            
        Raises:
            WorkerNotFoundError: If worker not found
            TaskNotFoundError: If task not found
        """
        with self.task_lock, self.worker_lock:
            task = self._get_task(task_id)
            worker = self._get_worker(worker_id)
            
            # Verify worker owns this task
            if task.claimed_by != worker_id:
                raise TaskQueueError(f"Task {task_id} not claimed by worker {worker_id}")
            
            # Update task status
            task.complete(result)
            
            # Update worker
            worker.release_task(task_id, success=True)
            
            # Update task sets
            self.running_tasks.remove(task_id)
            self.completed_tasks.add(task_id)
            
            # Update metrics
            self.metrics["tasks_completed"] += 1
            if task.started_at and task.completed_at:
                duration = (task.completed_at - task.started_at).total_seconds()
                self.metrics["avg_task_duration"] = (
                    (self.metrics["avg_task_duration"] * (self.metrics["tasks_completed"] - 1) + duration) /
                    self.metrics["tasks_completed"]
                )
            
            logger.info(f"Task {task_id} completed by worker {worker_id}")
            
            # Trigger callbacks
            self._trigger_task_callbacks(task)
            
            # Check if any dependent tasks can now be scheduled
            self._check_dependent_tasks(task_id)
            
            # Try to schedule more tasks
            self._schedule_tasks()
    
    def fail_task(
        self,
        worker_id: str,
        task_id: str,
        error: Optional[str] = None,
        retry: bool = True,
    ) -> None:
        """
        Mark a task as failed by a worker.
        
        Args:
            worker_id: ID of the worker
            task_id: ID of the task
            error: Optional error message
            retry: Whether to retry the task
            
        Raises:
            WorkerNotFoundError: If worker not found
            TaskNotFoundError: If task not found
        """
        with self.task_lock, self.worker_lock:
            task = self._get_task(task_id)
            worker = self._get_worker(worker_id)
            
            # Verify worker owns this task
            if task.claimed_by != worker_id:
                raise TaskQueueError(f"Task {task_id} not claimed by worker {worker_id}")
            
            # Update task status
            task.fail(error)
            
            # Update worker
            worker.release_task(task_id, success=False)
            
            # Update task sets
            self.running_tasks.remove(task_id)
            
            # Check if should retry
            if retry and task.retry_count < self.max_retries:
                logger.info(f"Task {task_id} failed, retrying ({task.retry_count + 1}/{self.max_retries})")
                task.retry()
                self._add_to_pending_queue(task)
                self.metrics["tasks_retried"] += 1
            else:
                logger.info(f"Task {task_id} failed, no more retries")
                self.failed_tasks.add(task_id)
                self.metrics["tasks_failed"] += 1
                
                # Trigger callbacks
                self._trigger_task_callbacks(task)
            
            # Try to schedule more tasks
            self._schedule_tasks()
    
    def cancel_task(self, task_id: str) -> None:
        """
        Cancel a task.
        
        Args:
            task_id: ID of the task
            
        Raises:
            TaskNotFoundError: If task not found
        """
        with self.task_lock:
            task = self._get_task(task_id)
            
            # Only cancel if task is not completed or failed
            if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                raise TaskQueueError(f"Cannot cancel task {task_id} with status {task.status}")
            
            # Update task status
            task.cancel()
            
            # Update task sets
            if task.id in self.running_tasks:
                self.running_tasks.remove(task.id)
                
                # If claimed by a worker, update worker
                if task.claimed_by:
                    try:
                        worker = self._get_worker(task.claimed_by)
                        worker.release_task(task.id, success=False)
                    except WorkerNotFoundError:
                        # Worker might be gone
                        pass
            else:
                self._remove_from_pending_queue(task)
            
            logger.info(f"Task {task_id} cancelled")
            
            # Trigger callbacks
            self._trigger_task_callbacks(task)
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Get task data.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task data dictionary
            
        Raises:
            TaskNotFoundError: If task not found
        """
        with self.task_lock:
            task = self._get_task(task_id)
            return task.to_dict()
    
    def get_worker(self, worker_id: str) -> Dict[str, Any]:
        """
        Get worker data.
        
        Args:
            worker_id: ID of the worker
            
        Returns:
            Worker data dictionary
            
        Raises:
            WorkerNotFoundError: If worker not found
        """
        with self.worker_lock:
            worker = self._get_worker(worker_id)
            return worker.to_dict()
    
    def list_tasks(
        self,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List tasks with optional filtering.
        
        Args:
            status: Optional status filter
            task_type: Optional task type filter
            limit: Max number of tasks to return
            offset: Offset for pagination
            
        Returns:
            List of task data dictionaries
        """
        with self.task_lock:
            tasks = list(self.tasks.values())
            
            # Apply filters
            if status:
                tasks = [t for t in tasks if t.status == status]
            if task_type:
                tasks = [t for t in tasks if t.task_type == task_type]
                
            # Sort by priority then timestamp
            tasks.sort(key=lambda t: (-t.priority, t.created_at))
            
            # Apply pagination
            tasks = tasks[offset:offset + limit]
            
            return [t.to_dict() for t in tasks]
    
    def list_workers(
        self,
        status: Optional[str] = None,
        capability: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List workers with optional filtering.
        
        Args:
            status: Optional status filter
            capability: Optional capability filter
            limit: Max number of workers to return
            offset: Offset for pagination
            
        Returns:
            List of worker data dictionaries
        """
        with self.worker_lock:
            workers = list(self.workers.values())
            
            # Apply filters
            if status:
                workers = [w for w in workers if w.status == status]
            if capability:
                workers = [w for w in workers if capability in w.capabilities]
                
            # Sort by last heartbeat
            workers.sort(key=lambda w: w.last_heartbeat or datetime.min, reverse=True)
            
            # Apply pagination
            workers = workers[offset:offset + limit]
            
            return [w.to_dict() for w in workers]
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Dictionary of queue statistics
        """
        with self.task_lock, self.worker_lock:
            # Count tasks by status
            pending_count = sum(len(tasks) for tasks in self.pending_tasks.values())
            tasks_by_status = {
                TaskStatus.PENDING: pending_count,
                TaskStatus.RUNNING: len(self.running_tasks),
                TaskStatus.COMPLETED: len(self.completed_tasks),
                TaskStatus.FAILED: len(self.failed_tasks),
                # Count other statuses
                TaskStatus.CLAIMED: len([t for t in self.tasks.values() if t.status == TaskStatus.CLAIMED]),
                TaskStatus.CANCELLED: len([t for t in self.tasks.values() if t.status == TaskStatus.CANCELLED]),
                TaskStatus.TIMEOUT: len([t for t in self.tasks.values() if t.status == TaskStatus.TIMEOUT]),
            }
            
            # Count tasks by type
            tasks_by_type = {}
            for task in self.tasks.values():
                if task.task_type not in tasks_by_type:
                    tasks_by_type[task.task_type] = 0
                tasks_by_type[task.task_type] += 1
            
            # Count workers by status
            workers_by_status = {
                WorkerStatus.ONLINE: len([w for w in self.workers.values() if w.status == WorkerStatus.ONLINE]),
                WorkerStatus.BUSY: len([w for w in self.workers.values() if w.status == WorkerStatus.BUSY]),
                WorkerStatus.OFFLINE: len([w for w in self.workers.values() if w.status == WorkerStatus.OFFLINE]),
                WorkerStatus.ERROR: len([w for w in self.workers.values() if w.status == WorkerStatus.ERROR]),
            }
            
            # Calculate throughput metrics
            return {
                "task_count": len(self.tasks),
                "worker_count": len(self.workers),
                "tasks_by_status": tasks_by_status,
                "tasks_by_type": tasks_by_type,
                "workers_by_status": workers_by_status,
                "metrics": self.metrics,
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    def register_task_callback(
        self,
        task_id: str,
        callback: Callable[[Task], None],
    ) -> None:
        """
        Register a callback for a task.
        
        The callback will be called when the task reaches a terminal state
        (completed, failed, cancelled, timeout).
        
        Args:
            task_id: ID of the task
            callback: Callback function
        """
        with self.task_lock:
            if task_id not in self.task_callbacks:
                self.task_callbacks[task_id] = []
            self.task_callbacks[task_id].append(callback)
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the task queue.
        
        Args:
            wait: Whether to wait for monitoring threads to stop
        """
        logger.info("Shutting down task queue")
        
        # Stop monitoring
        self.monitor_running = False
        
        # Persist state if path is set
        if self.persistence_path:
            self._persist_state()
        
        # Wait for threads to stop if requested
        if wait and self.monitor_thread:
            self.monitor_thread.join()
        if wait and self.persistence_thread:
            self.persistence_thread.join()
    
    def _get_task(self, task_id: str) -> Task:
        """Get task by ID, raising TaskNotFoundError if not found."""
        if task_id not in self.tasks:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return self.tasks[task_id]
    
    def _get_worker(self, worker_id: str) -> Worker:
        """Get worker by ID, raising WorkerNotFoundError if not found."""
        if worker_id not in self.workers:
            raise WorkerNotFoundError(f"Worker not found: {worker_id}")
        return self.workers[worker_id]
    
    def _add_to_pending_queue(self, task: Task) -> None:
        """Add a task to the pending queue."""
        if task.priority not in self.pending_tasks:
            self.pending_tasks[task.priority] = set()
        self.pending_tasks[task.priority].add(task.id)
    
    def _remove_from_pending_queue(self, task: Task) -> None:
        """Remove a task from the pending queue."""
        if task.priority in self.pending_tasks and task.id in self.pending_tasks[task.priority]:
            self.pending_tasks[task.priority].remove(task.id)
            if not self.pending_tasks[task.priority]:
                del self.pending_tasks[task.priority]
    
    def _can_start_task(self, task: Task) -> bool:
        """Check if a task can start (all dependencies completed)."""
        if not task.dependencies:
            return True
            
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                logger.warning(f"Task {task.id} depends on unknown task {dep_id}")
                return False
                
            dep_task = self.tasks[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
                
        return True
    
    def _check_dependent_tasks(self, completed_task_id: str) -> None:
        """Check if any tasks depending on the completed task can now be scheduled."""
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and 
                task.dependencies and 
                completed_task_id in task.dependencies and
                self._can_start_task(task)):
                self._add_to_pending_queue(task)
    
    def _find_task_for_worker(self, worker: Worker) -> Optional[str]:
        """Find a suitable task for a worker."""
        # Check worker capacity and status
        if not worker.has_capacity() or worker.status not in (WorkerStatus.ONLINE, WorkerStatus.BUSY):
            return None
            
        # Get worker capabilities
        capabilities = worker.capabilities
        
        # Check each priority level, from highest to lowest
        for priority in sorted(self.pending_tasks.keys(), reverse=True):
            tasks = self.pending_tasks[priority]
            
            # Find a task with a type the worker supports
            for task_id in tasks:
                task = self.tasks[task_id]
                
                # Check if worker can handle this task type
                if not capabilities or task.task_type in capabilities:
                    return task_id
                    
        return None
    
    def _schedule_tasks(self) -> None:
        """Schedule pending tasks to available workers."""
        # This is a simplified version, actual implementation would be more complex
        # and would handle worker affinity, location awareness, etc.
        
        # For each worker with capacity
        for worker_id, worker in self.workers.items():
            if worker.has_capacity() and worker.status in (WorkerStatus.ONLINE, WorkerStatus.BUSY):
                # Find a suitable task
                task_id = self._find_task_for_worker(worker)
                if task_id:
                    # Get task
                    task = self.tasks[task_id]
                    
                    # Update task status
                    task.claim(worker_id)
                    
                    # Update worker
                    worker.claim_task(task_id)
                    
                    # Update task sets
                    self._remove_from_pending_queue(task)
                    self.running_tasks.add(task_id)
                    
                    logger.info(f"Task {task_id} auto-assigned to worker {worker_id}")
    
    def _trigger_task_callbacks(self, task: Task) -> None:
        """Trigger callbacks for a task."""
        if task.id in self.task_callbacks:
            for callback in self.task_callbacks[task.id]:
                try:
                    callback(task)
                except Exception as e:
                    logger.error(f"Error in task callback: {e}")
    
    def _start_monitoring(self) -> None:
        """Start monitoring threads."""
        self.monitor_running = True
        
        # Start monitor thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="TaskQueueMonitor",
            daemon=True,
        )
        self.monitor_thread.start()
        
        # Start persistence thread if path is set
        if self.persistence_path:
            self.persistence_thread = threading.Thread(
                target=self._persistence_loop,
                name="TaskQueuePersistence",
                daemon=True,
            )
            self.persistence_thread.start()
    
    def _monitor_loop(self) -> None:
        """Monitor loop to check for dead workers and task timeouts."""
        logger.info("Starting monitor thread")
        
        while self.monitor_running:
            try:
                self._check_dead_workers()
                self._check_task_timeouts()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
    
    def _persistence_loop(self) -> None:
        """Persistence loop to save queue state."""
        logger.info("Starting persistence thread")
        
        while self.monitor_running:
            try:
                self._persist_state()
                time.sleep(self.persistence_interval)
            except Exception as e:
                logger.error(f"Error in persistence loop: {e}")
    
    def _check_dead_workers(self) -> None:
        """Check for dead workers and handle their tasks."""
        with self.worker_lock, self.task_lock:
            current_time = datetime.utcnow()
            dead_workers = []
            
            # Find dead workers
            for worker_id, worker in self.workers.items():
                if (worker.status != WorkerStatus.OFFLINE and
                    worker.last_heartbeat and
                    (current_time - worker.last_heartbeat) > timedelta(seconds=self.worker_timeout)):
                    logger.warning(f"Worker {worker_id} appears to be dead, no heartbeat for {self.worker_timeout}s")
                    
                    # Mark as offline
                    worker.set_status(WorkerStatus.OFFLINE, "Worker timeout")
                    
                    # Add to dead workers list
                    dead_workers.append(worker_id)
                    
                    # Update metrics
                    self.metrics["workers_lost"] += 1
            
            # Handle tasks from dead workers
            for worker_id in dead_workers:
                worker = self.workers[worker_id]
                
                # Get tasks assigned to this worker
                for task_id in list(worker.current_tasks):
                    if task_id in self.tasks:
                        task = self.tasks[task_id]
                        
                        # Mark task as failed for retry
                        task.fail("Worker died during task execution")
                        
                        # Update task sets
                        if task_id in self.running_tasks:
                            self.running_tasks.remove(task_id)
                        
                        # Retry task if possible
                        if task.retry_count < self.max_retries:
                            logger.info(f"Task {task_id} failed due to dead worker, retrying")
                            task.retry()
                            self._add_to_pending_queue(task)
                            self.metrics["tasks_retried"] += 1
                        else:
                            logger.info(f"Task {task_id} failed due to dead worker, no more retries")
                            self.failed_tasks.add(task_id)
                            self.metrics["tasks_failed"] += 1
                            
                            # Trigger callbacks
                            self._trigger_task_callbacks(task)
                
                # Clear worker's current tasks
                worker.current_tasks.clear()
    
    def _check_task_timeouts(self) -> None:
        """Check for task timeouts."""
        with self.task_lock:
            current_time = datetime.utcnow()
            
            # Check running tasks for timeouts
            for task_id in list(self.running_tasks):
                task = self.tasks[task_id]
                
                # Skip tasks without a start time
                if not task.started_at:
                    continue
                
                # Check if task has timed out
                elapsed = (current_time - task.started_at).total_seconds()
                if elapsed > task.timeout:
                    logger.warning(f"Task {task_id} timed out after {elapsed}s")
                    
                    # Mark task as timed out
                    task.timeout_task()
                    
                    # Update task sets
                    self.running_tasks.remove(task_id)
                    self.failed_tasks.add(task_id)
                    
                    # Update worker if task was claimed
                    if task.claimed_by:
                        try:
                            worker = self._get_worker(task.claimed_by)
                            worker.release_task(task_id, success=False)
                        except WorkerNotFoundError:
                            # Worker might be gone
                            pass
                    
                    # Trigger callbacks
                    self._trigger_task_callbacks(task)
    
    def _persist_state(self) -> None:
        """Persist queue state to disk."""
        if not self.persistence_path:
            return
            
        logger.debug("Persisting queue state")
        
        try:
            # Create state dictionary
            state = {
                "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
                "workers": {worker_id: worker.to_dict() for worker_id, worker in self.workers.items()},
                "queue_stats": self.get_queue_stats(),
            }
            
            # Write to temporary file first
            temp_path = f"{self.persistence_path}.tmp"
            with open(temp_path, "w") as f:
                json.dump(state, f, indent=2)
                
            # Rename to actual path for atomic update
            import os
            os.replace(temp_path, self.persistence_path)
            
            logger.debug(f"Queue state persisted to {self.persistence_path}")
        except Exception as e:
            logger.error(f"Error persisting queue state: {e}")
    
    def load_state(self, path: Optional[str] = None) -> None:
        """
        Load queue state from disk.
        
        Args:
            path: Path to load state from, defaults to persistence_path
        """
        path = path or self.persistence_path
        if not path:
            logger.warning("No persistence path specified, cannot load state")
            return
            
        try:
            logger.info(f"Loading queue state from {path}")
            
            with open(path, "r") as f:
                state = json.load(f)
                
            with self.task_lock, self.worker_lock:
                # Load tasks
                if "tasks" in state:
                    self.tasks = {}
                    for task_data in state["tasks"].values():
                        task = Task.from_dict(task_data)
                        self.tasks[task.id] = task
                        
                        # Update task sets
                        if task.status == TaskStatus.PENDING:
                            self._add_to_pending_queue(task)
                        elif task.status == TaskStatus.RUNNING or task.status == TaskStatus.CLAIMED:
                            self.running_tasks.add(task.id)
                        elif task.status == TaskStatus.COMPLETED:
                            self.completed_tasks.add(task.id)
                        elif task.status == TaskStatus.FAILED or task.status == TaskStatus.TIMEOUT:
                            self.failed_tasks.add(task.id)
                
                # Load workers
                if "workers" in state:
                    self.workers = {}
                    self.worker_by_capability = {}
                    
                    for worker_data in state["workers"].values():
                        worker = Worker.from_dict(worker_data)
                        self.workers[worker.id] = worker
                        
                        # Index worker by capabilities
                        for capability in worker.capabilities:
                            if capability not in self.worker_by_capability:
                                self.worker_by_capability[capability] = set()
                            self.worker_by_capability[capability].add(worker.id)
                
            logger.info(f"Loaded {len(self.tasks)} tasks and {len(self.workers)} workers")
        except Exception as e:
            logger.error(f"Error loading queue state: {e}")
    
    def __enter__(self) -> 'TaskQueue':
        """Context manager enter."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.shutdown() 