"""
Task Storage

This module provides storage backends for the Omnispindle distributed task system.
It defines interfaces for persisting tasks, workers, and task execution results.
"""

import uuid
import json
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union, Type
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from .models.task import Task, TaskStatus
from .models.task_status import TaskStatusInfo

logger = logging.getLogger(__name__)


class TaskStorage(ABC):
    """
    Abstract base class for task storage backends.
    
    Defines the interface that all storage backends must implement to store,
    retrieve, and update tasks in the distributed task system.
    """
    
    @abstractmethod
    async def create_task(self, task: Task) -> Task:
        """
        Create a new task in storage.
        
        Args:
            task: The task to create
            
        Returns:
            The created task with updated metadata
        """
        pass
    
    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Task]:
        """
        Retrieve a task by ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            The task or None if not found
        """
        pass
    
    @abstractmethod
    async def update_task(self, task: Task) -> Task:
        """
        Update an existing task.
        
        Args:
            task: The task to update
            
        Returns:
            The updated task
        """
        pass
    
    @abstractmethod
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: The ID of the task to delete
            
        Returns:
            True if the task was deleted, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_tasks(
        self, 
        status: Optional[Union[TaskStatus, List[TaskStatus]]] = None,
        owner: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """
        List tasks with optional filtering.
        
        Args:
            status: Filter by task status (or list of statuses)
            owner: Filter by task owner
            limit: Maximum number of tasks to return
            offset: Offset for pagination
            
        Returns:
            List of tasks matching the criteria
        """
        pass
    
    @abstractmethod
    async def claim_tasks(
        self, 
        worker_id: str,
        limit: int = 10
    ) -> List[Task]:
        """
        Claim pending tasks for a worker.
        
        Args:
            worker_id: ID of the worker claiming the tasks
            limit: Maximum number of tasks to claim
            
        Returns:
            List of claimed tasks
        """
        pass
    
    @abstractmethod
    async def update_worker_heartbeat(
        self, 
        worker_id: str,
        heartbeat_data: Dict[str, Any]
    ) -> None:
        """
        Update worker heartbeat information.
        
        Args:
            worker_id: ID of the worker
            heartbeat_data: Dictionary of heartbeat data
        """
        pass
    
    @abstractmethod
    async def list_workers(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List registered workers.
        
        Args:
            active_only: If True, only return workers with recent heartbeats
            limit: Maximum number of workers to return
            offset: Offset for pagination
            
        Returns:
            List of worker data dictionaries
        """
        pass


class InMemoryTaskStorage(TaskStorage):
    """
    In-memory implementation of TaskStorage.
    
    This implementation is primarily for testing and development.
    It stores all data in memory and doesn't persist across restarts.
    """
    
    def __init__(self):
        """Initialize an empty in-memory task storage."""
        self._tasks: Dict[str, Task] = {}
        self._workers: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def create_task(self, task: Task) -> Task:
        """Create a new task in storage."""
        async with self._lock:
            # Ensure task has an ID
            if not task.id:
                task.id = str(uuid.uuid4())
            
            # Set created_at if not set
            if not task.created_at:
                task.created_at = datetime.utcnow()
            
            # Store the task
            self._tasks[task.id] = task
            return task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        return self._tasks.get(task_id)
    
    async def update_task(self, task: Task) -> Task:
        """Update an existing task."""
        async with self._lock:
            # Check if task exists
            if task.id not in self._tasks:
                raise ValueError(f"Task with ID {task.id} not found")
            
            # Update the task
            self._tasks[task.id] = task
            return task
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        async with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False
    
    async def list_tasks(
        self, 
        status: Optional[Union[TaskStatus, List[TaskStatus]]] = None,
        owner: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """List tasks with optional filtering."""
        tasks = list(self._tasks.values())
        
        # Filter by status
        if status is not None:
            if isinstance(status, list):
                tasks = [t for t in tasks if t.status.current in status]
            else:
                tasks = [t for t in tasks if t.status.current == status]
        
        # Filter by owner
        if owner is not None:
            tasks = [t for t in tasks if t.owner == owner]
        
        # Sort by created_at (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Apply pagination
        return tasks[offset:offset+limit]
    
    async def claim_tasks(
        self, 
        worker_id: str,
        limit: int = 10
    ) -> List[Task]:
        """Claim pending tasks for a worker."""
        async with self._lock:
            # Find pending tasks
            pending_tasks = [
                t for t in self._tasks.values() 
                if t.status.current == TaskStatus.PENDING and t.worker_id is None
            ]
            
            # Sort by priority (high to low)
            pending_tasks.sort(key=lambda t: t.priority or 0, reverse=True)
            
            # Limit the number of tasks
            tasks_to_claim = pending_tasks[:limit]
            
            # Claim the tasks
            claimed_tasks = []
            for task in tasks_to_claim:
                task.claim(worker_id)
                claimed_tasks.append(task)
            
            return claimed_tasks
    
    async def update_worker_heartbeat(
        self, 
        worker_id: str,
        heartbeat_data: Dict[str, Any]
    ) -> None:
        """Update worker heartbeat information."""
        async with self._lock:
            self._workers[worker_id] = heartbeat_data
    
    async def list_workers(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List registered workers."""
        workers = list(self._workers.values())
        
        # Filter active workers (heartbeat within the last 2 minutes)
        if active_only:
            now = datetime.utcnow()
            workers = [
                w for w in workers 
                if "timestamp" in w and 
                now - datetime.fromisoformat(w["timestamp"]) < timedelta(minutes=2)
            ]
        
        # Apply pagination
        return workers[offset:offset+limit]


class RedisTaskStorage(TaskStorage):
    """
    Redis implementation of TaskStorage.
    
    This implementation uses Redis for persistence and supports distributed
    operation with multiple workers.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize Redis task storage.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self._redis = None
        self._lock = asyncio.Lock()
    
    async def _get_redis(self):
        """Get or create Redis connection."""
        if self._redis is None:
            import aioredis
            self._redis = await aioredis.from_url(self.redis_url)
        return self._redis
    
    async def _task_key(self, task_id: str) -> str:
        """Get Redis key for a task."""
        return f"omnispindle:task:{task_id}"
    
    async def _worker_key(self, worker_id: str) -> str:
        """Get Redis key for a worker."""
        return f"omnispindle:worker:{worker_id}"
    
    async def _serialize_task(self, task: Task) -> str:
        """Serialize task to JSON string."""
        return json.dumps(task.dict())
    
    async def _deserialize_task(self, data: str) -> Task:
        """Deserialize task from JSON string."""
        return Task.parse_obj(json.loads(data))
    
    async def create_task(self, task: Task) -> Task:
        """Create a new task in storage."""
        redis = await self._get_redis()
        
        # Ensure task has an ID
        if not task.id:
            task.id = str(uuid.uuid4())
        
        # Set created_at if not set
        if not task.created_at:
            task.created_at = datetime.utcnow()
        
        # Serialize and store the task
        task_data = await self._serialize_task(task)
        task_key = await self._task_key(task.id)
        await redis.set(task_key, task_data)
        
        # Add to pending list if the task is pending
        if task.status.current == TaskStatus.PENDING:
            await redis.zadd(
                "omnispindle:pending_tasks",
                {task.id: task.priority or 0}
            )
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        redis = await self._get_redis()
        task_key = await self._task_key(task_id)
        task_data = await redis.get(task_key)
        
        if not task_data:
            return None
        
        return await self._deserialize_task(task_data)
    
    async def update_task(self, task: Task) -> Task:
        """Update an existing task."""
        redis = await self._get_redis()
        task_key = await self._task_key(task.id)
        
        # Check if task exists
        exists = await redis.exists(task_key)
        if not exists:
            raise ValueError(f"Task with ID {task.id} not found")
        
        # Update task status in appropriate sets
        previous_status = None
        previous_task_data = await redis.get(task_key)
        if previous_task_data:
            previous_task = await self._deserialize_task(previous_task_data)
            previous_status = previous_task.status.current
        
        current_status = task.status.current
        
        # If status changed, update the status sets
        if previous_status != current_status:
            if previous_status == TaskStatus.PENDING:
                await redis.zrem("omnispindle:pending_tasks", task.id)
            
            if current_status == TaskStatus.PENDING:
                await redis.zadd(
                    "omnispindle:pending_tasks",
                    {task.id: task.priority or 0}
                )
        
        # Update the task data
        task_data = await self._serialize_task(task)
        await redis.set(task_key, task_data)
        
        return task
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        redis = await self._get_redis()
        task_key = await self._task_key(task_id)
        
        # Check if task exists
        exists = await redis.exists(task_key)
        if not exists:
            return False
        
        # Get the task to clean up from sets
        task_data = await redis.get(task_key)
        if task_data:
            task = await self._deserialize_task(task_data)
            if task.status.current == TaskStatus.PENDING:
                await redis.zrem("omnispindle:pending_tasks", task_id)
        
        # Delete the task
        await redis.delete(task_key)
        return True
    
    async def list_tasks(
        self, 
        status: Optional[Union[TaskStatus, List[TaskStatus]]] = None,
        owner: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """List tasks with optional filtering."""
        redis = await self._get_redis()
        
        # If status is PENDING, we can use the sorted set
        if status == TaskStatus.PENDING:
            task_ids = await redis.zrevrange(
                "omnispindle:pending_tasks", 
                offset, 
                offset + limit - 1
            )
            tasks = []
            for task_id in task_ids:
                task = await self.get_task(task_id)
                if task and (owner is None or task.owner == owner):
                    tasks.append(task)
            return tasks
        
        # Otherwise, we need to scan all tasks (less efficient)
        cursor = 0
        tasks = []
        pattern = "omnispindle:task:*"
        
        while True:
            cursor, keys = await redis.scan(cursor, match=pattern, count=100)
            
            for key in keys:
                task_data = await redis.get(key)
                if not task_data:
                    continue
                
                task = await self._deserialize_task(task_data)
                
                # Apply filters
                if status is not None:
                    if isinstance(status, list):
                        if task.status.current not in status:
                            continue
                    elif task.status.current != status:
                        continue
                
                if owner is not None and task.owner != owner:
                    continue
                
                tasks.append(task)
                
                # If we have enough tasks, break early
                if len(tasks) >= offset + limit:
                    break
            
            # If we've scanned all keys or have enough tasks, break
            if cursor == 0 or len(tasks) >= offset + limit:
                break
        
        # Sort by created_at (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Apply pagination
        return tasks[offset:offset+limit]
    
    async def claim_tasks(
        self, 
        worker_id: str,
        limit: int = 10
    ) -> List[Task]:
        """Claim pending tasks for a worker."""
        redis = await self._get_redis()
        
        # Use transaction to ensure atomicity
        async with self._lock:
            # Get high priority pending tasks
            task_ids = await redis.zrevrange(
                "omnispindle:pending_tasks",
                0, 
                limit - 1
            )
            
            if not task_ids:
                return []
            
            claimed_tasks = []
            for task_id in task_ids:
                task_key = await self._task_key(task_id)
                task_data = await redis.get(task_key)
                
                if not task_data:
                    # Task was deleted, remove from pending
                    await redis.zrem("omnispindle:pending_tasks", task_id)
                    continue
                
                task = await self._deserialize_task(task_data)
                
                # Claim the task
                if task.status.current == TaskStatus.PENDING and task.worker_id is None:
                    task.claim(worker_id)
                    await self.update_task(task)
                    claimed_tasks.append(task)
            
            return claimed_tasks
    
    async def update_worker_heartbeat(
        self, 
        worker_id: str,
        heartbeat_data: Dict[str, Any]
    ) -> None:
        """Update worker heartbeat information."""
        redis = await self._get_redis()
        worker_key = await self._worker_key(worker_id)
        
        # Convert heartbeat data to JSON
        if isinstance(heartbeat_data.get("timestamp"), datetime):
            heartbeat_data["timestamp"] = heartbeat_data["timestamp"].isoformat()
        
        worker_data = json.dumps(heartbeat_data)
        
        # Store the worker data with expiry (3 minutes)
        await redis.set(worker_key, worker_data, ex=180)
        
        # Also add to active workers set
        await redis.zadd(
            "omnispindle:active_workers",
            {worker_id: time.time()}
        )
    
    async def list_workers(
        self,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List registered workers."""
        redis = await self._get_redis()
        
        # Get worker IDs
        if active_only:
            # Use the active workers sorted set
            # Get workers with heartbeat in the last 2 minutes
            min_time = time.time() - 120
            worker_ids = await redis.zrevrangebyscore(
                "omnispindle:active_workers",
                "+inf",
                min_time,
                start=offset,
                num=limit
            )
        else:
            # Scan all workers
            cursor = 0
            worker_ids = []
            pattern = "omnispindle:worker:*"
            
            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                
                for key in keys:
                    # Extract worker ID from key
                    worker_id = key.split(":", 2)[2]
                    worker_ids.append(worker_id)
                
                # If we've scanned all keys, break
                if cursor == 0:
                    break
            
            # Apply pagination
            worker_ids = worker_ids[offset:offset+limit]
        
        # Get worker data for each ID
        workers = []
        for worker_id in worker_ids:
            worker_key = await self._worker_key(worker_id)
            worker_data = await redis.get(worker_key)
            
            if worker_data:
                worker = json.loads(worker_data)
                worker["id"] = worker_id  # Include the ID
                workers.append(worker)
        
        return workers


# Factory function to create the appropriate storage backend
def create_storage(
    storage_type: str = "memory",
    **kwargs
) -> TaskStorage:
    """
    Create a task storage backend.
    
    Args:
        storage_type: Type of storage to create ('memory' or 'redis')
        **kwargs: Additional arguments to pass to the storage constructor
        
    Returns:
        A TaskStorage instance
    """
    if storage_type == "memory":
        return InMemoryTaskStorage()
    elif storage_type == "redis":
        return RedisTaskStorage(**kwargs)
    else:
        raise ValueError(f"Unknown storage type: {storage_type}") 