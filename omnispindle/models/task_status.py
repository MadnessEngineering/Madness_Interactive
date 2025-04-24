"""
Task Status Model

This module defines the various states that a task can be in and the transitions between them.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Any
from datetime import datetime

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Enum representing possible task statuses."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    CLAIMED = "claimed"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    RETRYING = "retrying"
    TIMEOUT = "timeout"


class TaskPriority(str, Enum):
    """Enum representing task priorities."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class TaskStatusTransition(BaseModel):
    """Model representing a transition between task statuses."""
    from_status: TaskStatus
    to_status: TaskStatus
    
    class Config:
        frozen = True


# Define valid status transitions
VALID_TRANSITIONS = [
    # Initial states
    TaskStatusTransition(from_status=TaskStatus.PENDING, to_status=TaskStatus.SCHEDULED),
    TaskStatusTransition(from_status=TaskStatus.PENDING, to_status=TaskStatus.CLAIMED),
    TaskStatusTransition(from_status=TaskStatus.PENDING, to_status=TaskStatus.CANCELED),
    
    # Scheduled states
    TaskStatusTransition(from_status=TaskStatus.SCHEDULED, to_status=TaskStatus.CLAIMED),
    TaskStatusTransition(from_status=TaskStatus.SCHEDULED, to_status=TaskStatus.CANCELED),
    
    # Processing states
    TaskStatusTransition(from_status=TaskStatus.CLAIMED, to_status=TaskStatus.RUNNING),
    TaskStatusTransition(from_status=TaskStatus.CLAIMED, to_status=TaskStatus.FAILED),
    TaskStatusTransition(from_status=TaskStatus.CLAIMED, to_status=TaskStatus.CANCELED),
    
    # Running states
    TaskStatusTransition(from_status=TaskStatus.RUNNING, to_status=TaskStatus.SUCCEEDED),
    TaskStatusTransition(from_status=TaskStatus.RUNNING, to_status=TaskStatus.FAILED),
    TaskStatusTransition(from_status=TaskStatus.RUNNING, to_status=TaskStatus.CANCELED),
    TaskStatusTransition(from_status=TaskStatus.RUNNING, to_status=TaskStatus.TIMEOUT),
    
    # Retrying
    TaskStatusTransition(from_status=TaskStatus.FAILED, to_status=TaskStatus.RETRYING),
    TaskStatusTransition(from_status=TaskStatus.TIMEOUT, to_status=TaskStatus.RETRYING),
    TaskStatusTransition(from_status=TaskStatus.RETRYING, to_status=TaskStatus.PENDING),
]


# Build a lookup map for valid transitions
VALID_TRANSITIONS_MAP: Dict[TaskStatus, Set[TaskStatus]] = {status: set() for status in TaskStatus}
for transition in VALID_TRANSITIONS:
    VALID_TRANSITIONS_MAP[transition.from_status].add(transition.to_status)


class TaskStatusInfo(BaseModel):
    """
    Information about a task's status changes.
    
    Attributes:
        current: The current status of the task
        previous: The previous status of the task
        history: A list of status changes with timestamps
        valid_next_statuses: List of valid next statuses based on the current status
        last_updated: When the status was last updated
    """
    current: TaskStatus
    previous: Optional[TaskStatus] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def valid_next_statuses(self) -> List[TaskStatus]:
        """Get the list of valid next statuses based on the current status."""
        return list(VALID_TRANSITIONS_MAP.get(self.current, set()))
    
    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """Check if transitioning to the new status is valid."""
        return new_status in self.valid_next_statuses
    
    def update(self, new_status: TaskStatus, reason: Optional[str] = None) -> None:
        """
        Update the task status.
        
        Args:
            new_status: The new status to transition to
            reason: Optional reason for the status change
            
        Raises:
            ValueError: If the transition is not valid
        """
        if not self.can_transition_to(new_status):
            valid_statuses = ", ".join([s.value for s in self.valid_next_statuses])
            raise ValueError(
                f"Invalid status transition from {self.current} to {new_status}. "
                f"Valid next statuses are: {valid_statuses}"
            )
        
        timestamp = datetime.utcnow()
        
        # Add to history
        history_entry = {
            "from": self.current.value,
            "to": new_status.value,
            "timestamp": timestamp,
        }
        
        if reason:
            history_entry["reason"] = reason
            
        self.history.append(history_entry)
        
        # Update status
        self.previous = self.current
        self.current = new_status
        self.last_updated = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage or serialization."""
        return {
            "current": self.current.value,
            "previous": self.previous.value if self.previous else None,
            "history": self.history,
            "last_updated": self.last_updated.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskStatusInfo":
        """Create from a dictionary representation."""
        current = TaskStatus(data["current"])
        previous = TaskStatus(data["previous"]) if data.get("previous") else None
        
        # Parse the timestamp
        last_updated = data.get("last_updated")
        if isinstance(last_updated, str):
            last_updated = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
        elif not last_updated:
            last_updated = datetime.utcnow()
        
        return cls(
            current=current,
            previous=previous,
            history=data.get("history", []),
            last_updated=last_updated,
        ) 