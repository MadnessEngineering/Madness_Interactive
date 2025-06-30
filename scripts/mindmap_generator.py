#!/usr/bin/env python3
"""
Madness Interactive Mind Map Generator
=====================================

Generate beautiful mind maps from the project structure to help visualize
and navigate the growing ecosystem of projects.

Usage:
    python mindmap_generator.py [options]
    
Options:
    --format html|svg|dot|json  Output format (default: html)
    --output FILE               Output file (default: mindmap.html)
    --depth N                   Maximum depth to scan (default: 3)
    --style tech|hierarchical   Mind map style (default: tech)
    --interactive               Add interactive features (HTML only)
    --exclude PATTERN           Exclude directories matching pattern
    --include-todos             Include todo information in mindmap
    --include-todo-items        Include individual todo items as nodes (top 5 projects only)
    --todo-centric              Generate todo-centric mindmap focusing on active projects from database
    
Examples:
    python mindmap_generator.py --format html --interactive --include-todos
    python mindmap_generator.py --format html --include-todo-items
    python mindmap_generator.py --todo-centric --format html --interactive  # Shows only active todos
    python mindmap_generator.py --format svg --style hierarchical
    python mindmap_generator.py --format dot --depth 2
"""

import os
import json
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Try to import MCP todo server functionality
try:
    # Import MongoDB functionality if available
    import pymongo
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
    
    # Get MongoDB connection details
    MONGO_HOST = os.getenv('AWSIP', 'localhost')
    MONGO_PORT = 27017
    MONGO_DB = 'swarmonomicon'  # Updated database name
    MONGO_COLLECTION = 'todos'  # Updated collection name
    
except ImportError as e:
    MONGO_AVAILABLE = False
    print(f"Warning: MongoDB functionality not available: {e}")
    print("Mindmap will generate without todo data.")
    print("To enable todo integration, install pymongo: pip install pymongo")

@dataclass
class TodoSummary:
    """Summary of todos for a project"""
    total: int = 0
    initial: int = 0
    pending: int = 0
    completed: int = 0
    high_priority: int = 0
    medium_priority: int = 0
    low_priority: int = 0
    recent_todos: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.recent_todos is None:
            self.recent_todos = []

@dataclass
class ProjectNode:
    """Represents a project node in the mind map"""
    name: str
    path: str
    type: str  # 'category', 'project', 'file'
    language: str = ""
    description: str = ""
    children: List['ProjectNode'] = None
    metadata: Dict[str, Any] = None
    todo_summary: Optional[TodoSummary] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}

class TodoIntegration:
    """Handles todo data integration with mindmap"""
    
    def __init__(self):
        self.mongo_available = MONGO_AVAILABLE
    
    def get_project_todos(self, project_name: str) -> TodoSummary:
        """Get todo summary for a specific project"""
        if not self.mongo_available:
            return TodoSummary()
        
        try:
            # Connect to MongoDB
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            
            # Query todos for this project
            todos_cursor = collection.find({"project": project_name})
            
            summary = TodoSummary()
            for todo in todos_cursor:
                summary.total += 1
                
                # Count by status
                status = todo.get('status', 'initial')
                if status == 'initial':
                    summary.initial += 1
                elif status == 'pending':
                    summary.pending += 1
                elif status == 'completed':
                    summary.completed += 1
                
                # Count by priority
                priority = todo.get('priority', 'medium').lower()
                if priority == 'high':
                    summary.high_priority += 1
                elif priority == 'medium':
                    summary.medium_priority += 1
                elif priority == 'low':
                    summary.low_priority += 1
                
                # Keep recent todos (limit to 5)
                if len(summary.recent_todos) < 5:
                    summary.recent_todos.append({
                        'id': str(todo.get('_id', '')),
                        'description': todo.get('description', '')[:100] + ('...' if len(todo.get('description', '')) > 100 else ''),
                        'status': status,
                        'priority': priority
                    })
            
            client.close()
            return summary
            
        except Exception as e:
            print(f"Warning: Error fetching todos for project {project_name}: {e}")
            return TodoSummary()
    
    def get_all_project_todos(self) -> Dict[str, TodoSummary]:
        """Get todo summaries for all projects"""
        if not self.mongo_available:
            return {}
        
        try:
            # Connect to MongoDB
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            
            # Get all todos
            todos_cursor = collection.find({})
            
            project_summaries = {}
            for todo in todos_cursor:
                project = todo.get('project', 'unknown')
                if project not in project_summaries:
                    project_summaries[project] = TodoSummary()
                
                summary = project_summaries[project]
                summary.total += 1
                
                # Count by status
                status = todo.get('status', 'initial')
                if status == 'initial':
                    summary.initial += 1
                elif status == 'pending':
                    summary.pending += 1
                elif status == 'completed':
                    summary.completed += 1
                
                # Count by priority
                priority = todo.get('priority', 'medium').lower()
                if priority == 'high':
                    summary.high_priority += 1
                elif priority == 'medium':
                    summary.medium_priority += 1
                elif priority == 'low':
                    summary.low_priority += 1
                
                # Keep recent todos (limit to 3 per project)
                if len(summary.recent_todos) < 3:
                    summary.recent_todos.append({
                        'id': str(todo.get('_id', '')),
                        'description': todo.get('description', '')[:80] + ('...' if len(todo.get('description', '')) > 80 else ''),
                        'status': status,
                        'priority': priority
                    })
            
            client.close()
            return project_summaries
            
        except Exception as e:
            print(f"Warning: Error fetching all todos: {e}")
            return {}

    def get_top_projects_by_todo_count(self, limit: int = 5) -> List[str]:
        """Get the top N projects by todo count"""
        if not self.mongo_available:
            return []
        
        try:
            # Connect to MongoDB
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            
            # Aggregate to get project todo counts
            pipeline = [
                {"$group": {"_id": "$project", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]
            
            top_projects = []
            for result in collection.aggregate(pipeline):
                if result['_id']:  # Skip null/empty project names
                    top_projects.append(result['_id'])
            
            client.close()
            return top_projects
            
        except Exception as e:
            print(f"Warning: Error fetching top projects: {e}")
            return []
    
    def get_project_todo_items(self, project_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get individual todo items for a specific project (excluding completed)"""
        if not self.mongo_available:
            return []
        
        try:
            # Connect to MongoDB
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            
            # Query todos for this project, excluding completed ones
            query = {
                "project": project_name,
                "status": {"$ne": "completed"}  # Exclude completed todos
            }
            
            todos_cursor = collection.find(query).limit(limit)
            
            todo_items = []
            for todo in todos_cursor:
                todo_items.append({
                    'id': str(todo.get('_id', '')),
                    'description': todo.get('description', 'Untitled todo'),
                    'status': todo.get('status', 'initial'),
                    'priority': todo.get('priority', 'medium').lower(),
                    'created_at': todo.get('created_at', ''),
                    'updated_at': todo.get('updated_at', '')
                })
            
            # Sort by priority then by status (initial first, then pending)
            status_order = {"initial": 1, "pending": 2}
            priority_order = {"high": 1, "medium": 2, "low": 3}
            todo_items.sort(key=lambda x: (
                priority_order.get(x['priority'], 2),
                status_order.get(x['status'], 1)
            ))
            
            client.close()
            return todo_items
            
        except Exception as e:
            print(f"Warning: Error fetching todo items for project {project_name}: {e}")
            return []

    def get_active_project_todos(self) -> Dict[str, TodoSummary]:
        """Get todo summaries for all projects (excluding completed todos for active counts)"""
        if not self.mongo_available:
            return {}
        
        try:
            # Connect to MongoDB
            client = MongoClient(MONGO_HOST, MONGO_PORT)
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            
            # Get all non-completed todos
            todos_cursor = collection.find({"status": {"$ne": "completed"}})
            
            project_summaries = {}
            for todo in todos_cursor:
                project = todo.get('project', 'unknown')
                if project not in project_summaries:
                    project_summaries[project] = TodoSummary()
                
                summary = project_summaries[project]
                summary.total += 1
                
                # Count by status (only initial and pending now)
                status = todo.get('status', 'initial')
                if status == 'initial':
                    summary.initial += 1
                elif status == 'pending':
                    summary.pending += 1
                
                # Count by priority
                priority = todo.get('priority', 'medium').lower()
                if priority == 'high':
                    summary.high_priority += 1
                elif priority == 'medium':
                    summary.medium_priority += 1
                elif priority == 'low':
                    summary.low_priority += 1
                
                # Keep recent todos (limit to 3 per project)
                if len(summary.recent_todos) < 3:
                    summary.recent_todos.append({
                        'id': str(todo.get('_id', '')),
                        'description': todo.get('description', '')[:80] + ('...' if len(todo.get('description', '')) > 80 else ''),
                        'status': status,
                        'priority': priority
                    })
            
            client.close()
            return project_summaries
            
        except Exception as e:
            print(f"Warning: Error fetching active todos: {e}")
            return {}

class MindMapGenerator:
    """Generate mind maps from project structure"""

    def __init__(self, root_path: str = ".", include_todos: bool = False, include_todo_items: bool = False):
        self.root_path = Path(root_path).resolve()
        self.projects_path = self.root_path / "projects"
        self.include_todos = include_todos
        self.include_todo_items = include_todo_items
        self.todo_integration = None
        self.top_todo_projects = []

        # Initialize todo integration if requested
        if include_todos or include_todo_items:
            self.todo_integration = TodoIntegration()
            
            # Get top projects if we're including individual todo items
            if include_todo_items and self.todo_integration:
                self.top_todo_projects = self.todo_integration.get_top_projects_by_todo_count(5)

        # Language/technology mappings
        self.language_map = {
            'python': {'color': '#3776ab', 'icon': '🐍'},
            'rust': {'color': '#dea584', 'icon': '🦀'},
            'typescript': {'color': '#3178c6', 'icon': '📘'},
            'javascript': {'color': '#f7df1e', 'icon': '📜'},
            'lua': {'color': '#000080', 'icon': '🌙'},
            'mobile': {'color': '#a4c639', 'icon': '📱'},
            'tasker': {'color': '#ff6b35', 'icon': '⚙️'},
            'powershell': {'color': '#012456', 'icon': '💻'},
            'nodeJS': {'color': '#339933', 'icon': '🟢'},
            'OS': {'color': '#666666', 'icon': '🖥️'},
            'common': {'color': '#8b4513', 'icon': '🏛️'},
        }

        # Project categorization patterns
        self.category_patterns = {
            'AI/ML': ['ai', 'ml', 'scry', 'omnispindle', 'swarm'],
            'MCP': ['mcp', 'server', 'fastmcp'],
            'Automation': ['automation', 'tasker', 'mqtt', 'eventghost'],
            'Tools': ['utils', 'kit', 'cli', 'tool'],
            'Games': ['game', 'legends', 'raid'],
            'Web': ['web', 'html', 'server', 'api'],
            'Testing': ['test', 'pytest', 'kit'],
            'Communication': ['mqtt', 'conduit', 'bridge'],
        }

    def scan_projects(self, max_depth: int = 3, exclude_patterns: List[str] = None) -> ProjectNode:
        """Scan the projects directory and build the project tree"""
        exclude_patterns = exclude_patterns or [r'\.git', r'__pycache__', r'\.pytest_cache',
                                               r'node_modules', r'\.DS_Store', r'\.specstory']

        # Get all todo summaries if todo integration is enabled
        project_todos = {}
        if self.include_todos and self.todo_integration:
            project_todos = self.todo_integration.get_all_project_todos()

        root_node = ProjectNode(
            name="Madness Interactive",
            path=str(self.root_path),
            type="root",
            description="A Mad Tinker's AI Project Hub",
            metadata={
                'scan_time': datetime.now().isoformat(),
                'total_projects': 0,
                'languages': set(),
                'todo_enabled': self.include_todos,
                'total_todos': sum(summary.total for summary in project_todos.values()) if project_todos else 0
            }
        )

        if not self.projects_path.exists():
            return root_node

        # Scan by language/technology categories
        for lang_dir in self.projects_path.iterdir():
            if not lang_dir.is_dir() or self._should_exclude(lang_dir.name, exclude_patterns):
                continue

            lang_node = self._scan_language_category(lang_dir, max_depth - 1, exclude_patterns, project_todos)
            if lang_node.children:  # Only add if it has projects
                root_node.children.append(lang_node)
                root_node.metadata['languages'].add(lang_node.language)

        # Convert set to list for JSON serialization
        root_node.metadata['languages'] = list(root_node.metadata['languages'])
        root_node.metadata['total_projects'] = self._count_projects(root_node)

        return root_node

    def _scan_language_category(self, lang_path: Path, max_depth: int, exclude_patterns: List[str], project_todos: Dict[str, TodoSummary]) -> ProjectNode:
        """Scan a language category directory"""
        lang_name = lang_path.name
        lang_info = self.language_map.get(lang_name, {'color': '#666666', 'icon': '📁'})

        lang_node = ProjectNode(
            name=lang_name.title(),
            path=str(lang_path),
            type="category",
            language=lang_name,
            description=f"{lang_name.title()} projects",
            metadata={
                'color': lang_info['color'],
                'icon': lang_info['icon'],
                'project_count': 0
            }
        )

        if max_depth <= 0:
            return lang_node

        # Aggregate todo summary for this language category
        category_todo_summary = TodoSummary()

        # Scan projects in this language category
        for project_path in lang_path.iterdir():
            if not project_path.is_dir() or self._should_exclude(project_path.name, exclude_patterns):
                continue

            project_node = self._scan_project(project_path, max_depth - 1, exclude_patterns, lang_name, project_todos)
            if project_node:
                lang_node.children.append(project_node)
                lang_node.metadata['project_count'] += 1

                # Aggregate todos for this category
                if project_node.todo_summary:
                    category_todo_summary.total += project_node.todo_summary.total
                    category_todo_summary.initial += project_node.todo_summary.initial
                    category_todo_summary.pending += project_node.todo_summary.pending
                    category_todo_summary.completed += project_node.todo_summary.completed
                    category_todo_summary.high_priority += project_node.todo_summary.high_priority
                    category_todo_summary.medium_priority += project_node.todo_summary.medium_priority
                    category_todo_summary.low_priority += project_node.todo_summary.low_priority

        # Assign aggregated todo summary to language category
        lang_node.todo_summary = category_todo_summary

        return lang_node

    def _scan_project(self, project_path: Path, max_depth: int, exclude_patterns: List[str], language: str, project_todos: Dict[str, TodoSummary]) -> ProjectNode:
        """Scan an individual project"""
        project_name = project_path.name

        # Try to get project description from README or other sources
        description = self._get_project_description(project_path)
        category = self._categorize_project(project_name, description)

        project_node = ProjectNode(
            name=project_name,
            path=str(project_path),
            type="project",
            language=language,
            description=description,
            metadata={
                'category': category,
                'has_readme': (project_path / 'README.md').exists(),
                'has_config': self._has_config_files(project_path),
                'last_modified': self._get_last_modified(project_path),
                'size_estimate': self._estimate_project_size(project_path)
            },
            todo_summary=project_todos.get(project_name, TodoSummary())
        )

        # Optionally scan subdirectories for major components
        if max_depth > 0:
            for subdir in project_path.iterdir():
                if (subdir.is_dir() and
                    not self._should_exclude(subdir.name, exclude_patterns) and
                    subdir.name in ['src', 'lib', 'components', 'modules', 'tools']):

                    sub_node = ProjectNode(
                        name=subdir.name,
                        path=str(subdir),
                        type="component",
                        language=language,
                        description=f"{subdir.name} directory"
                    )
                    project_node.children.append(sub_node)

        # Add individual todo items as child nodes for top projects
        if self.include_todo_items and project_name in self.top_todo_projects and self.todo_integration:
            todo_items = self.todo_integration.get_project_todo_items(project_name, 10)
            for todo_item in todo_items:
                # Truncate description for better display
                description = todo_item['description']
                if len(description) > 60:
                    description = description[:57] + "..."
                
                todo_node = ProjectNode(
                    name=f"📋 {description}",
                    path="",  # Todos don't have file paths
                    type="todo",
                    language=language,
                    description=todo_item['description'],
                    metadata={
                        'todo_id': todo_item['id'],
                        'status': todo_item['status'],
                        'priority': todo_item['priority'],
                        'created_at': todo_item['created_at'],
                        'updated_at': todo_item['updated_at'],
                        'priority_color': {
                            'high': '#ff4757',
                            'medium': '#ffa502', 
                            'low': '#2ed573'
                        }.get(todo_item['priority'], '#ffa502'),
                        'status_color': {
                            'initial': '#5352ed',
                            'pending': '#ffa502',
                            'completed': '#2ed573'
                        }.get(todo_item['status'], '#5352ed')
                    }
                )
                project_node.children.append(todo_node)

        return project_node

    def _should_exclude(self, name: str, patterns: List[str]) -> bool:
        """Check if a directory should be excluded"""
        for pattern in patterns:
            if re.search(pattern, name):
                return True
        return False

    def _get_project_description(self, project_path: Path) -> str:
        """Try to extract project description from various sources"""
        # Try README files
        for readme_name in ['README.md', 'README.rst', 'README.txt', 'README']:
            readme_path = project_path / readme_name
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8')
                    # Extract first meaningful line
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and len(line) > 10:
                            return line[:100] + ('...' if len(line) > 100 else '')
                except:
                    pass

        # Try package.json for Node.js projects
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                if 'description' in data:
                    return data['description']
            except:
                pass

        # Try setup.py for Python projects
        setup_py = project_path / 'setup.py'
        if setup_py.exists():
            try:
                content = setup_py.read_text()
                # Simple regex to find description
                match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
            except:
                pass

        return f"Project in {project_path.parent.name}"

    def _categorize_project(self, name: str, description: str) -> str:
        """Categorize a project based on name and description"""
        text = (name + ' ' + description).lower()

        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return category

        return "Other"

    def _has_config_files(self, project_path: Path) -> bool:
        """Check if project has common config files"""
        config_files = [
            'package.json', 'setup.py', 'pyproject.toml', 'Cargo.toml',
            'requirements.txt', 'environment.yml', 'Dockerfile',
            '.env', 'config.json', 'config.yml'
        ]

        return any((project_path / cf).exists() for cf in config_files)

    def _get_last_modified(self, project_path: Path) -> str:
        """Get last modification time of the project"""
        try:
            # Get the most recent modification time in the project
            latest = max(p.stat().st_mtime for p in project_path.rglob('*') if p.is_file())
            return datetime.fromtimestamp(latest).isoformat()
        except:
            return datetime.now().isoformat()

    def _estimate_project_size(self, project_path: Path) -> str:
        """Estimate project size"""
        try:
            total_size = sum(p.stat().st_size for p in project_path.rglob('*') if p.is_file())
            if total_size < 1024:
                return f"{total_size}B"
            elif total_size < 1024**2:
                return f"{total_size/1024:.1f}KB"
            elif total_size < 1024**3:
                return f"{total_size/1024**2:.1f}MB"
            else:
                return f"{total_size/1024**3:.1f}GB"
        except:
            return "Unknown"

    def _count_projects(self, node: ProjectNode) -> int:
        """Count total number of projects in the tree"""
        count = 1 if node.type == "project" else 0
        for child in node.children:
            count += self._count_projects(child)
        return count

    def generate_html(self, root_node: ProjectNode, output_file: str, interactive: bool = True) -> None:
        """Generate an interactive HTML mind map"""

        # Calculate todo statistics
        total_todos = root_node.metadata.get('total_todos', 0)
        todo_enabled = root_node.metadata.get('todo_enabled', False)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Madness Interactive - Project Mind Map</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .stat {{
            text-align: center;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        #mindmap {{
            width: 100%;
            height: 600px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .node {{
            cursor: pointer;
            filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3));
        }}
        
        .node circle {{
            stroke: white;
            stroke-width: 2px;
        }}
        
        .node text {{
            font-size: 12px;
            fill: white;
            text-anchor: middle;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        }}
        
        .node.todo text {{
            font-size: 10px;
            text-anchor: start;
        }}
        
        .node.todo circle {{
            stroke-width: 1px;
        }}
        
        .link {{
            fill: none;
            stroke: rgba(255, 255, 255, 0.3);
            stroke-width: 2px;
        }}
        
        .link.todo {{
            stroke: rgba(255, 255, 255, 0.2);
            stroke-width: 1px;
            stroke-dasharray: 2,2;
        }}
        
        /* Todo badge styles */
        .todo-badge {{
            pointer-events: none;
        }}
        
        .todo-badge circle {{
            fill: #ff4757;
            stroke: white;
            stroke-width: 1px;
        }}
        
        .todo-badge text {{
            fill: white;
            font-size: 10px;
            font-weight: bold;
            text-anchor: middle;
            dominant-baseline: central;
        }}
        
        .priority-high {{ fill: #ff4757; }}
        .priority-medium {{ fill: #ffa502; }}
        .priority-low {{ fill: #2ed573; }}
        .status-initial {{ fill: #5352ed; }}
        .status-pending {{ fill: #ffa502; }}
        .status-completed {{ fill: #2ed573; }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            max-width: 300px;
            pointer-events: none;
            z-index: 1000;
        }}
        
        .tooltip h4 {{
            margin: 0 0 5px 0;
            color: #ffa502;
        }}
        
        .todo-item {{
            margin: 3px 0;
            padding: 2px 5px;
            border-radius: 3px;
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .controls {{
            text-align: center;
            margin: 20px 0;
        }}
        
        .controls button {{
            margin: 0 10px;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 5px;
            color: white;
            cursor: pointer;
            transition: background 0.3s;
        }}
        
        .controls button:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        
        .controls button.active {{
            background: rgba(255, 255, 255, 0.4);
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 15px;
            margin: 20px 0;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 5px 10px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            font-size: 0.9em;
        }}
        
        .legend-icon {{
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Madness Interactive Mind Map</h1>
            <p>A Mad Tinker's AI Project Hub Visualization</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-number">{root_node.metadata.get('total_projects', 0)}</span>
                <span class="stat-label">Projects</span>
            </div>
            <div class="stat">
                <span class="stat-number">{len(root_node.metadata.get('languages', []))}</span>
                <span class="stat-label">Technologies</span>
            </div>
            <div class="stat">
                <span class="stat-number">{len(root_node.children)}</span>
                <span class="stat-label">Categories</span>
            </div>
            {f'''<div class="stat">
                <span class="stat-number">{total_todos}</span>
                <span class="stat-label">Active Todos</span>
            </div>''' if todo_enabled else ''}
        </div>
        
        <div class="legend">
            {self._generate_legend_html(root_node)}
        </div>
        
        {"<div class='controls'><button onclick='expandAll()'>Expand All</button><button onclick='collapseAll()'>Collapse All</button><button onclick='resetView()'>Reset View</button>" + ("<button id='todoToggle' onclick='toggleTodos()'>Toggle Todos</button>" if todo_enabled else "") + "</div>" if interactive else ""}
        
        <div id="mindmap"></div>
    </div>
    
    <div class="tooltip" id="tooltip" style="display: none;"></div>
    
    <script>
        const data = {json.dumps(self._node_to_dict(root_node), indent=2)};
        let showTodos = {str(todo_enabled).lower()};
        {self._generate_d3_script(interactive)}
    </script>
</body>
</html>"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✨ Interactive HTML mind map generated: {output_file}")

    def _generate_legend_html(self, root_node: ProjectNode) -> str:
        """Generate HTML for the legend"""
        legend_items = []

        for child in root_node.children:
            if child.type == "category":
                icon = child.metadata.get('icon', '📁')
                legend_items.append(f'''
                    <div class="legend-item">
                        <span class="legend-icon">{icon}</span>
                        <span>{child.name} ({child.metadata.get('project_count', 0)})</span>
                    </div>
                ''')

        return ''.join(legend_items)

    def _node_to_dict(self, node: ProjectNode) -> Dict:
        """Convert ProjectNode to dictionary for JSON serialization"""
        result = {
            'name': node.name,
            'type': node.type,
            'language': node.language,
            'description': node.description,
            'metadata': node.metadata,
            'children': [self._node_to_dict(child) for child in node.children]
        }

        # Include todo summary if present
        if node.todo_summary:
            result['todo_summary'] = {
                'total': node.todo_summary.total,
                'initial': node.todo_summary.initial,
                'pending': node.todo_summary.pending,
                'completed': node.todo_summary.completed,
                'high_priority': node.todo_summary.high_priority,
                'medium_priority': node.todo_summary.medium_priority,
                'low_priority': node.todo_summary.low_priority,
                'recent_todos': node.todo_summary.recent_todos
            }

        return result

    def _generate_d3_script(self, interactive: bool) -> str:
        """Generate D3.js script for the mind map"""
        return f"""
        const width = document.getElementById('mindmap').clientWidth;
        const height = 600;
        
        const svg = d3.select("#mindmap")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        const g = svg.append("g");
        
        // Create zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        // Create tree layout
        const tree = d3.tree()
            .size([height - 100, width - 200])
            .separation((a, b) => (a.parent == b.parent ? 1 : 2) / a.depth);
        
        // Create hierarchy
        const root = d3.hierarchy(data);
        
        // Collapse all nodes initially except root and first level
        root.descendants().forEach(d => {{
            if (d.depth > 1) {{
                if (d.children) {{
                    d._children = d.children;
                    d.children = null;
                }}
            }}
        }});
        
        let i = 0;
        
        function update(source) {{
            // Compute the new tree layout
            const treeData = tree(root);
            const nodes = treeData.descendants();
            const links = treeData.descendants().slice(1);
            
            // Normalize for fixed-depth
            nodes.forEach(d => {{
                d.y = d.depth * 180;
            }});
            
            // Update nodes
            const node = g.selectAll('g.node')
                .data(nodes, d => d.id || (d.id = ++i));
            
            // Enter new nodes
            const nodeEnter = node.enter().append('g')
                .attr('class', 'node')
                .attr('transform', d => `translate(${{source.y0 || 0}},${{source.x0 || 0}})`)
                .on('click', click);
            
            // Add circles
            nodeEnter.append('circle')
                .attr('r', 1e-6)
                .style('fill', d => {{
                    if (d.data.type === 'root') return '#ff6b6b';
                    if (d.data.type === 'category') return d.data.metadata?.color || '#4ecdc4';
                    if (d.data.type === 'project') return '#45b7d1';
                    if (d.data.type === 'todo') return d.data.metadata?.priority_color || '#ffa502';
                    return '#96ceb4';
                }})
                .style('opacity', 0.8)
                .attr('class', d => d.data.type === 'todo' ? 'todo-node' : '');
            
            // Add labels
            nodeEnter.append('text')
                .attr('dy', '.35em')
                .attr('x', d => {{
                    if (d.data.type === 'todo') return 8;  // Todo items have text to the right
                    return d.children || d._children ? -13 : 13;
                }})
                .style('text-anchor', d => {{
                    if (d.data.type === 'todo') return 'start';
                    return d.children || d._children ? 'end' : 'start';
                }})
                .text(d => {{
                    if (d.data.type === 'todo') {{
                        const statusIcon = {{
                            'initial': '⭕',
                            'pending': '🟡'
                        }}[d.data.metadata?.status] || '⭕';
                        return `${{statusIcon}} ${{d.data.name.replace('📋 ', '')}}`;
                    }}
                    const icon = d.data.metadata?.icon || '';
                    return `${{icon}} ${{d.data.name}}`;
                }})
                .style('fill-opacity', 1e-6)
                .style('font-size', d => d.data.type === 'todo' ? '10px' : '12px');
            
            // Add todo badges
            if (showTodos) {{
                const todoBadges = nodeEnter.filter(d => d.data.todo_summary && d.data.todo_summary.total > 0)
                    .append('g')
                    .attr('class', 'todo-badge')
                    .attr('transform', 'translate(15, -15)');
                
                todoBadges.append('circle')
                    .attr('r', 8)
                    .style('fill', d => {{
                        if (d.data.todo_summary.high_priority > 0) return '#ff4757';
                        if (d.data.todo_summary.medium_priority > 0) return '#ffa502';
                        return '#2ed573';
                    }});
                
                todoBadges.append('text')
                    .text(d => d.data.todo_summary.total)
                    .attr('dy', '.35em')
                    .style('font-size', '10px')
                    .style('fill', 'white')
                    .style('text-anchor', 'middle');
            }}
            
            // Transition nodes to their new position
            const nodeUpdate = nodeEnter.merge(node);
            
            nodeUpdate.transition()
                .duration(750)
                .attr('transform', d => `translate(${{d.y}},${{d.x}})`);
            
            nodeUpdate.select('circle')
                .attr('r', d => {{
                    if (d.data.type === 'root') return 12;
                    if (d.data.type === 'category') return 10;
                    if (d.data.type === 'project') return 8;
                    if (d.data.type === 'todo') return 5;  // Smaller circles for todos
                    return 6;
                }})
                .style('fill', d => {{
                    if (d.data.type === 'root') return '#ff6b6b';
                    if (d.data.type === 'category') return d.data.metadata?.color || '#4ecdc4';
                    if (d.data.type === 'project') return '#45b7d1';
                    if (d.data.type === 'todo') return d.data.metadata?.priority_color || '#ffa502';
                    return '#96ceb4';
                }})
                .attr('cursor', 'pointer');
            
            nodeUpdate.select('text')
                .style('fill-opacity', 1);
            
            // Update todo badges
            nodeUpdate.selectAll('.todo-badge')
                .style('display', showTodos ? 'block' : 'none');
            
            // Remove exiting nodes
            const nodeExit = node.exit().transition()
                .duration(750)
                .attr('transform', d => `translate(${{source.y}},${{source.x}})`)
                .remove();
            
            nodeExit.select('circle')
                .attr('r', 1e-6);
            
            nodeExit.select('text')
                .style('fill-opacity', 1e-6);
            
            // Update links
            const link = g.selectAll('path.link')
                .data(links, d => d.id);
            
            // Enter new links
            const linkEnter = link.enter().insert('path', 'g')
                .attr('class', 'link')
                .attr('d', d => {{
                    const o = {{x: source.x0 || 0, y: source.y0 || 0}};
                    return diagonal(o, o);
                }});
            
            // Transition links to their new position
            linkEnter.merge(link).transition()
                .duration(750)
                .attr('d', d => diagonal(d, d.parent));
            
            // Remove exiting links
            link.exit().transition()
                .duration(750)
                .attr('d', d => {{
                    const o = {{x: source.x, y: source.y}};
                    return diagonal(o, o);
                }})
                .remove();
            
            // Store the old positions for transition
            nodes.forEach(d => {{
                d.x0 = d.x;
                d.y0 = d.y;
            }});
        }}
        
        // Diagonal line generator
        function diagonal(s, d) {{
            const path = `M ${{s.y}} ${{s.x}}
                         C ${{(s.y + d.y) / 2}} ${{s.x}},
                           ${{(s.y + d.y) / 2}} ${{d.x}},
                           ${{d.y}} ${{d.x}}`;
            return path;
        }}
        
        // Toggle children on click
        function click(event, d) {{
            if (d.children) {{
                d._children = d.children;
                d.children = null;
            }} else {{
                d.children = d._children;
                d._children = null;
            }}
            update(d);
        }}
        
        // Add tooltip functionality
        {"" if not interactive else '''
        g.selectAll('.node')
            .on('mouseover', function(event, d) {
                const tooltip = d3.select('#tooltip');
                let content = `<strong>${d.data.name}</strong><br>
                               Type: ${d.data.type}<br>`;
                               
                if (d.data.type === 'todo') {
                    content += `Status: ${d.data.metadata?.status || 'unknown'}<br>
                               Priority: ${d.data.metadata?.priority || 'medium'}<br>
                               Todo ID: ${d.data.metadata?.todo_id || 'N/A'}<br>`;
                    if (d.data.metadata?.created_at) {
                        content += `Created: ${new Date(d.data.metadata.created_at).toLocaleDateString()}<br>`;
                    }
                    if (d.data.metadata?.updated_at) {
                        content += `Updated: ${new Date(d.data.metadata.updated_at).toLocaleDateString()}<br>`;
                    }
                    content += `<div style="margin-top: 8px; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 4px;">
                               <strong>Full Description:</strong><br>${d.data.description}
                               </div>`;
                } else {
                    content += `${d.data.language ? `Language: ${d.data.language}<br>` : ''}
                               ${d.data.description ? `Description: ${d.data.description}<br>` : ''}
                               ${d.data.metadata?.category ? `Category: ${d.data.metadata.category}<br>` : ''}
                               ${d.data.metadata?.size_estimate ? `Size: ${d.data.metadata.size_estimate}<br>` : ''}`;
                    
                    if (d.data.todo_summary && d.data.todo_summary.total > 0) {
                        content += `<h4>📋 Active Todos (${d.data.todo_summary.total})</h4>`;
                        content += `<div>Initial: ${d.data.todo_summary.initial} | Pending: ${d.data.todo_summary.pending}</div>`;
                        content += `<div>High: ${d.data.todo_summary.high_priority} | Med: ${d.data.todo_summary.medium_priority} | Low: ${d.data.todo_summary.low_priority}</div>`;
                        content += `<div style="font-size: 10px; opacity: 0.8;">Completed todos filtered out</div>`;
                        
                        if (d.data.todo_summary.recent_todos && d.data.todo_summary.recent_todos.length > 0) {
                            content += '<div style="margin-top: 5px;"><strong>Recent active todos:</strong></div>';
                            d.data.todo_summary.recent_todos.forEach(todo => {
                                content += `<div class="todo-item">${todo.description}</div>`;
                            });
                        }
                    }
                }
                
                tooltip.style('display', 'block')
                    .html(content)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            })
            .on('mouseout', function() {
                d3.select('#tooltip').style('display', 'none');
            });
        '''}
        
        // Global functions for controls
        window.expandAll = function() {{
            root.descendants().forEach(d => {{
                if (d._children) {{
                    d.children = d._children;
                    d._children = null;
                }}
            }});
            update(root);
        }};
        
        window.collapseAll = function() {{
            root.descendants().forEach(d => {{
                if (d.children && d.depth > 0) {{
                    d._children = d.children;
                    d.children = null;
                }}
            }});
            update(root);
        }};
        
        window.resetView = function() {{
            svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
        }};
        
        window.toggleTodos = function() {{
            showTodos = !showTodos;
            const button = document.getElementById('todoToggle');
            if (button) {{
                button.classList.toggle('active', showTodos);
                button.textContent = showTodos ? 'Hide Todos' : 'Show Todos';
            }}
            update(root);
        }};
        
        // Initial render
        root.x0 = height / 2;
        root.y0 = 0;
        update(root);
        
        // Center the view
        svg.call(zoom.transform, d3.zoomIdentity.translate(50, 50));
        """

    def generate_json(self, root_node: ProjectNode, output_file: str) -> None:
        """Generate JSON representation of the mind map"""
        data = self._node_to_dict(root_node)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"📄 JSON mind map data generated: {output_file}")

    def generate_dot(self, root_node: ProjectNode, output_file: str) -> None:
        """Generate DOT/Graphviz representation"""
        dot_content = ['digraph MadnessInteractive {']
        dot_content.append('  graph [rankdir=TB, bgcolor="#2d3748", fontcolor=white];')
        dot_content.append('  node [style=filled, fontcolor=white, fontname="Arial"];')
        dot_content.append('  edge [color=white];')
        dot_content.append('')

        node_id = 0

        def add_node(node: ProjectNode, parent_id: int = None) -> int:
            nonlocal node_id
            current_id = node_id
            node_id += 1

            # Determine node color and shape
            if node.type == "root":
                color = "#e53e3e"
                shape = "ellipse"
            elif node.type == "category":
                color = node.metadata.get('color', '#4ecdc4')
                shape = "box"
            elif node.type == "project":
                color = "#45b7d1"
                shape = "box"
            else:
                color = "#96ceb4"
                shape = "box"

            # Add node
            label = node.name.replace('"', '\\"')
            if node.metadata.get('icon'):
                label = f"{node.metadata['icon']} {label}"

            # Add todo info to label if present
            if node.todo_summary and node.todo_summary.total > 0:
                label += f"\\n📋 {node.todo_summary.total} todos"

            dot_content.append(f'  n{current_id} [label="{label}", fillcolor="{color}", shape={shape}];')

            # Add edge from parent
            if parent_id is not None:
                dot_content.append(f'  n{parent_id} -> n{current_id};')

            # Add children
            for child in node.children:
                add_node(child, current_id)

            return current_id

        add_node(root_node)
        dot_content.append('}')

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(dot_content))

        print(f"🎯 DOT/Graphviz mind map generated: {output_file}")
        print(f"   To render: dot -Tpng {output_file} -o {output_file.replace('.dot', '.png')}")

    def generate_svg(self, root_node: ProjectNode, output_file: str) -> None:
        """Generate SVG mind map (simplified tree layout)"""
        width = 1200
        height = 800

        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
        </linearGradient>
        <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge> 
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>
    
    <rect width="100%" height="100%" fill="url(#bg)"/>
    
    <text x="{width//2}" y="30" text-anchor="middle" fill="white" font-size="24" font-weight="bold">
        🧠 Madness Interactive Mind Map
    </text>
    
    <text x="{width//2}" y="55" text-anchor="middle" fill="white" font-size="14" opacity="0.8">
        {root_node.metadata.get('total_projects', 0)} Projects • {len(root_node.metadata.get('languages', []))} Technologies{' • ' + str(root_node.metadata.get('total_todos', 0)) + ' Todos' if root_node.metadata.get('todo_enabled') else ''}
    </text>
'''

        # Simple radial layout
        center_x = width // 2
        center_y = height // 2

        # Root node
        svg_content += f'''
    <circle cx="{center_x}" cy="{center_y}" r="20" fill="#e53e3e" filter="url(#glow)"/>
    <text x="{center_x}" y="{center_y + 5}" text-anchor="middle" fill="white" font-size="12" font-weight="bold">
        {root_node.name}
    </text>
'''

        # Category nodes in a circle around root
        import math
        num_categories = len(root_node.children)
        if num_categories > 0:
            angle_step = 2 * math.pi / num_categories
            radius = 150

            for i, category in enumerate(root_node.children):
                angle = i * angle_step
                cat_x = center_x + radius * math.cos(angle)
                cat_y = center_y + radius * math.sin(angle)

                color = category.metadata.get('color', '#4ecdc4')
                icon = category.metadata.get('icon', '📁')

                # Line from root to category
                svg_content += f'''
    <line x1="{center_x}" y1="{center_y}" x2="{cat_x}" y2="{cat_y}" stroke="white" stroke-width="2" opacity="0.6"/>
    <circle cx="{cat_x}" cy="{cat_y}" r="15" fill="{color}" filter="url(#glow)"/>
    <text x="{cat_x}" y="{cat_y + 3}" text-anchor="middle" fill="white" font-size="10" font-weight="bold">
        {icon}
    </text>
    <text x="{cat_x}" y="{cat_y + 25}" text-anchor="middle" fill="white" font-size="10">
        {category.name}
    </text>
    <text x="{cat_x}" y="{cat_y + 40}" text-anchor="middle" fill="white" font-size="8" opacity="0.8">
        {category.metadata.get('project_count', 0)} projects{' • ' + str(category.todo_summary.total) + ' todos' if category.todo_summary and category.todo_summary.total > 0 else ''}
    </text>
'''

                # Project nodes around each category
                projects = [child for child in category.children if child.type == "project"]
                if projects:
                    proj_radius = 80
                    proj_angle_step = 2 * math.pi / len(projects) if len(projects) > 1 else 0

                    for j, project in enumerate(projects[:8]):  # Limit to 8 projects per category
                        proj_angle = angle + (j * proj_angle_step) - math.pi/2
                        proj_x = cat_x + proj_radius * math.cos(proj_angle)
                        proj_y = cat_y + proj_radius * math.sin(proj_angle)

                        # Ensure projects stay within bounds
                        proj_x = max(50, min(width - 50, proj_x))
                        proj_y = max(80, min(height - 30, proj_y))

                        svg_content += f'''
    <line x1="{cat_x}" y1="{cat_y}" x2="{proj_x}" y2="{proj_y}" stroke="white" stroke-width="1" opacity="0.4"/>
    <circle cx="{proj_x}" cy="{proj_y}" r="8" fill="#45b7d1" opacity="0.8"/>
    <text x="{proj_x}" y="{proj_y + 20}" text-anchor="middle" fill="white" font-size="8">
        {project.name[:15]}{'...' if len(project.name) > 15 else ''}
    </text>
'''

                        # Add todo badge for projects
                        if project.todo_summary and project.todo_summary.total > 0:
                            badge_color = '#ff4757' if project.todo_summary.high_priority > 0 else '#ffa502' if project.todo_summary.medium_priority > 0 else '#2ed573'
                            svg_content += f'''
    <circle cx="{proj_x + 12}" cy="{proj_y - 8}" r="6" fill="{badge_color}" opacity="0.9"/>
    <text x="{proj_x + 12}" y="{proj_y - 5}" text-anchor="middle" fill="white" font-size="7" font-weight="bold">
        {project.todo_summary.total}
    </text>
'''

        svg_content += '</svg>'

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        print(f"🎨 SVG mind map generated: {output_file}")

    def scan_todo_projects(self) -> ProjectNode:
        """Scan todo database and build a todo-centric project tree"""
        target_projects = [
            'madness_interactive',
            'swarmonomicon', 
            'todomill_projectorium',
            'inventorium',
            'SwarmDesk'
        ]

        # Get all todo summaries if todo integration is enabled
        project_todos = {}
        if self.todo_integration:
            all_project_todos = self.todo_integration.get_active_project_todos()
            # Filter to only target projects that have active todos
            for project_name in target_projects:
                if project_name in all_project_todos:
                    project_todos[project_name] = all_project_todos[project_name]

        root_node = ProjectNode(
            name="Active Todo Projects",
            path="",
            type="root",
            description="Current active projects tracked in todo system (completed todos filtered out)",
            metadata={
                'scan_time': datetime.now().isoformat(),
                'total_projects': len(project_todos),
                'todo_enabled': True,
                'total_todos': sum(summary.total for summary in project_todos.values()) if project_todos else 0,
                'target_projects': target_projects,
                'active_projects': list(project_todos.keys())
            }
        )

        # Create nodes for each target project that has todos
        for project_name in target_projects:
            if project_name not in project_todos:
                print(f"⚠️  Skipping {project_name} - no todos found in database")
                continue
                
            project_summary = project_todos[project_name]
            
            project_node = ProjectNode(
                name=project_name,
                path="",
                type="project",
                language="mixed",
                description=f"Active project with {project_summary.total} active todos",
                metadata={
                    'category': 'Active Project',
                    'todo_count': project_summary.total,
                    'high_priority_count': project_summary.high_priority,
                    'medium_priority_count': project_summary.medium_priority,
                    'low_priority_count': project_summary.low_priority,
                    'status_initial': project_summary.initial,
                    'status_pending': project_summary.pending,
                    'status_completed': project_summary.completed  # This will be 0 now
                },
                todo_summary=project_summary
            )

            # Add individual todo items as child nodes
            if self.todo_integration:
                todo_items = self.todo_integration.get_project_todo_items(project_name, 20)  # Get up to 20 todos
                for todo_item in todo_items:
                    # First 20 characters of description
                    short_desc = todo_item['description'][:20]
                    if len(todo_item['description']) > 20:
                        short_desc += "..."
                    
                    todo_node = ProjectNode(
                        name=f"{todo_item['id'][:8]}... {short_desc}",
                        path="",
                        type="todo",
                        language="",
                        description=todo_item['description'],  # Full description for tooltip
                        metadata={
                            'todo_id': todo_item['id'],
                            'status': todo_item['status'],
                            'priority': todo_item['priority'],
                            'created_at': todo_item['created_at'],
                            'updated_at': todo_item['updated_at'],
                            'priority_color': {
                                'high': '#ff4757',
                                'medium': '#ffa502', 
                                'low': '#2ed573'
                            }.get(todo_item['priority'], '#ffa502'),
                            'status_color': {
                                'initial': '#5352ed',
                                'pending': '#ffa502',
                                'completed': '#2ed573'
                            }.get(todo_item['status'], '#5352ed')
                        }
                    )
                    project_node.children.append(todo_node)
            
            root_node.children.append(project_node)

        return root_node

def main():
    parser = argparse.ArgumentParser(description="Generate mind maps from Madness Interactive project structure")
    parser.add_argument('--format', choices=['html', 'svg', 'dot', 'json'], default='html',
                        help='Output format (default: html)')
    parser.add_argument('--output', help='Output file (default: mindmap.{format})')
    parser.add_argument('--depth', type=int, default=3, help='Maximum depth to scan (default: 3)')
    parser.add_argument('--style', choices=['tech', 'hierarchical'], default='tech',
                        help='Mind map style (default: tech)')
    parser.add_argument('--interactive', action='store_true', help='Add interactive features (HTML only)')
    parser.add_argument('--exclude', action='append', help='Exclude directories matching pattern')
    parser.add_argument('--include-todos', action='store_true', help='Include todo information in mindmap')
    parser.add_argument('--include-todo-items', action='store_true', help='Include individual todo items as nodes (top 5 projects only)')
    parser.add_argument('--todo-centric', action='store_true', help='Generate todo-centric mindmap focusing on active projects from database')
    parser.add_argument('--root', default='.', help='Root directory to scan (default: current directory)')

    args = parser.parse_args()

    # Determine output file
    if not args.output:
        args.output = f"mindmap.{args.format}"

    print("🧠 Madness Interactive Mind Map Generator")
    print("=" * 50)
    print(f"📁 Scanning projects from: {os.path.abspath(args.root)}")
    print(f"📊 Output format: {args.format}")
    print(f"📄 Output file: {args.output}")
    print(f"🔍 Max depth: {args.depth}")
    if args.include_todos:
        print("📋 Todo integration: enabled")
    if args.include_todo_items:
        print("📋 Individual todo items: enabled (top 5 projects)")
    if args.todo_centric:
        print("📋 Todo-centric: enabled")
    print("")

    # Generate mind map
    if args.todo_centric:
        # Force todo integration for todo-centric mode
        generator = MindMapGenerator(args.root, True, True)
    else:
        generator = MindMapGenerator(args.root, args.include_todos, args.include_todo_items)

    print("🔄 Scanning project structure...")
    if args.todo_centric:
        root_node = generator.scan_todo_projects()
    else:
        root_node = generator.scan_projects(args.depth, args.exclude or [])

    print(f"✅ Scanned {root_node.metadata.get('total_projects', 0)} projects in {len(root_node.children)} categories")
    if args.todo_centric:
        print(f"🎯 Active projects: {', '.join(root_node.metadata.get('active_projects', []))}")
        print(f"📋 Active todos: {root_node.metadata.get('total_todos', 0)} (completed todos filtered out)")
    else:
        print(f"🏷️  Technologies: {', '.join(root_node.metadata.get('languages', []))}")
        if args.include_todos:
            print(f"📋 Total todos: {root_node.metadata.get('total_todos', 0)}")
        if args.include_todo_items and generator.top_todo_projects:
            print(f"📋 Top projects with individual todos: {', '.join(generator.top_todo_projects)}")
    print("")

    print(f"🎨 Generating {args.format.upper()} mind map...")

    if args.format == 'html':
        generator.generate_html(root_node, args.output, args.interactive)
    elif args.format == 'svg':
        generator.generate_svg(root_node, args.output)
    elif args.format == 'dot':
        generator.generate_dot(root_node, args.output)
    elif args.format == 'json':
        generator.generate_json(root_node, args.output)

    print("")
    print("🎉 Mind map generation complete!")
    print("   Open the generated file to explore your Madness Interactive ecosystem!")

if __name__ == "__main__":
    main()
