#!/usr/bin/env python3.11
"""
Setup script for configuring OpenAI API proxy with local models.
This tool helps set up a proxy to route AI API calls through local models for content checking.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    required = ['openai', 'requests', 'python-dotenv']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

def setup_env():
    """Setup environment configuration."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("Creating .env file...")
        with open(env_path, "w") as f:
            f.write("""# Local Model Settings
LOCAL_MODEL_URL=http://localhost:11434/v1
OPENAI_API_BASE=http://localhost:8080/v1
OPENAI_API_KEY=dummy-key

# Proxy Settings
PROXY_PORT=8080
ALLOWED_MODELS=["gpt-3.5-turbo", "gpt-4"]
LOCAL_MODEL_NAME=codellama
""")
        print("Created .env file with default settings")
    else:
        print(".env file already exists")

def setup_proxy():
    """Setup the proxy server configuration."""
    proxy_dir = Path("proxy")
    proxy_dir.mkdir(exist_ok=True)
    
    # Create proxy server file
    with open(proxy_dir / "proxy_server.py", "w") as f:
        f.write("""#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import requests

load_dotenv()

app = Flask(__name__)
LOCAL_MODEL_URL = os.getenv("LOCAL_MODEL_URL")
ALLOWED_MODELS = eval(os.getenv("ALLOWED_MODELS", "[]"))
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "codellama")

@app.route("/v1/<path:path>", methods=["POST"])
def proxy(path):
    data = request.get_json()
    
    # Check content for secrets/sensitive info using local model
    if "messages" in data:
        check_response = requests.post(
            f"{LOCAL_MODEL_URL}/chat/completions",
            json={
                "model": LOCAL_MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "You are a content safety checker. Analyze the following content for potential secrets or sensitive information."},
                    {"role": "user", "content": str(data["messages"])}
                ]
            }
        )
        
        if "sensitive" in check_response.json().get("choices", [{}])[0].get("message", {}).get("content", "").lower():
            return jsonify({"error": "Content contains potential sensitive information"}), 400
    
    # Forward request to local model
    response = requests.post(
        f"{LOCAL_MODEL_URL}/{path}",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    return response.json()

if __name__ == "__main__":
    port = int(os.getenv("PROXY_PORT", 8080))
    app.run(host="0.0.0.0", port=port)
""")

def main():
    parser = argparse.ArgumentParser(description="Setup OpenAI API proxy for local model content checking")
    parser.add_argument("--port", type=int, default=8080, help="Port for proxy server (default: 8080)")
    parser.add_argument("--model", default="codellama", help="Local model to use (default: codellama)")
    args = parser.parse_args()
    
    print("Setting up OpenAI API proxy with local model content checking...")
    
    # Check and install requirements
    check_requirements()
    
    # Setup environment
    setup_env()
    
    # Setup proxy
    setup_proxy()
    
    print(f"""
Setup complete! To use the proxy:

1. Start your local model (e.g., Ollama):
   ollama run {args.model}

2. Start the proxy server:
   python proxy/proxy_server.py

3. Configure your OpenAI client to use the proxy:
   export OPENAI_API_BASE=http://localhost:{args.port}/v1
   export OPENAI_API_KEY=dummy-key

The proxy will now check content for sensitive information using your local model
before forwarding requests.
""")

if __name__ == "__main__":
    main() 
