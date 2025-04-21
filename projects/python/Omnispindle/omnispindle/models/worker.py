"""
Worker Model

This module provides a Worker model for the Omnispindle distributed task system.
Workers represent computational resources that can execute tasks.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set


class WorkerStatus:
    """Worker status constants."""
    ONLINE = "online"       # Worker is online and available
    BUSY = "busy"           # Worker is online but executing tasks
    OFFLINE = "offline"     # Worker is offline
    ERROR = "error"         # Worker is in an error state


class Worker:
    """
    Worker class to represent a computational resource in the distributed system.
    
    Workers have the following properties:
    - Unique ID
    - Capabilities (types of tasks they can execute)
    - Status (online, busy, offline, error)
    - Resource metrics (CPU, memory, etc.)
    - Current tasks (tasks being executed)
    - Task history (completed tasks)
    """
    
    def __init__(
        self,
        worker_id: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        capacity: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        heartbeat_interval: int = 30,  # seconds
    ):
        """
        Initialize a worker.
        
        Args:
            worker_id: Optional custom ID, will generate UUID if not provided
            capabilities: List of task types this worker can execute
            capacity: Number of concurrent tasks this worker can execute
            metadata: Optional metadata to store with the worker
            heartbeat_interval: How often the worker should send heartbeats (seconds)
        """
        self.id = worker_id or str(uuid.uuid4())
        self.capabilities = set(capabilities or [])
        self.capacity = capacity
        self.metadata = metadata or {}
        self.heartbeat_interval = heartbeat_interval
        
        # Status management
        self.status = WorkerStatus.OFFLINE
        self.status_message: Optional[str] = None
        
        # Execution tracking
        self.current_tasks: Set[str] = set()  # Task IDs currently being executed
        self.completed_tasks: List[str] = []  # Task IDs of completed tasks
        self.failed_tasks: List[str] = []  # Task IDs of failed tasks
        
        # Metrics
        self.task_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_execution_time = 0.0  # seconds
        
        # Audit trail
        self.registered_at = datetime.utcnow()
        self.last_heartbeat = self.registered_at
        self.updated_at = self.registered_at
        
        # Resource metrics
        self.resources: Dict[str, Any] = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0,
        }
        
        # History tracking
        self.history: List[Dict[str, Any]] = [{
            "timestamp": self.registered_at,
            "status": self.status,
            "message": "Worker registered"
        }]
    
    def add_capability(self, capability: str) -> None:
        """
        Add a capability to this worker.
        
        Args:
            capability: Task type the worker can execute
        """
        self.capabilities.add(capability)
        self.updated_at = datetime.utcnow()
    
    def remove_capability(self, capability: str) -> None:
        """
        Remove a capability from this worker.
        
        Args:
            capability: Task type to remove
        """
        if capability in self.capabilities:
            self.capabilities.remove(capability)
            self.updated_at = datetime.utcnow()
    
    def can_handle(self, task_type: str) -> bool:
        """
        Check if this worker can handle a task of the given type.
        
        Args:
            task_type: Type of task to check
            
        Returns:
            True if the worker can handle the task, False otherwise
        """
        return task_type in self.capabilities
    
    def has_capacity(self) -> bool:
        """
        Check if this worker has capacity to execute more tasks.
        
        Returns:
            True if the worker has capacity, False otherwise
        """
        return len(self.current_tasks) < self.capacity
    
    def claim_task(self, task_id: str) -> None:
        """
        Claim a task for execution.
        
        Args:
            task_id: ID of the task to claim
        """
        if not self.has_capacity():
            raise ValueError("Worker does not have capacity for more tasks")
            
        self.current_tasks.add(task_id)
        
        if len(self.current_tasks) >= self.capacity:
            self.set_status(WorkerStatus.BUSY, "Worker at capacity")
        else:
            self.set_status(WorkerStatus.ONLINE, "Worker processing tasks")
            
        self.updated_at = datetime.utcnow()
    
    def release_task(self, task_id: str, success: bool = True) -> None:
        """
        Release a task after execution.
        
        Args:
            task_id: ID of the task to release
            success: Whether the task was completed successfully
        """
        if task_id in self.current_tasks:
            self.current_tasks.remove(task_id)
            
            if success:
                self.completed_tasks.append(task_id)
                self.success_count += 1
            else:
                self.failed_tasks.append(task_id)
                self.failure_count += 1
                
            self.task_count += 1
            
            # Update status if worker was at capacity
            if self.status == WorkerStatus.BUSY:
                self.set_status(WorkerStatus.ONLINE, "Worker has available capacity")
                
            self.updated_at = datetime.utcnow()
    
    def heartbeat(self, resources: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the worker heartbeat.
        
        Args:
            resources: Optional updated resource metrics
        """
        self.last_heartbeat = datetime.utcnow()
        
        if resources:
            self.resources.update(resources)
            
        # If worker was offline, set to online
        if self.status == WorkerStatus.OFFLINE:
            if len(self.current_tasks) >= self.capacity:
                self.set_status(WorkerStatus.BUSY, "Worker at capacity")
            else:
                self.set_status(WorkerStatus.ONLINE, "Worker back online")
                
        self.updated_at = self.last_heartbeat
    
    def set_status(self, status: str, message: Optional[str] = None) -> None:
        """
        Set the worker status.
        
        Args:
            status: New worker status
            message: Optional message about the status change
        """
        self.status = status
        self.status_message = message
        self.updated_at = datetime.utcnow()
        
        self._add_history_entry(status, message or f"Status changed to {status}")
    
    def is_alive(self) -> bool:
        """
        Check if the worker is alive based on heartbeat.
        
        Returns:
            True if the worker is alive, False otherwise
        """
        cutoff = datetime.utcnow() - timedelta(seconds=self.heartbeat_interval * 2)
        return self.last_heartbeat >= cutoff
    
    def _add_history_entry(self, status: str, message: str) -> None:
        """
        Add an entry to the worker history.
        
        Args:
            status: Status at this point in history
            message: Message describing the event
        """
        self.history.append({
            "timestamp": datetime.utcnow(),
            "status": status,
            "message": message,
            "task_count": len(self.current_tasks)
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert worker to a dictionary representation.
        
        Returns:
            Dictionary representation of the worker
        """
        result = {
            "id": self.id,
            "capabilities": list(self.capabilities),
            "capacity": self.capacity,
            "status": self.status,
            "status_message": self.status_message,
            "current_tasks": list(self.current_tasks),
            "completed_tasks_count": len(self.completed_tasks),
            "failed_tasks_count": len(self.failed_tasks),
            "task_count": self.task_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "total_execution_time": self.total_execution_time,
            "registered_at": self.registered_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resources": self.resources,
            "metadata": self.metadata,
            "heartbeat_interval": self.heartbeat_interval,
            "is_alive": self.is_alive(),
        }
        
        # Include condensed history
        result["history"] = [
            {
                "timestamp": entry["timestamp"].isoformat(),
                "status": entry["status"],
                "message": entry["message"],
                "task_count": entry.get("task_count", 0)
            }
            for entry in self.history
        ]
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Worker':
        """
        Create a worker from a dictionary representation.
        
        Args:
            data: Dictionary representation of a worker
            
        Returns:
            New Worker instance
        """
        worker = cls(
            worker_id=data.get("id"),
            capabilities=data.get("capabilities", []),
            capacity=data.get("capacity", 1),
            metadata=data.get("metadata", {}),
            heartbeat_interval=data.get("heartbeat_interval", 30),
        )
        
        # Convert ISO timestamp strings to datetime objects
        if "registered_at" in data and data["registered_at"]:
            worker.registered_at = datetime.fromisoformat(data["registered_at"])
        if "last_heartbeat" in data and data["last_heartbeat"]:
            worker.last_heartbeat = datetime.fromisoformat(data["last_heartbeat"])
        if "updated_at" in data and data["updated_at"]:
            worker.updated_at = datetime.fromisoformat(data["updated_at"])
            
        # Set status attributes
        worker.status = data.get("status", WorkerStatus.OFFLINE)
        worker.status_message = data.get("status_message")
        
        # Set task tracking
        worker.current_tasks = set(data.get("current_tasks", []))
        worker.completed_tasks = data.get("completed_tasks", [])
        worker.failed_tasks = data.get("failed_tasks", [])
        
        # Set metrics
        worker.task_count = data.get("task_count", 0)
        worker.success_count = data.get("success_count", 0)
        worker.failure_count = data.get("failure_count", 0)
        worker.total_execution_time = data.get("total_execution_time", 0.0)
        
        # Set resources
        if "resources" in data:
            worker.resources = data["resources"]
            
        # Rebuild history with proper datetime objects
        if "history" in data and data["history"]:
            worker.history = [
                {
                    "timestamp": datetime.fromisoformat(entry["timestamp"]),
                    "status": entry["status"],
                    "message": entry["message"],
                    "task_count": entry.get("task_count", 0)
                }
                for entry in data["history"]
            ]
            
        return worker 