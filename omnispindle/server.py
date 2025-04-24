"""
Omnispindle Server

This module provides a simple command-line interface to run the Omnispindle API server.
"""

import os
import sys
import logging
import argparse
from typing import Optional

import uvicorn

from .api.server import init_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("omnispindle_server")


def main():
    """Run the Omnispindle API server."""
    parser = argparse.ArgumentParser(description="Run the Omnispindle API server.")
    
    parser.add_argument(
        "--host", 
        default=os.environ.get("OMNISPINDLE_HOST", "0.0.0.0"),
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port", 
        type=int,
        default=int(os.environ.get("OMNISPINDLE_PORT", "8000")),
        help="Port to bind the server to (default: 8000)"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=int(os.environ.get("OMNISPINDLE_MAX_RETRIES", "3")),
        help="Maximum number of retry attempts for failed tasks (default: 3)"
    )
    
    parser.add_argument(
        "--worker-timeout",
        type=int,
        default=int(os.environ.get("OMNISPINDLE_WORKER_TIMEOUT", "90")),
        help="Timeout for workers to be considered dead in seconds (default: 90)"
    )
    
    parser.add_argument(
        "--persistence-path",
        default=os.environ.get("OMNISPINDLE_PERSISTENCE_PATH"),
        help="Path for persisting queue state (default: None)"
    )
    
    parser.add_argument(
        "--no-load-state",
        action="store_true",
        help="Don't load state from persistence path on startup"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=os.environ.get("OMNISPINDLE_LOG_LEVEL", "INFO"),
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Initialize the server
    logger.info(f"Initializing Omnispindle server with max_retries={args.max_retries}, worker_timeout={args.worker_timeout}s")
    if args.persistence_path:
        logger.info(f"Using persistence path: {args.persistence_path}")
        
    app = init_server(
        max_retries=args.max_retries,
        worker_timeout=args.worker_timeout,
        persistence_path=args.persistence_path,
        load_from_persistence=not args.no_load_state,
    )
    
    # Start the server
    logger.info(f"Starting Omnispindle server on {args.host}:{args.port}")
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main() 