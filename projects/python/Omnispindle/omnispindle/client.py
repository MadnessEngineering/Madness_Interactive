"""
Omnispindle Client

This module provides client interfaces to interact with the Omnispindle distributed task system.
The TaskQueueClient handles communication with the task queue, while WorkerClient manages
worker registration and task execution.
"""

import json
import uuid
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Callable, Union, Tuple

import requests
from requests.exceptions import RequestException

from .models.task import Task, TaskStatus
from .models.worker import Worker, WorkerStatus

# Configure logging
logger = logging.getLogger(__name__)


class OmnispindleClientError(Exception):
    """Base exception for Omnispindle client errors."""
    pass


class TaskQueueClient:
    """
    Client for interacting with the Omnispindle task queue.
    
    Provides methods to submit, query, and manage tasks in the distributed system.
    Can connect to both local (in-process) and remote task queues.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        local_queue = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize the TaskQueueClient.
        
        Args:
            base_url: Base URL for the task queue API (for remote queues)
            local_queue: Local TaskQueue instance (for in-process queues)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.local_queue = local_queue
        self.api_key = api_key
        self.timeout = timeout
        
        if not base_url and not local_queue:
            raise OmnispindleClientError("Either base_url or local_queue must be provided")
    
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
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if self.local_queue:
            return self.local_queue.submit_task(
                task_type=task_type,
                parameters=parameters,
                priority=priority,
                timeout=timeout,
                dependencies=dependencies,
                metadata=metadata,
                task_id=task_id,
            )
        else:
            data = {
                "task_type": task_type,
                "parameters": parameters,
                "priority": priority,
                "timeout": timeout,
                "dependencies": dependencies,
                "metadata": metadata,
                "task_id": task_id,
            }
            
            return self._make_request("POST", "/tasks", data)["task_id"]
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Get task details.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task data dictionary
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if self.local_queue:
            return self.local_queue.get_task(task_id)
        else:
            return self._make_request("GET", f"/tasks/{task_id}")
    
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
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if self.local_queue:
            return self.local_queue.list_tasks(
                status=status,
                task_type=task_type,
                limit=limit,
                offset=offset,
            )
        else:
            params = {}
            if status:
                params["status"] = status
            if task_type:
                params["task_type"] = task_type
            params["limit"] = limit
            params["offset"] = offset
            
            return self._make_request("GET", "/tasks", params=params)["tasks"]
    
    def cancel_task(self, task_id: str) -> None:
        """
        Cancel a task.
        
        Args:
            task_id: ID of the task
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if self.local_queue:
            self.local_queue.cancel_task(task_id)
        else:
            self._make_request("POST", f"/tasks/{task_id}/cancel")
    
    def wait_for_task(
        self,
        task_id: str,
        timeout: Optional[int] = None,
        poll_interval: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Wait for a task to complete.
        
        Args:
            task_id: ID of the task
            timeout: Maximum time to wait in seconds (None for no timeout)
            poll_interval: How often to poll for updates in seconds
            
        Returns:
            Task data dictionary
            
        Raises:
            OmnispindleClientError: If the request fails or times out
            
        Note:
            For local queues, this uses a callback for efficiency.
            For remote queues, this polls the API.
        """
        if self.local_queue:
            # For local queue, use event-based waiting
            event = threading.Event()
            result = [None]
            
            def callback(task):
                result[0] = task.to_dict()
                event.set()
            
            # Register callback
            self.local_queue.register_task_callback(task_id, callback)
            
            # Check current state (might already be done)
            task = self.local_queue.get_task(task_id)
            if task["status"] in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT):
                return task
            
            # Wait for callback or timeout
            if timeout:
                success = event.wait(timeout)
                if not success:
                    raise OmnispindleClientError(f"Timeout waiting for task {task_id}")
            else:
                event.wait()
            
            return result[0]
        else:
            # For remote queue, use polling
            start_time = time.time()
            
            while True:
                task = self.get_task(task_id)
                
                if task["status"] in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT):
                    return task
                
                if timeout and (time.time() - start_time) > timeout:
                    raise OmnispindleClientError(f"Timeout waiting for task {task_id}")
                
                time.sleep(poll_interval)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Dictionary of queue statistics
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if self.local_queue:
            return self.local_queue.get_queue_stats()
        else:
            return self._make_request("GET", "/stats")
    
    def submit_batch(
        self,
        tasks: List[Dict[str, Any]],
        batch_mode: str = "parallel",
    ) -> List[str]:
        """
        Submit a batch of tasks.
        
        Args:
            tasks: List of task definitions (dict with same args as submit_task)
            batch_mode: How to handle the batch ("parallel" or "sequential")
            
        Returns:
            List of task IDs
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if batch_mode not in ("parallel", "sequential"):
            raise ValueError(f"Invalid batch mode: {batch_mode}")
        
        if batch_mode == "parallel":
            # Submit all tasks in parallel
            task_ids = []
            for task_def in tasks:
                task_id = self.submit_task(**task_def)
                task_ids.append(task_id)
            return task_ids
        else:
            # Create dependencies for sequential execution
            task_ids = []
            prev_task_id = None
            
            for task_def in tasks:
                # Add dependency to previous task
                if prev_task_id:
                    if "dependencies" not in task_def:
                        task_def["dependencies"] = []
                    task_def["dependencies"].append(prev_task_id)
                
                # Submit task
                task_id = self.submit_task(**task_def)
                task_ids.append(task_id)
                prev_task_id = task_id
            
            return task_ids
    
    def wait_for_batch(
        self,
        task_ids: List[str],
        timeout: Optional[int] = None,
        poll_interval: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Wait for all tasks in a batch to complete.
        
        Args:
            task_ids: List of task IDs to wait for
            timeout: Maximum time to wait in seconds (None for no timeout)
            poll_interval: How often to poll for updates in seconds
            
        Returns:
            List of task data dictionaries
            
        Raises:
            OmnispindleClientError: If the request fails or times out
        """
        start_time = time.time()
        results = {}
        
        while len(results) < len(task_ids):
            # Check for timeout
            if timeout and (time.time() - start_time) > timeout:
                raise OmnispindleClientError(f"Timeout waiting for batch ({len(results)}/{len(task_ids)} completed)")
            
            # Check unfinished tasks
            for task_id in task_ids:
                if task_id in results:
                    continue
                    
                task = self.get_task(task_id)
                if task["status"] in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT):
                    results[task_id] = task
            
            # If not all done, wait before polling again
            if len(results) < len(task_ids):
                time.sleep(poll_interval)
        
        # Return results in the same order as the input task_ids
        return [results[task_id] for task_id in task_ids]
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a request to the task queue API."""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=self.timeout,
            )
            
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise OmnispindleClientError(f"API request failed: {str(e)}")


class WorkerClient:
    """
    Client for worker nodes in the Omnispindle distributed system.
    
    Handles worker registration, task claiming, and task lifecycle management.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        local_queue = None,
        capabilities: Optional[List[str]] = None,
        capacity: int = 1,
        worker_id: Optional[str] = None,
        heartbeat_interval: int = 30,
        metadata: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize the WorkerClient.
        
        Args:
            base_url: Base URL for the task queue API (for remote queues)
            local_queue: Local TaskQueue instance (for in-process queues)
            capabilities: List of task types this worker can execute
            capacity: Number of concurrent tasks this worker can execute
            worker_id: Optional custom worker ID
            heartbeat_interval: Heartbeat interval in seconds
            metadata: Additional metadata for the worker
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.local_queue = local_queue
        self.api_key = api_key
        self.timeout = timeout
        
        if not base_url and not local_queue:
            raise OmnispindleClientError("Either base_url or local_queue must be provided")
        
        # Worker properties
        self.capabilities = capabilities or []
        self.capacity = capacity
        self.worker_id = worker_id
        self.heartbeat_interval = heartbeat_interval
        self.metadata = metadata or {}
        
        # Worker state
        self.registered = False
        self.worker_id = None
        self.current_tasks = set()
        self.task_executors = {}
        
        # Monitoring thread
        self.heartbeat_thread = None
        self.running = False
    
    def register(self) -> str:
        """
        Register the worker with the task queue.
        
        Returns:
            Worker ID
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if self.registered:
            return self.worker_id
        
        if self.local_queue:
            self.worker_id = self.local_queue.register_worker(
                capabilities=self.capabilities,
                capacity=self.capacity,
                metadata=self.metadata,
                worker_id=self.worker_id,
                heartbeat_interval=self.heartbeat_interval,
            )
        else:
            data = {
                "capabilities": self.capabilities,
                "capacity": self.capacity,
                "metadata": self.metadata,
                "worker_id": self.worker_id,
                "heartbeat_interval": self.heartbeat_interval,
            }
            
            response = self._make_request("POST", "/workers", data)
            self.worker_id = response["worker_id"]
        
        self.registered = True
        
        # Start heartbeat thread
        self._start_heartbeat()
        
        logger.info(f"Worker registered with ID: {self.worker_id}")
        return self.worker_id
    
    def claim_task(self) -> Optional[Dict[str, Any]]:
        """
        Claim a task from the queue.
        
        Returns:
            Task data dictionary or None if no tasks available
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if not self.registered:
            raise OmnispindleClientError("Worker not registered")
        
        if len(self.current_tasks) >= self.capacity:
            return None
        
        if self.local_queue:
            task_data = self.local_queue.claim_task(self.worker_id)
        else:
            task_data = self._make_request("POST", f"/workers/{self.worker_id}/claim")
        
        if task_data:
            self.current_tasks.add(task_data["id"])
        
        return task_data
    
    def start_task(self, task_id: str) -> None:
        """
        Mark a task as started.
        
        Args:
            task_id: ID of the task
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if not self.registered:
            raise OmnispindleClientError("Worker not registered")
        
        if task_id not in self.current_tasks:
            raise OmnispindleClientError(f"Task {task_id} not claimed by this worker")
        
        if self.local_queue:
            self.local_queue.start_task(self.worker_id, task_id)
        else:
            self._make_request("POST", f"/workers/{self.worker_id}/tasks/{task_id}/start")
    
    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark a task as completed.
        
        Args:
            task_id: ID of the task
            result: Optional task result data
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if not self.registered:
            raise OmnispindleClientError("Worker not registered")
        
        if task_id not in self.current_tasks:
            raise OmnispindleClientError(f"Task {task_id} not claimed by this worker")
        
        if self.local_queue:
            self.local_queue.complete_task(self.worker_id, task_id, result)
        else:
            data = {"result": result}
            self._make_request("POST", f"/workers/{self.worker_id}/tasks/{task_id}/complete", data)
        
        self.current_tasks.remove(task_id)
    
    def fail_task(self, task_id: str, error: Optional[str] = None, retry: bool = True) -> None:
        """
        Mark a task as failed.
        
        Args:
            task_id: ID of the task
            error: Optional error message
            retry: Whether to retry the task
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if not self.registered:
            raise OmnispindleClientError("Worker not registered")
        
        if task_id not in self.current_tasks:
            raise OmnispindleClientError(f"Task {task_id} not claimed by this worker")
        
        if self.local_queue:
            self.local_queue.fail_task(self.worker_id, task_id, error, retry)
        else:
            data = {"error": error, "retry": retry}
            self._make_request("POST", f"/workers/{self.worker_id}/tasks/{task_id}/fail", data)
        
        self.current_tasks.remove(task_id)
    
    def heartbeat(self, status: Optional[str] = None, resources: Optional[Dict[str, Any]] = None) -> None:
        """
        Send a heartbeat to the task queue.
        
        Args:
            status: Optional new status for the worker
            resources: Optional resource metrics
            
        Raises:
            OmnispindleClientError: If the request fails
        """
        if not self.registered:
            raise OmnispindleClientError("Worker not registered")
        
        if self.local_queue:
            self.local_queue.worker_heartbeat(self.worker_id, status, resources)
        else:
            data = {"status": status, "resources": resources}
            self._make_request("POST", f"/workers/{self.worker_id}/heartbeat", data)
    
    def register_task_executor(self, task_type: str, executor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Register a task executor function.
        
        Args:
            task_type: Type of task to execute
            executor: Function to execute tasks (takes task data, returns result)
        """
        self.task_executors[task_type] = executor
        
        # Add capability if not already present
        if task_type not in self.capabilities:
            self.capabilities.append(task_type)
    
    def start(self, poll_interval: float = 1.0) -> None:
        """
        Start the worker.
        
        This will register the worker, start the heartbeat thread,
        and begin polling for tasks to execute.
        
        Args:
            poll_interval: How often to poll for new tasks in seconds
        """
        # Register worker if not already registered
        if not self.registered:
            self.register()
        
        self.running = True
        
        # Main worker loop
        while self.running:
            try:
                # Check if we can claim more tasks
                if len(self.current_tasks) < self.capacity:
                    # Claim a task
                    task_data = self.claim_task()
                    
                    if task_data:
                        # Start task in a separate thread
                        thread = threading.Thread(
                            target=self._execute_task,
                            args=(task_data,),
                            name=f"TaskExecutor-{task_data['id']}",
                        )
                        thread.daemon = True
                        thread.start()
                    else:
                        # No tasks available, wait before polling again
                        time.sleep(poll_interval)
                else:
                    # At capacity, wait for tasks to complete
                    time.sleep(poll_interval)
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                time.sleep(poll_interval)
    
    def stop(self) -> None:
        """Stop the worker."""
        logger.info("Stopping worker")
        self.running = False
        
        # Wait for heartbeat thread to stop
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
    
    def _execute_task(self, task_data: Dict[str, Any]) -> None:
        """Execute a task in a separate thread."""
        task_id = task_data["id"]
        task_type = task_data["task_type"]
        
        logger.info(f"Executing task {task_id} (type: {task_type})")
        
        try:
            # Mark task as started
            self.start_task(task_id)
            
            # Check if we have an executor for this task type
            if task_type not in self.task_executors:
                raise OmnispindleClientError(f"No executor registered for task type: {task_type}")
            
            # Execute task
            executor = self.task_executors[task_type]
            result = executor(task_data)
            
            # Mark task as completed
            self.complete_task(task_id, result)
            
            logger.info(f"Task {task_id} completed successfully")
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            
            # Mark task as failed
            self.fail_task(task_id, str(e))
    
    def _start_heartbeat(self) -> None:
        """Start the heartbeat thread."""
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            name="WorkerHeartbeat",
            daemon=True,
        )
        self.heartbeat_thread.start()
    
    def _heartbeat_loop(self) -> None:
        """Heartbeat loop to send periodic heartbeats."""
        logger.info(f"Starting heartbeat thread (interval: {self.heartbeat_interval}s)")
        
        while self.running and self.registered:
            try:
                # Collect resource metrics
                resources = self._collect_resource_metrics()
                
                # Send heartbeat
                self.heartbeat(resources=resources)
                
                # Sleep until next heartbeat
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                time.sleep(5)  # Shorter interval on error
    
    def _collect_resource_metrics(self) -> Dict[str, Any]:
        """Collect resource metrics for the worker."""
        metrics = {
            "tasks_running": len(self.current_tasks),
            "capacity": self.capacity,
            "available_capacity": self.capacity - len(self.current_tasks),
        }
        
        # Add system metrics if psutil is available
        try:
            import psutil
            
            metrics.update({
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
            })
        except ImportError:
            pass
        
        return metrics
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a request to the task queue API."""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=self.timeout,
            )
            
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise OmnispindleClientError(f"API request failed: {str(e)}")
    
    def __enter__(self) -> 'WorkerClient':
        """Context manager enter."""
        if not self.registered:
            self.register()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop() 