"""
Omnispindle API Server

This module provides a FastAPI server for the Omnispindle distributed task system.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..task_queue import TaskQueue
from ..models.task import TaskStatus
from ..models.worker import WorkerStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("omnispindle_api")

# Initialize FastAPI app
app = FastAPI(
    title="Omnispindle API",
    description="API for the Omnispindle distributed task system",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task queue instance
task_queue = None


# Pydantic models for API requests and responses
class TaskSubmit(BaseModel):
    task_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 0
    timeout: Optional[int] = None
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    task_id: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: int
    status: str
    claimed_by: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    claimed_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    dependencies: List[str]
    timeout: int
    retry_count: int
    metadata: Dict[str, Any]


class TaskBatch(BaseModel):
    tasks: List[TaskSubmit]
    batch_mode: str = "parallel"  # "parallel" or "sequential"


class TaskBatchResponse(BaseModel):
    task_ids: List[str]


class WorkerSubmit(BaseModel):
    capabilities: List[str] = Field(default_factory=list)
    capacity: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)
    worker_id: Optional[str] = None
    heartbeat_interval: int = 30


class WorkerResponse(BaseModel):
    id: str
    capabilities: List[str]
    capacity: int
    status: str
    current_tasks: List[str]
    last_heartbeat: Optional[str] = None
    metadata: Dict[str, Any]


class WorkerHeartbeat(BaseModel):
    status: Optional[str] = None
    resources: Optional[Dict[str, Any]] = None


class WorkerTaskResult(BaseModel):
    result: Optional[Dict[str, Any]] = None


class WorkerTaskFailure(BaseModel):
    error: Optional[str] = None
    retry: bool = True


class QueueStats(BaseModel):
    task_count: int
    worker_count: int
    tasks_by_status: Dict[str, int]
    tasks_by_type: Dict[str, int]
    workers_by_status: Dict[str, int]
    metrics: Dict[str, Any]
    timestamp: str


# Dependency to get the task queue
def get_task_queue():
    if task_queue is None:
        raise HTTPException(status_code=500, detail="Task queue not initialized")
    return task_queue


# Routes
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health checks."""
    return {"status": "healthy", "service": "Omnispindle API"}


@app.post("/tasks", response_model=Dict[str, str], tags=["Tasks"])
async def submit_task(
    task_data: TaskSubmit,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Submit a task to the queue."""
    try:
        task_id = queue.submit_task(
            task_type=task_data.task_type,
            parameters=task_data.parameters,
            priority=task_data.priority,
            timeout=task_data.timeout,
            dependencies=task_data.dependencies,
            metadata=task_data.metadata,
            task_id=task_data.task_id,
        )
        return {"task_id": task_id}
    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(
    task_id: str,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Get task details."""
    try:
        task = queue.get_task(task_id)
        return task
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")


@app.get("/tasks", response_model=Dict[str, List[TaskResponse]], tags=["Tasks"])
async def list_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    queue: TaskQueue = Depends(get_task_queue)
):
    """List tasks with optional filtering."""
    try:
        tasks = queue.list_tasks(
            status=status,
            task_type=task_type,
            limit=limit,
            offset=offset,
        )
        return {"tasks": tasks}
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tasks/{task_id}/cancel", tags=["Tasks"])
async def cancel_task(
    task_id: str,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Cancel a task."""
    try:
        queue.cancel_task(task_id)
        return {"status": "success", "message": f"Task {task_id} cancelled"}
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tasks/batch", response_model=TaskBatchResponse, tags=["Tasks"])
async def submit_batch(
    batch_data: TaskBatch,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Submit a batch of tasks."""
    try:
        # Convert Pydantic models to dicts
        tasks = [task.model_dump() for task in batch_data.tasks]
        
        # Sequential or parallel batch mode
        if batch_data.batch_mode == "sequential":
            # Create dependencies for sequential execution
            task_ids = []
            prev_task_id = None
            
            for task_dict in tasks:
                # Add dependency to previous task
                if prev_task_id:
                    if "dependencies" not in task_dict:
                        task_dict["dependencies"] = []
                    task_dict["dependencies"].append(prev_task_id)
                
                # Submit task
                task_id = queue.submit_task(**task_dict)
                task_ids.append(task_id)
                prev_task_id = task_id
                
            return {"task_ids": task_ids}
        else:
            # Submit all tasks in parallel
            task_ids = []
            for task_dict in tasks:
                task_id = queue.submit_task(**task_dict)
                task_ids.append(task_id)
                
            return {"task_ids": task_ids}
    except Exception as e:
        logger.error(f"Error submitting batch: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/workers", response_model=Dict[str, str], tags=["Workers"])
async def register_worker(
    worker_data: WorkerSubmit,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Register a worker with the queue."""
    try:
        worker_id = queue.register_worker(
            capabilities=worker_data.capabilities,
            capacity=worker_data.capacity,
            metadata=worker_data.metadata,
            worker_id=worker_data.worker_id,
            heartbeat_interval=worker_data.heartbeat_interval,
        )
        return {"worker_id": worker_id}
    except Exception as e:
        logger.error(f"Error registering worker: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/workers/{worker_id}", response_model=WorkerResponse, tags=["Workers"])
async def get_worker(
    worker_id: str,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Get worker details."""
    try:
        worker = queue.get_worker(worker_id)
        return worker
    except Exception as e:
        logger.error(f"Error getting worker {worker_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Worker not found: {worker_id}")


@app.get("/workers", response_model=Dict[str, List[WorkerResponse]], tags=["Workers"])
async def list_workers(
    status: Optional[str] = None,
    capability: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    queue: TaskQueue = Depends(get_task_queue)
):
    """List workers with optional filtering."""
    try:
        workers = queue.list_workers(
            status=status,
            capability=capability,
            limit=limit,
            offset=offset,
        )
        return {"workers": workers}
    except Exception as e:
        logger.error(f"Error listing workers: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/workers/{worker_id}/heartbeat", tags=["Workers"])
async def worker_heartbeat(
    worker_id: str,
    heartbeat_data: WorkerHeartbeat,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Update worker heartbeat."""
    try:
        queue.worker_heartbeat(
            worker_id=worker_id,
            status=heartbeat_data.status,
            resources=heartbeat_data.resources,
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error updating heartbeat for worker {worker_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/workers/{worker_id}/claim", response_model=Optional[TaskResponse], tags=["Workers"])
async def claim_task(
    worker_id: str,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Claim a task for a worker."""
    try:
        task = queue.claim_task(worker_id)
        return task
    except Exception as e:
        logger.error(f"Error claiming task for worker {worker_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/workers/{worker_id}/tasks/{task_id}/start", tags=["Workers"])
async def start_task(
    worker_id: str,
    task_id: str,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Mark a task as started by a worker."""
    try:
        queue.start_task(worker_id, task_id)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error starting task {task_id} for worker {worker_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/workers/{worker_id}/tasks/{task_id}/complete", tags=["Workers"])
async def complete_task(
    worker_id: str,
    task_id: str,
    result_data: WorkerTaskResult,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Mark a task as completed by a worker."""
    try:
        queue.complete_task(worker_id, task_id, result_data.result)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error completing task {task_id} for worker {worker_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/workers/{worker_id}/tasks/{task_id}/fail", tags=["Workers"])
async def fail_task(
    worker_id: str,
    task_id: str,
    failure_data: WorkerTaskFailure,
    queue: TaskQueue = Depends(get_task_queue)
):
    """Mark a task as failed by a worker."""
    try:
        queue.fail_task(worker_id, task_id, failure_data.error, failure_data.retry)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error failing task {task_id} for worker {worker_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/stats", response_model=QueueStats, tags=["System"])
async def get_queue_stats(
    queue: TaskQueue = Depends(get_task_queue)
):
    """Get queue statistics."""
    try:
        stats = queue.get_queue_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting queue stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Server initialization function
def init_server(
    max_retries: int = 3,
    worker_timeout: int = 90,
    persistence_path: Optional[str] = None,
    load_from_persistence: bool = True,
) -> FastAPI:
    """
    Initialize the API server.
    
    Args:
        max_retries: Maximum number of retry attempts for failed tasks
        worker_timeout: Timeout for workers to be considered dead in seconds
        persistence_path: Optional path for persisting queue state
        load_from_persistence: Whether to load state from persistence path
    
    Returns:
        Initialized FastAPI application
    """
    global task_queue
    
    # Create task queue
    task_queue = TaskQueue(
        max_retries=max_retries,
        worker_timeout=worker_timeout,
        persistence_path=persistence_path,
    )
    
    # Load state if requested and path exists
    if load_from_persistence and persistence_path and os.path.exists(persistence_path):
        logger.info(f"Loading state from {persistence_path}")
        task_queue.load_state()
    
    logger.info("Omnispindle API server initialized")
    return app


# For running the server directly
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    max_retries = int(os.environ.get("OMNISPINDLE_MAX_RETRIES", "3"))
    worker_timeout = int(os.environ.get("OMNISPINDLE_WORKER_TIMEOUT", "90"))
    persistence_path = os.environ.get("OMNISPINDLE_PERSISTENCE_PATH")
    
    # Initialize server
    app = init_server(
        max_retries=max_retries,
        worker_timeout=worker_timeout,
        persistence_path=persistence_path,
    )
    
    # Start server
    uvicorn.run(
        app,
        host=os.environ.get("OMNISPINDLE_HOST", "0.0.0.0"),
        port=int(os.environ.get("OMNISPINDLE_PORT", "8000")),
    ) 