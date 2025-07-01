# 🧠 Madness Interactive Mind Map System

Welcome to the Madness Interactive Mind Map system! This tool visualizes the sprawling ecosystem of projects, todos, and lessons learned in a beautiful, interactive way. It helps you (and your AI agents) see the big picture, track progress, and discover hidden connections across the Madness Interactive universe.

## Overview

The mindmap system is powered by `scripts/mindmap_generator.py`, a flexible Python tool that scans the project structure, queries the MCP todo/lessons database, and generates interactive visualizations in multiple formats (HTML, SVG, DOT, JSON).

- **Visualize**: See all projects, technologies, and their relationships at a glance.
- **Track Todos**: Integrate with the MCP todo system to show active work, priorities, and project health.
- **Lessons Learned**: Explore a knowledge base of lessons, cross-referenced by language and tags.
- **Customizable**: Filter by depth, style, or focus on todos/lessons.

## Features

- **Interactive HTML Mind Map**: Pan, zoom, expand/collapse nodes, and view tooltips for rich project/todo/lesson info.
- **SVG, DOT, JSON Exports**: For embedding, automation, or further analysis.
- **Todo Integration**: Show project todo counts, priorities, and individual items (active only).
- **Lessons Learned Mode**: Visualize knowledge by language and tag, with lesson summaries and details.
- **Makefile Integration**: Easy one-command generation for all formats.

## Usage

Run the generator from the project root:

```bash
python3 scripts/mindmap_generator.py --format html --interactive --output docs/mindmap.html
```

### Common Options

- `--format html|svg|dot|json`   Output format (default: html)
- `--output FILE`                Output file (default: mindmap.html)
- `--depth N`                    Maximum directory depth (default: 3)
- `--style tech|hierarchical`    Mind map style (default: tech)
- `--interactive`                Enable interactive HTML features
- `--include-todos`              Show todo summaries per project
- `--include-todo-items`         Show individual todo items (top 5 projects)
- `--todo-centric`               Show only active projects/todos from the database
- `--lessons-learned`            Visualize lessons learned by language/tag

See all options:

```bash
python3 scripts/mindmap_generator.py --help
```

## Makefile Targets

The Makefile provides convenient shortcuts:

- `make mindmap`                   – Interactive HTML mind map (default)
- `make mindmap-with-todos`         – Mind map with todo summaries
- `make mindmap-with-todo-items`    – Mind map with individual todo items (top 5 projects)
- `make mindmap-todo-centric`       – Mind map focused on active projects/todos
- `make mindmap-lessons-learned`    – Mind map of lessons learned (by language/tag)
- `make mindmap-svg`                – SVG export
- `make mindmap-dot`                – DOT/Graphviz export
- `make mindmap-json`               – JSON export
- `make mindmap-all`                – All formats

Outputs are written to `docs/` (e.g., `docs/mindmap.html`, `docs/mindmap_todos.html`, etc).

## Customization

- **Project/Category Structure**: Controlled by directory layout in `projects/`.
- **Todo/Knowledge Data**: Pulled directly from the MCP MongoDB (`swarmonomicon.todos`, `lessons_learned`).
- **Appearance/Behavior**: Tweak `scripts/mindmap_generator.py` for advanced customization (colors, icons, node types, etc).

## Example Outputs

- [Interactive Mind Map](mindmap.html)
- [Todo-Centric Mind Map](mindmap_todos.html)
- [Lessons Learned Map](mindmap_lessons.html)
- [SVG Export](mindmap.svg)
- [DOT Export](mindmap.dot)
- [JSON Export](mindmap.json)

## Troubleshooting

- Ensure `pymongo` is installed for database integration: `pip install pymongo`
- MongoDB connection details are read from environment or default to localhost.
- If you see missing data, check your database connection and todo/lesson collections.

## Contributing

- Add new mindmap features or visualizations in `scripts/mindmap_generator.py`.
- Update this README with new capabilities or usage tips.
- Share your own mindmap outputs and ideas!

---

*"The difference between madness and genius is measured only by success!" – Unknown Mad Scientist*
