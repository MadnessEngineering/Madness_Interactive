"""
Omnispindle API Client

This module provides a client for interacting with the Omnispindle API.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

import aiohttp
import requests
from pydantic import ValidationError

from omnispindle.models.task import Task, TaskStatus, TaskPriority, TaskQuery


logger = logging.getLogger(__name__)


class TaskClientError(Exception):
    """Base exception for TaskClient errors."""
    pass


class TaskNotFoundError(TaskClientError):
    """Exception raised when a task is not found."""
    pass


class APIError(TaskClientError):
    """Exception raised for API errors."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error ({status_code}): {message}")


class TaskClient:
    """
    Client for interacting with the Omnispindle API.
    
    This client provides methods for creating, querying, and managing tasks.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the TaskClient.
        
        Args:
            base_url: The base URL of the Omnispindle API.
            api_key: Optional API key for authentication.
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle the API response.
        
        Raises:
            APIError: If the response contains an error.
            TaskNotFoundError: If the task is not found (404).
        """
        if response.status_code == 404:
            raise TaskNotFoundError(f"Task not found: {response.text}")
        
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get("detail", response.text)
            except (ValueError, KeyError):
                error_message = response.text
            
            raise APIError(response.status_code, error_message)
        
        try:
            return response.json()
        except ValueError:
            return {"detail": "No content"}
    
    def create_task(
        self,
        name: str,
        payload: Optional[Dict[str, Any]] = None,
        handler: Optional[str] = None,
        priority: Union[str, TaskPriority] = TaskPriority.NORMAL,
        queue: str = "default",
        tags: Optional[List[str]] = None,
        scheduled_for: Optional[datetime] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        parent_id: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """
        Create a new task.
        
        Args:
            name: The name of the task.
            payload: Optional payload data for the task.
            handler: Optional handler function for the task.
            priority: Priority level for the task.
            queue: Queue to place the task in.
            tags: Optional list of tags for the task.
            scheduled_for: Optional time to schedule the task for.
            timeout: Optional timeout in seconds.
            max_retries: Optional maximum number of retries.
            parent_id: Optional parent task ID.
            depends_on: Optional list of task IDs this task depends on.
            metadata: Optional metadata for the task.
            
        Returns:
            The created Task object.
            
        Raises:
            APIError: If the API returns an error.
        """
        task_data = {
            "name": name,
            "payload": payload or {},
            "priority": priority.value if isinstance(priority, TaskPriority) else priority,
            "queue": queue,
        }
        
        if handler:
            task_data["handler"] = handler
        
        if tags:
            task_data["tags"] = tags
        
        if scheduled_for:
            task_data["scheduled_for"] = scheduled_for.isoformat()
        
        if timeout is not None:
            task_data["timeout"] = timeout
        
        if max_retries is not None:
            task_data["max_retries"] = max_retries
        
        if parent_id:
            task_data["parent_id"] = parent_id
        
        if depends_on:
            task_data["depends_on"] = depends_on
        
        if metadata:
            task_data["metadata"] = metadata
        
        url = f"{self.base_url}/api/tasks"
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=task_data,
        )
        
        result = self._handle_response(response)
        
        try:
            return Task.from_dict(result)
        except ValidationError as e:
            logger.error(f"Failed to parse task data: {e}")
            raise APIError(500, f"Failed to parse task data: {e}")
    
    def get_task(self, task_id: str) -> Task:
        """
        Get a task by ID.
        
        Args:
            task_id: The ID of the task to get.
            
        Returns:
            The Task object.
            
        Raises:
            TaskNotFoundError: If the task is not found.
            APIError: If the API returns an error.
        """
        url = f"{self.base_url}/api/tasks/{task_id}"
        response = requests.get(
            url,
            headers=self._get_headers(),
        )
        
        result = self._handle_response(response)
        
        try:
            return Task.from_dict(result)
        except ValidationError as e:
            logger.error(f"Failed to parse task data: {e}")
            raise APIError(500, f"Failed to parse task data: {e}")
    
    def get_task_status(self, task_id: str) -> str:
        """
        Get the status of a task.
        
        Args:
            task_id: The ID of the task to get the status of.
            
        Returns:
            The status of the task as a string.
            
        Raises:
            TaskNotFoundError: If the task is not found.
            APIError: If the API returns an error.
        """
        url = f"{self.base_url}/api/tasks/{task_id}/status"
        response = requests.get(
            url,
            headers=self._get_headers(),
        )
        
        result = self._handle_response(response)
        return result.get("status")
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the result of a task.
        
        Args:
            task_id: The ID of the task to get the result of.
            
        Returns:
            The result data of the task, or None if the task has no result.
            
        Raises:
            TaskNotFoundError: If the task is not found.
            APIError: If the API returns an error.
        """
        url = f"{self.base_url}/api/tasks/{task_id}/result"
        response = requests.get(
            url,
            headers=self._get_headers(),
        )
        
        result = self._handle_response(response)
        return result.get("data")
    
    def cancel_task(self, task_id: str, reason: Optional[str] = None) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: The ID of the task to cancel.
            reason: Optional reason for cancellation.
            
        Returns:
            True if the task was cancelled, False otherwise.
            
        Raises:
            TaskNotFoundError: If the task is not found.
            APIError: If the API returns an error.
        """
        url = f"{self.base_url}/api/tasks/{task_id}/cancel"
        payload = {}
        if reason:
            payload["reason"] = reason
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
        )
        
        result = self._handle_response(response)
        return result.get("success", False)
    
    def query_tasks(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> List[Task]:
        """
        Query tasks based on filters.
        
        Args:
            filters: Dictionary of filter criteria.
            limit: Maximum number of tasks to return.
            offset: Offset for pagination.
            sort_by: Field to sort by.
            sort_desc: Whether to sort in descending order.
            
        Returns:
            List of Task objects matching the criteria.
            
        Raises:
            APIError: If the API returns an error.
        """
        url = f"{self.base_url}/api/tasks"
        
        params = {
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
            "sort_desc": sort_desc,
        }
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, datetime):
                        params[key] = value.isoformat()
                    elif isinstance(value, (list, dict)):
                        params[key] = json.dumps(value)
                    else:
                        params[key] = value
        
        response = requests.get(
            url,
            headers=self._get_headers(),
            params=params,
        )
        
        result = self._handle_response(response)
        
        try:
            return [Task.from_dict(task_data) for task_data in result.get("items", [])]
        except ValidationError as e:
            logger.error(f"Failed to parse task data: {e}")
            raise APIError(500, f"Failed to parse task data: {e}")
    
    def retry_task(self, task_id: str) -> bool:
        """
        Retry a failed task.
        
        Args:
            task_id: The ID of the task to retry.
            
        Returns:
            True if the task was queued for retry, False otherwise.
            
        Raises:
            TaskNotFoundError: If the task is not found.
            APIError: If the API returns an error.
        """
        url = f"{self.base_url}/api/tasks/{task_id}/retry"
        response = requests.post(
            url,
            headers=self._get_headers(),
        )
        
        result = self._handle_response(response)
        return result.get("success", False)
    
    # Async versions of the methods
    
    async def _init_async_session(self):
        """Initialize the async session if not already initialized."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _handle_async_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """
        Handle the async API response.
        
        Raises:
            APIError: If the response contains an error.
            TaskNotFoundError: If the task is not found (404).
        """
        if response.status == 404:
            text = await response.text()
            raise TaskNotFoundError(f"Task not found: {text}")
        
        if response.status >= 400:
            try:
                error_data = await response.json()
                error_message = error_data.get("detail", await response.text())
            except (ValueError, KeyError):
                error_message = await response.text()
            
            raise APIError(response.status, error_message)
        
        try:
            return await response.json()
        except ValueError:
            return {"detail": "No content"}
    
    async def create_task_async(
        self,
        name: str,
        payload: Optional[Dict[str, Any]] = None,
        handler: Optional[str] = None,
        priority: Union[str, TaskPriority] = TaskPriority.NORMAL,
        queue: str = "default",
        tags: Optional[List[str]] = None,
        scheduled_for: Optional[datetime] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        parent_id: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """
        Create a new task asynchronously.
        
        See `create_task` for parameter details.
        """
        await self._init_async_session()
        
        task_data = {
            "name": name,
            "payload": payload or {},
            "priority": priority.value if isinstance(priority, TaskPriority) else priority,
            "queue": queue,
        }
        
        if handler:
            task_data["handler"] = handler
        
        if tags:
            task_data["tags"] = tags
        
        if scheduled_for:
            task_data["scheduled_for"] = scheduled_for.isoformat()
        
        if timeout is not None:
            task_data["timeout"] = timeout
        
        if max_retries is not None:
            task_data["max_retries"] = max_retries
        
        if parent_id:
            task_data["parent_id"] = parent_id
        
        if depends_on:
            task_data["depends_on"] = depends_on
        
        if metadata:
            task_data["metadata"] = metadata
        
        url = f"{self.base_url}/api/tasks"
        
        async with self.session.post(
            url,
            headers=self._get_headers(),
            json=task_data,
        ) as response:
            result = await self._handle_async_response(response)
        
        try:
            return Task.from_dict(result)
        except ValidationError as e:
            logger.error(f"Failed to parse task data: {e}")
            raise APIError(500, f"Failed to parse task data: {e}")
    
    async def get_task_async(self, task_id: str) -> Task:
        """
        Get a task by ID asynchronously.
        
        See `get_task` for parameter details.
        """
        await self._init_async_session()
        
        url = f"{self.base_url}/api/tasks/{task_id}"
        
        async with self.session.get(
            url,
            headers=self._get_headers(),
        ) as response:
            result = await self._handle_async_response(response)
        
        try:
            return Task.from_dict(result)
        except ValidationError as e:
            logger.error(f"Failed to parse task data: {e}")
            raise APIError(500, f"Failed to parse task data: {e}")
    
    async def get_task_status_async(self, task_id: str) -> str:
        """
        Get the status of a task asynchronously.
        
        See `get_task_status` for parameter details.
        """
        await self._init_async_session()
        
        url = f"{self.base_url}/api/tasks/{task_id}/status"
        
        async with self.session.get(
            url,
            headers=self._get_headers(),
        ) as response:
            result = await self._handle_async_response(response)
        
        return result.get("status")
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None 