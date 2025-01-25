"""
Git Assistant
An LM Studio-powered tool for automated Git operations with intelligent commit messages
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Dict
from openai import OpenAI

# Initialize LM Studio client
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
MODEL = "qwen2.5-7b-instruct"

def get_git_diff() -> str:
    """Get the current git diff for staged changes"""
    try:
        # First check if there are any staged changes
        staged = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            check=True
        )
        if staged.stdout.strip():
            return staged.stdout

        # If no staged changes, get unstaged changes
        unstaged = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            check=True
        )
        return unstaged.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e.stderr}")
        sys.exit(1)

def create_branch(branch_name: str) -> None:
    """Create and checkout a new branch"""
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Created and switched to new branch: {branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating branch: {e.stderr}")
        sys.exit(1)

def stage_changes() -> None:
    """Stage all changes"""
    try:
        subprocess.run(
            ["git", "add", "."],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error staging changes: {e.stderr}")
        sys.exit(1)

def commit_changes(message: str) -> None:
    """Commit staged changes with the given message"""
    try:
        subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Changes committed with message: {message}")
    except subprocess.CalledProcessError as e:
        print(f"Error committing changes: {e.stderr}")
        sys.exit(1)

def merge_branch(target_branch: str = "main") -> None:
    """Merge current branch into target branch"""
    try:
        current_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()

        # Switch to target branch
        subprocess.run(
            ["git", "checkout", target_branch],
            capture_output=True,
            text=True,
            check=True
        )

        # Merge the feature branch
        subprocess.run(
            ["git", "merge", current_branch],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Successfully merged {current_branch} into {target_branch}")
    except subprocess.CalledProcessError as e:
        print(f"Error during merge: {e.stderr}")
        print("Please resolve conflicts manually")
        sys.exit(1)

def generate_commit_message(diff: str) -> str:
    """Generate a commit message using LM Studio based on the diff"""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that generates clear and concise git commit "
                "messages. You analyze git diffs and create conventional commit messages "
                "that follow best practices. Focus on describing WHAT changed and WHY, "
                "being specific but concise. Use the conventional commits format: "
                "type(scope): description"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Please generate a commit message for the following changes:\n\n{diff}"
            ),
        },
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating commit message: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Git Assistant - Automated Git Operations")
    parser.add_argument(
        "--new-branch",
        type=str,
        help="Create and switch to a new branch before committing",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge changes back to main branch after committing",
    )
    parser.add_argument(
        "--target-branch",
        type=str,
        default="main",
        help="Target branch for merge (default: main)",
    )
    parser.add_argument(
        "--message",
        type=str,
        help="Use a specific commit message instead of generating one",
    )
    args = parser.parse_args()

    # Create new branch if requested
    if args.new_branch:
        create_branch(args.new_branch)

    # Get the diff of changes
    diff = get_git_diff()
    if not diff:
        print("No changes detected!")
        sys.exit(0)

    # Stage all changes
    stage_changes()

    # Generate or use provided commit message
    commit_message = args.message
    if not commit_message:
        print("\nAnalyzing changes to generate commit message...")
        commit_message = generate_commit_message(diff)
        if not commit_message:
            print("Failed to generate commit message")
            sys.exit(1)

        print(f"\nGenerated commit message: {commit_message}")
        proceed = input("\nProceed with this commit message? [Y/n]: ").lower()
        if proceed and proceed != "y":
            print("Commit aborted")
            sys.exit(0)

    # Commit changes
    commit_changes(commit_message)

    # Merge if requested
    if args.merge:
        merge_branch(args.target_branch)

if __name__ == "__main__":
    main()
