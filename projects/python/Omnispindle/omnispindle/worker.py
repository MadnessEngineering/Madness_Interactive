"""
Task Worker

This module provides the TaskWorker class that processes tasks in the distributed task system.
Workers claim tasks, execute them, and report results back to the coordinator.
"""

import uuid
import time
import asyncio
import logging
import importlib
import traceback
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from datetime import datetime, timedelta

from .models.task import Task, TaskStatus
from .models.task_status import TaskStatusInfo
from .storage import TaskStorage

logger = logging.getLogger(__name__)


class TaskHandlerRegistry:
    """
    Registry for task handlers.
    
    This class manages the registration and lookup of handler functions that execute tasks.
    Handlers can be registered by name and later retrieved when a task needs to be executed.
    """
    
    def __init__(self):
        """Initialize an empty handler registry."""
        self._handlers: Dict[str, Callable] = {}
    
    def register(self, name: str, handler: Callable) -> None:
        """
        Register a handler function with the given name.
        
        Args:
            name: The name to register the handler under
            handler: The handler function
        """
        self._handlers[name] = handler
        logger.debug(f"Registered handler: {name}")
    
    def register_function(self, func: Callable) -> Callable:
        """
        Decorator to register a function as a task handler.
        
        Args:
            func: The function to register
            
        Returns:
            The original function (unchanged)
        """
        name = f"{func.__module__}.{func.__name__}"
        self.register(name, func)
        return func
    
    def get_handler(self, name: str) -> Optional[Callable]:
        """
        Get a handler by name.
        
        Args:
            name: The name of the handler to retrieve
            
        Returns:
            The handler function or None if not found
        """
        # Check if it's directly registered
        if name in self._handlers:
            return self._handlers[name]
        
        # Try to import dynamically
        try:
            if "." in name:
                module_name, func_name = name.rsplit(".", 1)
                module = importlib.import_module(module_name)
                return getattr(module, func_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import handler {name}: {e}")
        
        return None
    
    def list_handlers(self) -> List[str]:
        """
        List all registered handlers.
        
        Returns:
            List of registered handler names
        """
        return list(self._handlers.keys())


class TaskWorker:
    """
    Worker that processes tasks from the distributed task system.
    
    The worker claims tasks, executes them using the appropriate handler,
    and reports the results back to the task storage system.
    """
    
    def __init__(
        self,
        storage: TaskStorage,
        worker_id: Optional[str] = None,
        polling_interval: float = 5.0,
        max_concurrent_tasks: int = 10,
        registry: Optional[TaskHandlerRegistry] = None,
    ):
        """
        Initialize a new task worker.
        
        Args:
            storage: Task storage backend to use
            worker_id: Unique identifier for this worker (generated if not provided)
            polling_interval: How often to poll for new tasks (in seconds)
            max_concurrent_tasks: Maximum number of tasks to process concurrently
            registry: Task handler registry (created if not provided)
        """
        self.storage = storage
        self.worker_id = worker_id or f"worker-{uuid.uuid4()}"
        self.polling_interval = polling_interval
        self.max_concurrent_tasks = max_concurrent_tasks
        self.registry = registry or TaskHandlerRegistry()
        
        self._running = False
        self._current_tasks: Dict[str, asyncio.Task] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        # Worker metadata
        self.started_at = None
        self.last_heartbeat = None
        self.tasks_completed = 0
        self.tasks_failed = 0
        
        logger.info(f"Initialized worker {self.worker_id}")
    
    async def start(self) -> None:
        """Start the worker and begin processing tasks."""
        if self._running:
            logger.warning("Worker is already running")
            return
        
        self._running = True
        self._loop = asyncio.get_running_loop()
        self.started_at = datetime.utcnow()
        
        # Start heartbeat
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        logger.info(f"Worker {self.worker_id} started")
        
        try:
            while self._running:
                await self._process_cycle()
                await asyncio.sleep(self.polling_interval)
        except asyncio.CancelledError:
            logger.info("Worker task cancelled")
            self._running = False
        except Exception as e:
            logger.exception(f"Unexpected error in worker loop: {e}")
            self._running = False
            raise
        finally:
            await self.stop()
    
    async def stop(self) -> None:
        """Stop the worker gracefully."""
        if not self._running:
            return
        
        logger.info(f"Stopping worker {self.worker_id}...")
        self._running = False
        
        # Cancel heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Wait for current tasks to complete
        if self._current_tasks:
            logger.info(f"Waiting for {len(self._current_tasks)} tasks to complete")
            pending_tasks = list(self._current_tasks.values())
            await asyncio.gather(*pending_tasks, return_exceptions=True)
        
        logger.info(f"Worker {self.worker_id} stopped")
    
    async def _process_cycle(self) -> None:
        """Run a single processing cycle to claim and execute tasks."""
        # Skip if at capacity
        if len(self._current_tasks) >= self.max_concurrent_tasks:
            return
        
        # Clean up completed tasks
        self._cleanup_finished_tasks()
        
        # Calculate how many new tasks we can take
        slots_available = self.max_concurrent_tasks - len(self._current_tasks)
        if slots_available <= 0:
            return
        
        # Claim new tasks
        try:
            tasks = await self.storage.claim_tasks(self.worker_id, limit=slots_available)
            if tasks:
                logger.info(f"Claimed {len(tasks)} new tasks")
                for task in tasks:
                    self._execute_task(task)
        except Exception as e:
            logger.error(f"Error claiming tasks: {e}")
    
    def _cleanup_finished_tasks(self) -> None:
        """Remove completed tasks from the current tasks dictionary."""
        finished_tasks = []
        for task_id, task in list(self._current_tasks.items()):
            if task.done():
                finished_tasks.append(task_id)
        
        for task_id in finished_tasks:
            self._current_tasks.pop(task_id, None)
    
    def _execute_task(self, task: Task) -> None:
        """
        Execute a task asynchronously.
        
        Args:
            task: The task to execute
        """
        task_coroutine = self._run_task(task)
        async_task = asyncio.create_task(task_coroutine)
        self._current_tasks[task.id] = async_task
    
    async def _run_task(self, task: Task) -> None:
        """
        Execute a task and handle success or failure.
        
        Args:
            task: The task to execute
        """
        logger.info(f"Executing task {task.id}: {task.name}")
        
        # Mark as running
        task.start_execution()
        await self.storage.update_task(task)
        
        try:
            # Get the handler
            handler_name = task.definition.handler
            handler = self.registry.get_handler(handler_name)
            
            if not handler:
                raise ValueError(f"Handler not found: {handler_name}")
            
            # Execute the handler
            result = await self._execute_handler(handler, task)
            
            # Mark as succeeded
            task.complete(result)
            self.tasks_completed += 1
            logger.info(f"Task {task.id} completed successfully")
        
        except asyncio.CancelledError:
            # Worker is shutting down
            logger.warning(f"Task {task.id} cancelled due to worker shutdown")
            # Release the task to be picked up by another worker
            task.status.update(TaskStatus.PENDING)
            task.worker_id = None
        
        except Exception as e:
            # Mark as failed
            error_info = {
                "message": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
            task.fail(error_info)
            self.tasks_failed += 1
            logger.error(f"Task {task.id} failed: {e}")
        
        finally:
            # Update the task in storage
            try:
                await self.storage.update_task(task)
            except Exception as e:
                logger.error(f"Failed to update task {task.id} in storage: {e}")
    
    async def _execute_handler(self, handler: Callable, task: Task) -> Any:
        """
        Execute the task handler.
        
        Supports both synchronous and asynchronous handlers.
        
        Args:
            handler: The handler function to execute
            task: The task to execute
            
        Returns:
            The result of the handler
        """
        # Get handler parameters
        params = task.definition.params or {}
        
        try:
            # Execute the handler
            result = handler(task=task, **params)
            
            # Handle async or sync results
            if asyncio.iscoroutine(result):
                result = await result
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing handler for task {task.id}: {e}")
            raise
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to indicate the worker is alive."""
        while self._running:
            try:
                await self._send_heartbeat()
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            except asyncio.CancelledError:
                logger.debug("Heartbeat loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in heartbeat: {e}")
                await asyncio.sleep(5)  # Shorter delay on error
    
    async def _send_heartbeat(self) -> None:
        """Send a heartbeat to the task storage system."""
        self.last_heartbeat = datetime.utcnow()
        
        heartbeat_data = {
            "worker_id": self.worker_id,
            "timestamp": self.last_heartbeat,
            "uptime_seconds": (self.last_heartbeat - self.started_at).total_seconds() if self.started_at else 0,
            "current_tasks": list(self._current_tasks.keys()),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "max_concurrent_tasks": self.max_concurrent_tasks
        }
        
        try:
            await self.storage.update_worker_heartbeat(self.worker_id, heartbeat_data)
            logger.debug(f"Sent heartbeat for worker {self.worker_id}")
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")
    
    def register_handler(self, name: str, handler: Callable) -> None:
        """
        Register a task handler.
        
        Args:
            name: Name to register the handler under
            handler: The handler function
        """
        self.registry.register(name, handler)
    
    def handler(self, func: Callable) -> Callable:
        """
        Decorator to register a function as a task handler.
        
        Args:
            func: The function to register
            
        Returns:
            The original function (unchanged)
        """
        return self.registry.register_function(func)


# Example task handler registration
def register_default_handlers(registry: TaskHandlerRegistry) -> None:
    """Register default task handlers with the registry."""
    
    @registry.register_function
    async def echo_task(task: Task, message: str = "Hello, World!") -> Dict[str, Any]:
        """Simple echo task handler for testing."""
        return {
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task.id
        }
    
    @registry.register_function
    async def sleep_task(task: Task, seconds: float = 5.0) -> Dict[str, Any]:
        """Task that sleeps for the specified number of seconds."""
        start_time = datetime.utcnow()
        await asyncio.sleep(seconds)
        end_time = datetime.utcnow()
        
        return {
            "slept_for": seconds,
            "actual_duration": (end_time - start_time).total_seconds(),
            "timestamp": end_time.isoformat()
        } 