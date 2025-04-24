#!/usr/bin/env python3
"""
Omnispindle Command Line Interface

This module provides a command-line interface for the Omnispindle task system.
"""

import os
import sys
import time
import logging
from typing import Optional, List

import click
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("omnispindle")


# CLI Group
@click.group()
@click.version_option()
@click.option(
    "--config",
    "-c",
    help="Path to configuration file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool, quiet: bool) -> None:
    """
    Omnispindle - Distributed Task Management Engine
    
    This tool helps manage and monitor the Omnispindle task system.
    """
    # Configure logging based on verbosity options
    if verbose:
        logger.setLevel(logging.DEBUG)
    elif quiet:
        logger.setLevel(logging.WARNING)
    
    # Initialize context object
    ctx.ensure_object(dict)
    ctx.obj["CONFIG_PATH"] = config
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["QUIET"] = quiet
    
    # Load configuration here if needed
    if config:
        # Placeholder for configuration loading
        logger.debug(f"Loading configuration from {config}")
        # ctx.obj["CONFIG"] = load_config(config)


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind the server to")
@click.option("--port", default=8000, help="Port to bind the server to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.option("--workers", default=1, help="Number of worker processes")
@click.pass_context
def serve(ctx: click.Context, host: str, port: int, reload: bool, workers: int) -> None:
    """Start the Omnispindle API server."""
    import uvicorn
    from omnispindle.api.server import create_app
    
    logger.info(f"Starting Omnispindle server on {host}:{port}")
    logger.info(f"Workers: {workers}, Reload: {reload}")
    
    # Create the FastAPI application
    app = create_app()
    
    # Start the server
    uvicorn.run(
        "omnispindle.api.server:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
    )


@cli.command()
@click.option("--broker-url", help="Redis broker URL", default="redis://localhost:6379/0")
@click.option("--concurrency", default=4, help="Number of concurrent tasks")
@click.option("--queues", help="Comma-separated list of queues to process", default="default")
@click.pass_context
def worker(ctx: click.Context, broker_url: str, concurrency: int, queues: str) -> None:
    """Start a worker process to execute tasks."""
    from omnispindle.workers.worker import Worker
    
    queue_list = [q.strip() for q in queues.split(',')]
    logger.info(f"Starting worker with concurrency {concurrency}")
    logger.info(f"Connecting to broker at {broker_url}")
    logger.info(f"Processing queues: {', '.join(queue_list)}")
    
    # Initialize and start worker
    worker = Worker(
        broker_url=broker_url,
        concurrency=concurrency,
        queues=queue_list,
    )
    
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Shutting down worker...")
        worker.stop()
        sys.exit(0)


@cli.command()
@click.argument("task_name")
@click.option("--payload", "-p", help="JSON payload for the task")
@click.option("--priority", default="normal", help="Task priority (low, normal, high, critical)")
@click.option("--queue", default="default", help="Queue to submit the task to")
@click.option("--wait", is_flag=True, help="Wait for task completion")
@click.pass_context
def submit(
    ctx: click.Context,
    task_name: str,
    payload: Optional[str],
    priority: str,
    queue: str,
    wait: bool,
) -> None:
    """Submit a task to the Omnispindle system."""
    import json
    from omnispindle.api.client import TaskClient
    
    # Parse the payload if provided
    task_payload = {}
    if payload:
        try:
            task_payload = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
            sys.exit(1)
    
    # Get API URL from environment or use default
    api_url = os.environ.get("OMNISPINDLE_API_URL", "http://localhost:8000")
    
    # Create client and submit task
    client = TaskClient(api_url)
    logger.info(f"Submitting task '{task_name}' to queue '{queue}' with priority '{priority}'")
    
    try:
        task = client.create_task(
            name=task_name,
            payload=task_payload,
            priority=priority,
            queue=queue,
        )
        logger.info(f"Task submitted with ID: {task.id}")
        
        if wait:
            logger.info("Waiting for task to complete...")
            while True:
                status = client.get_task_status(task.id)
                logger.info(f"Task status: {status}")
                if status in ["completed", "failed", "cancelled"]:
                    break
                time.sleep(1)
    except Exception as e:
        logger.error(f"Error submitting task: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("task_id")
@click.pass_context
def status(ctx: click.Context, task_id: str) -> None:
    """Get the status of a task."""
    from omnispindle.api.client import TaskClient
    
    # Get API URL from environment or use default
    api_url = os.environ.get("OMNISPINDLE_API_URL", "http://localhost:8000")
    
    # Create client and get task status
    client = TaskClient(api_url)
    
    try:
        status = client.get_task_status(task_id)
        result = client.get_task_result(task_id)
        logger.info(f"Task {task_id}:")
        logger.info(f"  Status: {status}")
        if result:
            logger.info(f"  Result: {result}")
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("task_id")
@click.pass_context
def cancel(ctx: click.Context, task_id: str) -> None:
    """Cancel a task."""
    from omnispindle.api.client import TaskClient
    
    # Get API URL from environment or use default
    api_url = os.environ.get("OMNISPINDLE_API_URL", "http://localhost:8000")
    
    # Create client and cancel task
    client = TaskClient(api_url)
    
    try:
        client.cancel_task(task_id)
        logger.info(f"Task {task_id} cancelled successfully")
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option("--status", help="Filter by task status")
@click.option("--queue", help="Filter by queue")
@click.option("--limit", default=10, help="Maximum number of tasks to list")
@click.pass_context
def list(ctx: click.Context, status: Optional[str], queue: Optional[str], limit: int) -> None:
    """List tasks in the system."""
    from omnispindle.api.client import TaskClient
    
    # Get API URL from environment or use default
    api_url = os.environ.get("OMNISPINDLE_API_URL", "http://localhost:8000")
    
    # Create client and list tasks
    client = TaskClient(api_url)
    
    try:
        filters = {}
        if status:
            filters["status"] = status
        if queue:
            filters["queue"] = queue
        
        tasks = client.query_tasks(filters=filters, limit=limit)
        
        if not tasks:
            logger.info("No tasks found matching criteria")
            return
        
        for task in tasks:
            logger.info(f"Task {task.id}:")
            logger.info(f"  Name: {task.name}")
            logger.info(f"  Status: {task.status}")
            logger.info(f"  Queue: {task.queue}")
            logger.info(f"  Priority: {task.priority}")
            logger.info(f"  Created: {task.created_at}")
            logger.info(f"  Updated: {task.updated_at}")
            logger.info("-" * 40)
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 