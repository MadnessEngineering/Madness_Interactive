#!/usr/bin/env python3.11
"""
Setup script for model API gateway.
This tool helps set up a gateway to manage multiple models with load balancing and caching.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from common import setup_env  # Import the common setup_env function

def check_requirements():
    """Check if required packages are installed."""
    required = ['fastapi', 'uvicorn', 'redis', 'python-dotenv', 'pydantic']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

def setup_env_gateway():
    """Setup environment for gateway."""
    env_string = """# Gateway Settings
GATEWAY_PORT=8000
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
MODELS=[
    {
        "name": "codellama",
        "url": "http://localhost:11434",
        "weight": 1.0,
        "timeout": 30,
        "max_tokens": 2048
    },
    {
        "name": "llama2",
        "url": "http://localhost:11435",
        "weight": 0.8,
        "timeout": 30,
        "max_tokens": 2048
    }
]
"""
    setup_env(env_string)  # Call the common setup_env function

def setup_gateway():
    """Setup the API gateway files."""
    # Create necessary directories
    Path("gateway").mkdir(exist_ok=True)
    
    # Create gateway implementation
    with open("gateway/main.py", "w") as f:
        f.write("""#!/usr/bin/env python3
import json
import os
import random
import time
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import httpx
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Model API Gateway")

# Initialize Redis
redis_client = redis.from_url(os.getenv("REDIS_URL"))
CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))

# Load model configurations
MODELS = json.loads(os.getenv("MODELS", "[]"))

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None

class ChatResponse(BaseModel):
    model: str
    choices: List[Dict]
    usage: Dict

def get_cache_key(request: ChatRequest) -> str:
    \"\"\"Generate cache key from request.\"\"\"
    return f"{request.model}:{str(request.messages)}:{request.temperature}"

def select_model_instance(model_name: str) -> Dict:
    \"\"\"Select model instance using weighted random selection.\"\"\"
    instances = [m for m in MODELS if m["name"] == model_name]
    if not instances:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    
    total_weight = sum(inst["weight"] for inst in instances)
    r = random.uniform(0, total_weight)
    
    for instance in instances:
        r -= instance["weight"]
        if r <= 0:
            return instance
    
    return instances[0]

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest) -> ChatResponse:
    # Check cache
    cache_key = get_cache_key(request)
    cached_response = redis_client.get(cache_key)
    if cached_response:
        return ChatResponse(**json.loads(cached_response))
    
    # Select model instance
    instance = select_model_instance(request.model)
    
    # Prepare request
    max_tokens = min(
        request.max_tokens or instance["max_tokens"],
        instance["max_tokens"]
    )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{instance['url']}/v1/chat/completions",
                json={
                    "model": instance["name"],
                    "messages": [m.dict() for m in request.messages],
                    "temperature": request.temperature,
                    "max_tokens": max_tokens
                },
                timeout=instance["timeout"]
            )
            response.raise_for_status()
            result = response.json()
            
            # Cache successful response
            redis_client.setex(
                cache_key,
                CACHE_TTL,
                json.dumps(result)
            )
            
            return ChatResponse(**result)
            
        except httpx.TimeoutException:
            # Try fallback model if available
            fallback_instances = [
                m for m in MODELS
                if m["name"] != instance["name"]
            ]
            if fallback_instances:
                instance = fallback_instances[0]
                response = await client.post(
                    f"{instance['url']}/v1/chat/completions",
                    json={
                        "model": instance["name"],
                        "messages": [m.dict() for m in request.messages],
                        "temperature": request.temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=instance["timeout"]
                )
                response.raise_for_status()
                return ChatResponse(**response.json())
            raise HTTPException(
                status_code=504,
                detail="Request timed out and no fallback available"
            )
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing request: {str(e)}"
            )

@app.get("/v1/models")
async def list_models() -> Dict[str, List[str]]:
    \"\"\"List available models.\"\"\"
    return {
        "models": list(set(m["name"] for m in MODELS))
    }

@app.get("/v1/health")
async def health_check() -> Dict[str, str]:
    \"\"\"Check gateway health.\"\"\"
    return {"status": "healthy"}
""")
    
    # Create Docker Compose file for Redis
    with open("docker-compose.yml", "w") as f:
        f.write("""version: '3'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
""")

def main():
    parser = argparse.ArgumentParser(description="Setup model API gateway")
    parser.add_argument("--port", type=int, default=8000,
                      help="Port for gateway server (default: 8000)")
    args = parser.parse_args()
    
    print("Setting up model API gateway...")
    
    # Check and install requirements
    check_requirements()
    
    # Setup environment
    setup_env_gateway()
    
    # Setup gateway
    setup_gateway()
    
    print(f"""
Setup complete! To run the gateway:

1. Start Redis:
   docker-compose up -d

2. Start the gateway:
   cd gateway && uvicorn main:app --host 0.0.0.0 --port {args.port}

The gateway provides:
- Load balancing across model instances
- Response caching with Redis
- Automatic fallback handling
- Health checking
- OpenAI-compatible API

API Endpoints:
- POST /v1/chat/completions - Chat completion endpoint
- GET /v1/models - List available models
- GET /v1/health - Health check

Features:
- Weighted load balancing
- Response caching
- Timeout handling
- Fallback models
- Request validation

Configuration:
- Edit .env file to:
  * Add/remove models
  * Adjust weights
  * Configure timeouts
  * Set cache TTL

Tips:
- Monitor Redis memory usage
- Adjust cache TTL based on needs
- Use health check for monitoring
- Configure proper timeouts
""")

if __name__ == "__main__":
    main() 
