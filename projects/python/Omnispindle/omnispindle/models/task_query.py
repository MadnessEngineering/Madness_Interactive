"""
Task Query Model

This module provides models for querying and filtering tasks.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class QueryOperator(str, Enum):
    """Enum for query operators."""
    EQ = "eq"  # Equal
    NE = "ne"  # Not equal
    GT = "gt"  # Greater than
    GTE = "gte"  # Greater than or equal
    LT = "lt"  # Less than
    LTE = "lte"  # Less than or equal
    IN = "in"  # In list
    NIN = "nin"  # Not in list
    CONTAINS = "contains"  # Contains substring
    STARTS_WITH = "starts_with"  # Starts with
    ENDS_WITH = "ends_with"  # Ends with
    EXISTS = "exists"  # Field exists
    MATCH = "match"  # Regex match
    BETWEEN = "between"  # Between two values


class FilterCondition(BaseModel):
    """
    Model for a single filter condition.
    
    Examples:
        - {"field": "status", "op": "eq", "value": "pending"}
        - {"field": "created_at", "op": "gte", "value": "2022-01-01T00:00:00Z"}
        - {"field": "tags", "op": "in", "value": ["important", "urgent"]}
    """
    field: str
    op: QueryOperator
    value: Any


class TaskQuery(BaseModel):
    """
    Model for querying tasks with complex filters.
    
    Attributes:
        filters: List of filter conditions to apply (AND logic)
        or_filters: List of filter condition lists (OR logic between lists)
        limit: Maximum number of tasks to return
        offset: Number of tasks to skip
        sort_by: Field to sort by
        sort_desc: Whether to sort in descending order
    """
    filters: Optional[List[FilterCondition]] = Field(default_factory=list)
    or_filters: Optional[List[List[FilterCondition]]] = Field(default_factory=list)
    limit: int = Field(default=100)
    offset: int = Field(default=0)
    sort_by: str = Field(default="created_at")
    sort_desc: bool = Field(default=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the query to a dictionary format for API requests."""
        return {
            "filters": [f.dict() for f in self.filters] if self.filters else [],
            "or_filters": [[f.dict() for f in filter_group] for filter_group in self.or_filters] if self.or_filters else [],
            "limit": self.limit,
            "offset": self.offset,
            "sort_by": self.sort_by,
            "sort_desc": self.sort_desc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskQuery":
        """
        Create a TaskQuery from a dictionary.
        
        Args:
            data: Dictionary containing query parameters
            
        Returns:
            TaskQuery object
        """
        filters = []
        if "filters" in data and data["filters"]:
            for filter_data in data["filters"]:
                filters.append(FilterCondition(**filter_data))
        
        or_filters = []
        if "or_filters" in data and data["or_filters"]:
            for filter_group in data["or_filters"]:
                or_filters.append([FilterCondition(**f) for f in filter_group])
        
        return cls(
            filters=filters,
            or_filters=or_filters,
            limit=data.get("limit", 100),
            offset=data.get("offset", 0),
            sort_by=data.get("sort_by", "created_at"),
            sort_desc=data.get("sort_desc", True),
        )


class TaskFilter:
    """
    Helper class for building task queries programmatically.
    
    Example:
        ```
        filter = TaskFilter() \
            .status_equals("pending") \
            .created_after(datetime(2022, 1, 1)) \
            .with_tags(["important"]) \
            .build()
        ```
    """
    
    def __init__(self):
        self.filters = []
        self.or_filters = []
        self.current_limit = 100
        self.current_offset = 0
        self.current_sort_by = "created_at"
        self.current_sort_desc = True
    
    def add_filter(self, field: str, op: Union[str, QueryOperator], value: Any) -> "TaskFilter":
        """Add a filter condition."""
        if isinstance(op, str):
            op = QueryOperator(op)
        
        self.filters.append(FilterCondition(field=field, op=op, value=value))
        return self
    
    def add_or_filters(self, filter_conditions: List[FilterCondition]) -> "TaskFilter":
        """Add a group of OR conditions."""
        self.or_filters.append(filter_conditions)
        return self
    
    def status_equals(self, status: str) -> "TaskFilter":
        """Filter by task status."""
        return self.add_filter("status", QueryOperator.EQ, status)
    
    def priority_equals(self, priority: str) -> "TaskFilter":
        """Filter by task priority."""
        return self.add_filter("priority", QueryOperator.EQ, priority)
    
    def queue_equals(self, queue: str) -> "TaskFilter":
        """Filter by task queue."""
        return self.add_filter("queue", QueryOperator.EQ, queue)
    
    def with_tag(self, tag: str) -> "TaskFilter":
        """Filter tasks that have a specific tag."""
        return self.add_filter("tags", QueryOperator.CONTAINS, tag)
    
    def with_tags(self, tags: List[str]) -> "TaskFilter":
        """Filter tasks that have any of the specified tags."""
        filter_conditions = [
            FilterCondition(field="tags", op=QueryOperator.CONTAINS, value=tag)
            for tag in tags
        ]
        self.or_filters.append(filter_conditions)
        return self
    
    def created_after(self, timestamp: Union[datetime, str]) -> "TaskFilter":
        """Filter tasks created after a specific timestamp."""
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()
        return self.add_filter("created_at", QueryOperator.GTE, timestamp)
    
    def created_before(self, timestamp: Union[datetime, str]) -> "TaskFilter":
        """Filter tasks created before a specific timestamp."""
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()
        return self.add_filter("created_at", QueryOperator.LTE, timestamp)
    
    def scheduled_after(self, timestamp: Union[datetime, str]) -> "TaskFilter":
        """Filter tasks scheduled after a specific timestamp."""
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()
        return self.add_filter("scheduled_for", QueryOperator.GTE, timestamp)
    
    def scheduled_before(self, timestamp: Union[datetime, str]) -> "TaskFilter":
        """Filter tasks scheduled before a specific timestamp."""
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()
        return self.add_filter("scheduled_for", QueryOperator.LTE, timestamp)
    
    def payload_contains(self, key: str, value: Any) -> "TaskFilter":
        """Filter tasks where payload contains a specific key-value pair."""
        return self.add_filter(f"payload.{key}", QueryOperator.EQ, value)
    
    def has_parent(self, parent_id: Optional[str] = None) -> "TaskFilter":
        """Filter tasks that have a parent task."""
        if parent_id:
            return self.add_filter("parent_id", QueryOperator.EQ, parent_id)
        return self.add_filter("parent_id", QueryOperator.EXISTS, True)
    
    def is_root_task(self) -> "TaskFilter":
        """Filter tasks that have no parent (root tasks)."""
        return self.add_filter("parent_id", QueryOperator.EXISTS, False)
    
    def has_handler(self, handler: Optional[str] = None) -> "TaskFilter":
        """Filter tasks that have a specific handler."""
        if handler:
            return self.add_filter("handler", QueryOperator.EQ, handler)
        return self.add_filter("handler", QueryOperator.EXISTS, True)
    
    def limit(self, limit: int) -> "TaskFilter":
        """Set the maximum number of tasks to return."""
        self.current_limit = limit
        return self
    
    def offset(self, offset: int) -> "TaskFilter":
        """Set the number of tasks to skip."""
        self.current_offset = offset
        return self
    
    def sort_by(self, field: str, descending: bool = True) -> "TaskFilter":
        """Set the field to sort by and the sort direction."""
        self.current_sort_by = field
        self.current_sort_desc = descending
        return self
    
    def build(self) -> TaskQuery:
        """Build the TaskQuery from the current state."""
        return TaskQuery(
            filters=self.filters,
            or_filters=self.or_filters,
            limit=self.current_limit,
            offset=self.current_offset,
            sort_by=self.current_sort_by,
            sort_desc=self.current_sort_desc,
        ) 