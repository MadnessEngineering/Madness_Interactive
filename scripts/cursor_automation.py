#!/usr/bin/env python3
"""
Cursor Automation Helper Script

This script provides custom automations that work alongside Cursor IDE.
It can be triggered manually or via file watchers/git hooks.
"""

import os
import subprocess
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

class CursorAutomation:
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.cursor_rules_dir = self.workspace_root / ".cursor" / "rules"
        self.madness_root = Path("/Users/d.edens/lab/madness_interactive")
        
    def check_cursor_rules_centralization(self) -> Dict[str, Any]:
        """Check if cursor rules are centralized and suggest centralization if not"""
        result = {
            "is_centralized": False,
            "needs_centralization": False,
            "centralizer_available": False,
            "suggestions": []
        }
        
        # Check if cursor rules directory exists
        if not self.cursor_rules_dir.exists():
            result["suggestions"].append("No cursor rules directory found. Consider creating one.")
            return result
            
        # Check if it's a symbolic link (centralized)
        if self.cursor_rules_dir.is_symlink():
            result["is_centralized"] = True
            result["link_target"] = str(self.cursor_rules_dir.readlink())
            result["suggestions"].append("✅ Cursor rules are centralized!")
        else:
            result["needs_centralization"] = True
            result["suggestions"].append("📦 Cursor rules could be centralized for better management")
            
        # Check if centralizer script is available
        centralizer_script = self.madness_root / "scripts" / "cursor_rules_centralizer.zsh"
        if centralizer_script.exists():
            result["centralizer_available"] = True
            result["centralizer_path"] = str(centralizer_script)
            if result["needs_centralization"]:
                result["suggestions"].append(f"💡 Run: {centralizer_script} to centralize cursor rules")
                
        return result
        
    def auto_test_on_change(self, file_path: str) -> Dict[str, Any]:
        """Auto-run tests when specific files change"""
        file_path = Path(file_path)
        results = {"tests_run": [], "suggestions": []}
        
        if file_path.suffix == ".py":
            # Run Python tests
            test_file = file_path.parent / f"test_{file_path.stem}.py"
            if test_file.exists():
                result = subprocess.run(
                    ["python", "-m", "pytest", str(test_file), "-v"],
                    capture_output=True, text=True
                )
                results["tests_run"].append({
                    "file": str(test_file),
                    "passed": result.returncode == 0,
                    "output": result.stdout
                })
            else:
                results["suggestions"].append(f"Consider creating test file: {test_file}")
                
        elif file_path.suffix == ".rs":
            # Run Rust tests
            if (file_path.parent / "Cargo.toml").exists():
                result = subprocess.run(
                    ["cargo", "test"], 
                    cwd=file_path.parent, 
                    capture_output=True, text=True
                )
                results["tests_run"].append({
                    "type": "cargo_test",
                    "passed": result.returncode == 0,
                    "output": result.stdout
                })
                
        elif file_path.suffix == ".zsh" and "cursor" in file_path.name.lower():
            # Special handling for cursor automation scripts
            results["suggestions"].append("🔧 Mad Tinker script detected! Consider testing with a dry-run first.")
            
        return results
    
    def generate_commit_message(self, staged_files: List[str]) -> str:
        """Generate intelligent commit messages based on changed files"""
        if not staged_files:
            return "chore: minor updates"
            
        file_types = set(Path(f).suffix for f in staged_files)
        dirs = set(Path(f).parent.name for f in staged_files)
        
        # Check for Mad Tinker automation files
        mad_tinker_files = [f for f in staged_files if "cursor" in f.lower() and "script" in f.lower()]
        if mad_tinker_files:
            return "feat: enhance Mad Tinker automation capabilities 🔧⚡"
        
        # Analyze patterns
        if ".py" in file_types and any("test" in f for f in staged_files):
            return "test: update Python test coverage"
        elif ".rs" in file_types:
            return f"feat: update Rust components in {', '.join(dirs)}"
        elif ".md" in file_types:
            return "docs: update documentation"
        elif any("cursor" in f.lower() for f in staged_files):
            return "config: update Cursor IDE configuration"
        elif ".zsh" in file_types:
            return "feat: enhance shell automation scripts 🧙‍♂️"
        else:
            return f"feat: update {', '.join(dirs)} components"
    
    def create_todo_from_comments(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract TODO comments and create MCP todo items"""
        todos_found = []
        file_path = Path(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                if "TODO:" in line or "FIXME:" in line or "HACK:" in line or "MWAHAHAHA:" in line:
                    # Extract the todo text
                    todo_text = line.split("TODO:")[-1].split("FIXME:")[-1].split("HACK:")[-1].split("MWAHAHAHA:")[-1].strip()
                    todo_text = todo_text.lstrip("# ").lstrip("// ").strip()
                    
                    if todo_text:
                        priority = "High" if "FIXME:" in line else "Medium"
                        if "MWAHAHAHA:" in line:
                            priority = "High"
                            todo_text = f"🧙‍♂️ Mad Tinker Enhancement: {todo_text}"
                            
                        todos_found.append({
                            "description": f"{file_path.name}:{line_num} - {todo_text}",
                            "project": "Madness_interactive",
                            "priority": priority,
                            "metadata": {
                                "file": str(file_path),
                                "line": line_num,
                                "type": "code_comment"
                            }
                        })
                        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
        return todos_found
    
    def check_code_quality(self, file_path: str) -> Dict[str, Any]:
        """Run code quality checks"""
        file_path = Path(file_path)
        results = {"issues": [], "suggestions": []}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Check for common issues
            for line_num, line in enumerate(lines, 1):
                # Check line length
                if len(line.strip()) > 120:
                    results["issues"].append({
                        "line": line_num,
                        "type": "line_too_long",
                        "message": f"Line {line_num} exceeds 120 characters"
                    })
                
                # Check for potential security issues
                if any(danger in line.lower() for danger in ["eval(", "exec(", "os.system("]):
                    results["issues"].append({
                        "line": line_num,
                        "type": "security_risk",
                        "message": f"Potential security risk at line {line_num}"
                    })
                    
                # Check for Mad Tinker patterns (this is good!)
                if "MWAHAHAHA" in line or "Mad Tinker" in line:
                    results["suggestions"].append(f"🔧⚡ Mad Tinker energy detected at line {line_num}! Excellent!")
            
            # Check function complexity (simple heuristic)
            function_lines = 0
            in_function = False
            for line in lines:
                if line.strip().startswith("def ") or line.strip().startswith("fn "):
                    in_function = True
                    function_lines = 1
                elif in_function:
                    if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                        if function_lines > 50:
                            results["suggestions"].append(
                                "Consider breaking down large functions (>50 lines)"
                            )
                        in_function = False
                        function_lines = 0
                    else:
                        function_lines += 1
                        
        except Exception as e:
            results["issues"].append({"type": "error", "message": str(e)})
            
        return results
    
    def detect_mad_tinker_opportunities(self) -> Dict[str, Any]:
        """Detect opportunities for Mad Tinker automation enhancements"""
        opportunities = {
            "automation_suggestions": [],
            "centralization_opportunities": [],
            "script_enhancements": []
        }
        
        # Check for cursor rules centralization
        cursor_check = self.check_cursor_rules_centralization()
        if cursor_check["needs_centralization"]:
            opportunities["centralization_opportunities"].append(
                "Cursor rules can be centralized for better management"
            )
            
        # Check for common automation patterns
        if (self.workspace_root / "package.json").exists():
            opportunities["automation_suggestions"].append(
                "Node.js project detected - consider npm install automation"
            )
            
        if (self.workspace_root / "Cargo.toml").exists():
            opportunities["automation_suggestions"].append(
                "Rust project detected - consider cargo build/test automation"
            )
            
        if (self.workspace_root / "requirements.txt").exists():
            opportunities["automation_suggestions"].append(
                "Python project detected - consider pip install automation"
            )
            
        # Check for git hooks opportunities
        git_hooks_dir = self.workspace_root / ".git" / "hooks"
        if git_hooks_dir.exists():
            existing_hooks = list(git_hooks_dir.glob("*"))
            if not existing_hooks:
                opportunities["script_enhancements"].append(
                    "No git hooks detected - consider adding pre-commit automation"
                )
                
        return opportunities
    
    def run_automation_suite(self, trigger: str, file_path: str = None) -> Dict[str, Any]:
        """Run a full automation suite based on trigger"""
        results = {
            "trigger": trigger, 
            "timestamp": subprocess.check_output(["date"]).decode().strip(),
            "mad_tinker_signature": "🔧⚡ MWAHAHAHA! 🧙‍♂️"
        }
        
        if trigger == "file_change" and file_path:
            results["test_results"] = self.auto_test_on_change(file_path)
            results["quality_check"] = self.check_code_quality(file_path)
            results["todos_found"] = self.create_todo_from_comments(file_path)
            results["cursor_rules_status"] = self.check_cursor_rules_centralization()
            
        elif trigger == "pre_commit":
            # Get staged files
            staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"]).decode().strip()
            staged_files = staged.split('\n') if staged else []
            
            results["staged_files"] = staged_files
            results["suggested_commit_message"] = self.generate_commit_message(staged_files)
            
            # Run tests on all staged files
            results["test_results"] = []
            for file_path in staged_files:
                if Path(file_path).exists():  # File might be deleted
                    results["test_results"].append(self.auto_test_on_change(file_path))
                    
        elif trigger == "project_analysis":
            results["mad_tinker_opportunities"] = self.detect_mad_tinker_opportunities()
            results["cursor_rules_status"] = self.check_cursor_rules_centralization()
                    
        return results

def main():
    parser = argparse.ArgumentParser(description="Mad Tinker's Cursor Automation Helper 🔧⚡")
    parser.add_argument("trigger", choices=["file_change", "pre_commit", "post_commit", "project_analysis"])
    parser.add_argument("--file", help="File path for file_change trigger")
    parser.add_argument("--workspace", help="Workspace root directory")
    
    args = parser.parse_args()
    
    automation = CursorAutomation(args.workspace)
    results = automation.run_automation_suite(args.trigger, args.file)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main() 
