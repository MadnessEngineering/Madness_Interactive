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
    
Examples:
    python mindmap_generator.py --format html --interactive
    python mindmap_generator.py --format svg --style hierarchical
    python mindmap_generator.py --format dot --depth 2
"""

import os
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime

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
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}

class MindMapGenerator:
    """Generate mind maps from project structure"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.projects_path = self.root_path / "projects"
        
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
        
        root_node = ProjectNode(
            name="Madness Interactive",
            path=str(self.root_path),
            type="root",
            description="A Mad Tinker's AI Project Hub",
            metadata={
                'scan_time': datetime.now().isoformat(),
                'total_projects': 0,
                'languages': set()
            }
        )
        
        if not self.projects_path.exists():
            return root_node
        
        # Scan by language/technology categories
        for lang_dir in self.projects_path.iterdir():
            if not lang_dir.is_dir() or self._should_exclude(lang_dir.name, exclude_patterns):
                continue
                
            lang_node = self._scan_language_category(lang_dir, max_depth - 1, exclude_patterns)
            if lang_node.children:  # Only add if it has projects
                root_node.children.append(lang_node)
                root_node.metadata['languages'].add(lang_node.language)
        
        # Convert set to list for JSON serialization
        root_node.metadata['languages'] = list(root_node.metadata['languages'])
        root_node.metadata['total_projects'] = self._count_projects(root_node)
        
        return root_node
    
    def _scan_language_category(self, lang_path: Path, max_depth: int, exclude_patterns: List[str]) -> ProjectNode:
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
        
        # Scan projects in this language category
        for project_path in lang_path.iterdir():
            if not project_path.is_dir() or self._should_exclude(project_path.name, exclude_patterns):
                continue
            
            project_node = self._scan_project(project_path, max_depth - 1, exclude_patterns, lang_name)
            if project_node:
                lang_node.children.append(project_node)
                lang_node.metadata['project_count'] += 1
        
        return lang_node
    
    def _scan_project(self, project_path: Path, max_depth: int, exclude_patterns: List[str], language: str) -> ProjectNode:
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
            }
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
        
        .link {{
            fill: none;
            stroke: rgba(255, 255, 255, 0.3);
            stroke-width: 2px;
        }}
        
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
        </div>
        
        <div class="legend">
            {self._generate_legend_html(root_node)}
        </div>
        
        {"<div class='controls'><button onclick='expandAll()'>Expand All</button><button onclick='collapseAll()'>Collapse All</button><button onclick='resetView()'>Reset View</button></div>" if interactive else ""}
        
        <div id="mindmap"></div>
    </div>
    
    <div class="tooltip" id="tooltip" style="display: none;"></div>
    
    <script>
        const data = {json.dumps(self._node_to_dict(root_node), indent=2)};
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
        return {
            'name': node.name,
            'type': node.type,
            'language': node.language,
            'description': node.description,
            'metadata': node.metadata,
            'children': [self._node_to_dict(child) for child in node.children]
        }
    
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
                    return '#96ceb4';
                }})
                .style('opacity', 0.8);
            
            // Add labels
            nodeEnter.append('text')
                .attr('dy', '.35em')
                .attr('x', d => d.children || d._children ? -13 : 13)
                .style('text-anchor', d => d.children || d._children ? 'end' : 'start')
                .text(d => {{
                    const icon = d.data.metadata?.icon || '';
                    return `${{icon}} ${{d.data.name}}`;
                }})
                .style('fill-opacity', 1e-6);
            
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
                    return 6;
                }})
                .style('fill', d => {{
                    if (d.data.type === 'root') return '#ff6b6b';
                    if (d.data.type === 'category') return d.data.metadata?.color || '#4ecdc4';
                    if (d.data.type === 'project') return '#45b7d1';
                    return '#96ceb4';
                }})
                .attr('cursor', 'pointer');
            
            nodeUpdate.select('text')
                .style('fill-opacity', 1);
            
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
                tooltip.style('display', 'block')
                    .html(`
                        <strong>${d.data.name}</strong><br>
                        Type: ${d.data.type}<br>
                        ${d.data.language ? `Language: ${d.data.language}<br>` : ''}
                        ${d.data.description ? `Description: ${d.data.description}<br>` : ''}
                        ${d.data.metadata?.category ? `Category: ${d.data.metadata.category}<br>` : ''}
                        ${d.data.metadata?.size_estimate ? `Size: ${d.data.metadata.size_estimate}<br>` : ''}
                    `)
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
        {root_node.metadata.get('total_projects', 0)} Projects • {len(root_node.metadata.get('languages', []))} Technologies
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
        {category.metadata.get('project_count', 0)} projects
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
        
        svg_content += '</svg>'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"🎨 SVG mind map generated: {output_file}")

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
    print("")
    
    # Generate mind map
    generator = MindMapGenerator(args.root)
    
    print("🔄 Scanning project structure...")
    root_node = generator.scan_projects(args.depth, args.exclude or [])
    
    print(f"✅ Scanned {root_node.metadata.get('total_projects', 0)} projects in {len(root_node.children)} categories")
    print(f"🏷️  Technologies: {', '.join(root_node.metadata.get('languages', []))}")
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
