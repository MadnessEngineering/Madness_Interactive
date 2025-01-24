"""
Project Initialization Agent
An LM Studio agent that can help create and setup new projects
"""

import json
import subprocess
import sys
from pathlib import Path
from openai import OpenAI

# Initialize LM Studio client
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
MODEL = "qwen2.5-7b-instruct"

# Define project initialization tool
PROJECT_INIT_TOOL = {
    "type": "function",
    "function": {
        "name": "init_project",
        "description": (
            "Initialize a new project in the appropriate projects directory. "
            "This will create a new repository with proper structure and configuration."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the project (will be used as directory name)",
                },
                "project_type": {
                    "type": "string",
                    "enum": ["python", "rust", "common"],
                    "description": "Type of project to create",
                },
                "description": {
                    "type": "string",
                    "description": "Short description of the project",
                },
            },
            "required": ["name", "project_type", "description"],
        },
    },
}

def execute_project_init(name: str, project_type: str, description: str) -> dict:
    """Execute the project initialization script"""
    try:
        result = subprocess.run(
            [sys.executable, "project_init.py", name, project_type, description],
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            "status": "success",
            "message": result.stdout,
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Error initializing project: {e.stderr}",
        }

def main():
    """Main function to handle project initialization requests"""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that can create new project repositories. "
                "When asked to create a project, you will determine the appropriate "
                "project type (python/rust/common) based on the requirements and create "
                "a properly structured repository."
            ),
        }
    ]

    print(
        "Assistant: Hi! I can help you create new projects. Just tell me what kind of "
        "project you want to create and I'll set it up with the proper structure."
    )
    print("(Type 'quit' to exit)")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "quit":
            break

        messages.append({"role": "user", "content": user_input})
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=[PROJECT_INIT_TOOL],
            )

            if response.choices[0].message.tool_calls:
                tool_calls = response.choices[0].message.tool_calls
                messages.append(response.choices[0].message)

                for tool_call in tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    result = execute_project_init(
                        args["name"],
                        args["project_type"],
                        args["description"],
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "content": json.dumps(result),
                            "tool_call_id": tool_call.id,
                        }
                    )

                # Get final response after tool use
                final_response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                )
                print("\nAssistant:", final_response.choices[0].message.content)
                messages.append(final_response.choices[0].message)
            else:
                print("\nAssistant:", response.choices[0].message.content)
                messages.append(response.choices[0].message)

        except Exception as e:
            print(
                f"\nError communicating with LM Studio server!\n\n"
                f"Please ensure:\n"
                f"1. LM Studio server is running at 127.0.0.1:1234\n"
                f"2. Model '{MODEL}' is downloaded and loaded\n\n"
                f"Error details: {str(e)}"
            )
            sys.exit(1)

if __name__ == "__main__":
    main()
