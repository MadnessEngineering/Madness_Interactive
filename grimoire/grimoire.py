#!/usr/bin/env python
"""
GRIMOIRE OF KNOWLEDGE
=====================
A mad-science themed documentation generator that
transmutes mundane markdown into an arcane grimoire!

Author: MadScientist-AI
Version: 0.1.0
License: The Mad Scientific License (MSL-1.0)
"""

import os
import re
import shutil
import random
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import typer
import markdown
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler
from jinja2 import Environment, FileSystemLoader
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Initialize Typer app
app = typer.Typer(
    help="Transform your mundane documentation into a GRIMOIRE OF FORBIDDEN KNOWLEDGE!",
    add_completion=False,
)

# Initialize Rich console
console = Console()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("grimoire")

# Arcane constants
ALCHEMICAL_SYMBOLS = {
    "warning": "☠️",
    "note": "⚗️",
    "tip": "🔮",
    "important": "⚡",
    "example": "🧪",
    "experimental": "🧙",
    "deprecated": "⚰️",
}

ARCANE_TITLES = [
    "The Grand Codex of",
    "Forbidden Secrets of",
    "The Mad Scientist's Guide to",
    "Eldritch Revelations:",
    "The Alchemical Principles of",
    "Darkest Discoveries:",
    "Experimental Protocols:",
    "Unfathomable Wisdom:",
    "Laboratory Chronicles:",
    "Theoretical Abominations:",
]

class GrimoireTheme:
    """Controls the theming of the generated grimoire."""
    
    def __init__(self, theme_name: str = "eldritch"):
        self.theme_name = theme_name
        self.css_vars = self._load_theme()
        
    def _load_theme(self) -> Dict[str, str]:
        """Load theme variables."""
        themes = {
            "eldritch": {
                "primary-color": "#6a0dad",
                "secondary-color": "#1e8c93",
                "background-color": "#f5f3e9",
                "text-color": "#333333",
                "header-font": "'Cinzel Decorative', cursive",
                "body-font": "'Crimson Text', serif",
                "code-font": "'Fira Code', monospace",
                "border-style": "double",
                "page-texture": "url('assets/parchment.png')",
            },
            "steampunk": {
                "primary-color": "#b87333",
                "secondary-color": "#5c4033",
                "background-color": "#f8ecc9",
                "text-color": "#333333",
                "header-font": "'Philosopher', serif",
                "body-font": "'IM Fell English', serif",
                "code-font": "'Source Code Pro', monospace",
                "border-style": "groove",
                "page-texture": "url('assets/brass.png')",
            },
            "cosmic": {
                "primary-color": "#8a2be2",
                "secondary-color": "#00ced1",
                "background-color": "#111133",
                "text-color": "#e6e6fa",
                "header-font": "'Orbitron', sans-serif",
                "body-font": "'Exo 2', sans-serif",
                "code-font": "'Major Mono Display', monospace",
                "border-style": "ridge",
                "page-texture": "url('assets/stars.png')",
            },
        }
        return themes.get(self.theme_name, themes["eldritch"])
    
    def get_css(self) -> str:
        """Generate CSS based on theme variables."""
        css_template = """
        :root {
            --primary-color: {{primary-color}};
            --secondary-color: {{secondary-color}};
            --background-color: {{background-color}};
            --text-color: {{text-color}};
            --header-font: {{header-font}};
            --body-font: {{body-font}};
            --code-font: {{code-font}};
            --border-style: {{border-style}};
            --page-texture: {{page-texture}};
        }
        """
        for key, value in self.css_vars.items():
            css_template = css_template.replace(f"{{{{{key}}}}}", value)
        return css_template

class GrimoireGenerator:
    """Core generator for the Grimoire of Knowledge."""
    
    def __init__(
        self, 
        input_dir: Path, 
        output_dir: Path, 
        theme: str = "eldritch",
        template_dir: Optional[Path] = None,
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.theme = GrimoireTheme(theme)
        
        # Set up template environment
        self.template_dir = template_dir or Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create assets directory
        self.assets_dir = self.output_dir / "assets"
        self.assets_dir.mkdir(exist_ok=True)
        
    def _enhance_title(self, title: str) -> str:
        """Add some arcane flair to boring titles."""
        if random.random() < 0.7:  # 70% chance to add arcane prefix
            return f"{random.choice(ARCANE_TITLES)} {title}"
        return title
    
    def _process_markdown(self, content: str) -> str:
        """Process markdown with mad-science themed enhancements."""
        # Add arcane symbols to admonitions
        for key, symbol in ALCHEMICAL_SYMBOLS.items():
            content = re.sub(
                rf"!!! {key}",
                f"!!! {key} {symbol}",
                content
            )
        
        # Enhance headings with arcane prefixes (only level 1 and 2)
        def enhance_heading(match):
            level, title = match.groups()
            if level in ("#", "##") and ":" not in title:
                enhanced = self._enhance_title(title.strip())
                return f"{level} {enhanced}"
            return match.group(0)
            
        content = re.sub(r"(^#{1,2})\s+([^\n]+)", enhance_heading, content, flags=re.MULTILINE)
        
        # Add random arcane quotes to the document
        quotes = [
            "> *\"The difference between madness and genius is measured only by success!\"*",
            "> *\"In the depths of chaos, I found the secrets of order.\"*",
            "> *\"That is not dead which can eternal lie, and with strange aeons even code may compile.\"*",
            "> *\"Science without madness is like a day without electricity coursing through random objects!\"*",
            "> *\"When the experiment fails, you have discovered a new way to create an explosion.\"*",
        ]
        
        if random.random() < 0.4:  # 40% chance to add a quote
            quote_pos = content.find("\n\n")
            if quote_pos > -1:
                content = content[:quote_pos] + "\n\n" + random.choice(quotes) + content[quote_pos:]
        
        return content
    
    def _convert_markdown_to_html(self, content: str) -> str:
        """Convert enhanced markdown to HTML."""
        extensions = [
            'pymdownx.superfences',
            'pymdownx.tabbed',
            'pymdownx.highlight',
            'pymdownx.emoji',
            'pymdownx.tasklist',
            'pymdownx.details',
            'mdx_math',
            'toc',
        ]
        
        html = markdown.markdown(
            content,
            extensions=extensions,
            output_format='html5'
        )
        return html
    
    def _render_template(self, template_name: str, context: Dict) -> str:
        """Render a template with the given context."""
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)
    
    def process_file(self, input_file: Path) -> Path:
        """Process a single markdown file into a grimoire page."""
        rel_path = input_file.relative_to(self.input_dir)
        output_file = self.output_dir / rel_path.with_suffix('.html')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with input_file.open('r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from the first heading or use filename
        title_match = re.search(r'^# (.*?)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
        else:
            title = input_file.stem.replace('_', ' ').title()
        
        # Process markdown with arcane enhancements
        enhanced_content = self._process_markdown(content)
        html_content = self._convert_markdown_to_html(enhanced_content)
        
        # Render with template
        full_html = self._render_template('page.html', {
            'title': title,
            'content': html_content,
            'css': self.theme.get_css(),
            'relative_path': '../' * (len(rel_path.parts) - 1) if len(rel_path.parts) > 1 else './'
        })
        
        with output_file.open('w', encoding='utf-8') as f:
            f.write(full_html)
        
        return output_file
    
    def process_directory(self) -> List[Path]:
        """Process all markdown files in the input directory."""
        processed_files = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]Conjuring grimoire pages..."),
            console=console
        ) as progress:
            task = progress.add_task("Transmuting...", total=None)
            
            for file in self.input_dir.glob('**/*.md'):
                if file.is_file():
                    try:
                        output_file = self.process_file(file)
                        processed_files.append(output_file)
                        progress.update(task, advance=1)
                    except Exception as e:
                        log.error(f"Failed to process {file}: {e}")
            
            # Copy assets
            source_assets = Path(__file__).parent / "assets"
            if source_assets.exists():
                for asset in source_assets.iterdir():
                    if asset.is_file():
                        shutil.copy(asset, self.assets_dir)
            
            # Generate index
            self._generate_index(processed_files)
            
        return processed_files
    
    def _generate_index(self, processed_files: List[Path]) -> Path:
        """Generate an index page for the grimoire."""
        pages = []
        for file in processed_files:
            rel_path = file.relative_to(self.output_dir)
            with file.open('r', encoding='utf-8') as f:
                content = f.read()
                title_match = re.search(r'<title>(.*?)</title>', content)
                title = title_match.group(1) if title_match else rel_path.stem.replace('_', ' ').title()
            
            pages.append({
                'title': title,
                'path': rel_path.as_posix(),
                'category': rel_path.parent.name if rel_path.parent.name != '.' else 'Uncategorized'
            })
        
        # Sort pages by category and title
        pages.sort(key=lambda x: (x['category'], x['title']))
        
        # Group by category
        categories = {}
        for page in pages:
            cat = page['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(page)
        
        index_html = self._render_template('index.html', {
            'title': 'The Grand Grimoire of Knowledge',
            'categories': categories,
            'css': self.theme.get_css(),
            'relative_path': './'
        })
        
        index_path = self.output_dir / 'index.html'
        with index_path.open('w', encoding='utf-8') as f:
            f.write(index_html)
        
        return index_path

class GrimoireWatcher(FileSystemEventHandler):
    """Watch for changes in markdown files and regenerate the grimoire."""
    
    def __init__(self, generator: GrimoireGenerator):
        self.generator = generator
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            log.info(f"Change detected in {event.src_path}")
            try:
                input_file = Path(event.src_path)
                if input_file.exists() and input_file.is_relative_to(self.generator.input_dir):
                    self.generator.process_file(input_file)
                    log.info(f"Regenerated {input_file}")
            except Exception as e:
                log.error(f"Error processing changed file: {e}")

@app.command()
def generate(
    input_dir: str = typer.Argument(
        "docs", help="Directory containing markdown files"
    ),
    output_dir: str = typer.Option(
        "grimoire_output", "--output", "-o", help="Output directory for the grimoire"
    ),
    theme: str = typer.Option(
        "eldritch", "--theme", "-t", 
        help="Theme for the grimoire (eldritch, steampunk, cosmic)"
    ),
    watch: bool = typer.Option(
        False, "--watch", "-w", help="Watch for changes and regenerate"
    ),
):
    """Generate a mad-science themed grimoire from markdown files."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        log.error(f"Input directory {input_dir} does not exist!")
        raise typer.Exit(code=1)
    
    console.print(f"[bold magenta]INITIATING ARCANE GRIMOIRE GENERATION RITUAL![/]")
    console.print(f"[dim]Input: {input_path.absolute()}[/]")
    console.print(f"[dim]Output: {output_path.absolute()}[/]")
    console.print(f"[dim]Theme: {theme}[/]")
    
    generator = GrimoireGenerator(
        input_dir=input_path,
        output_dir=output_path,
        theme=theme,
    )
    
    processed_files = generator.process_directory()
    console.print(f"[bold green]RITUAL COMPLETE![/] [dim]Generated {len(processed_files)} grimoire pages[/]")
    
    if watch:
        console.print("[yellow]Entering watchful trance... Press Ctrl+C to break the spell[/]")
        event_handler = GrimoireWatcher(generator)
        observer = Observer()
        observer.schedule(event_handler, input_path, recursive=True)
        observer.start()
        
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            console.print("[bold red]The ritual has been interrupted![/]")
        
        observer.join()

@app.command()
def create_template(
    output_dir: str = typer.Argument(
        "grimoire_templates", help="Directory to create template files"
    ),
):
    """Create template files for the grimoire generator."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    templates = {
        "page.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Fira+Code&family=IM+Fell+English&family=Major+Mono+Display&family=Orbitron:wght@400;600&family=Philosopher:wght@400;700&display=swap">
    <style>
        {{ css }}
        
        body {
            font-family: var(--body-font);
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 0;
            margin: 0;
            background-image: var(--page-texture);
        }
        
        .grimoire-container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
            border: 7px var(--border-style) var(--primary-color);
            border-radius: 8px;
            background-color: var(--background-color);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            position: relative;
        }
        
        .grimoire-container::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(
                circle at center,
                transparent 80%,
                rgba(0, 0, 0, 0.1)
            );
            pointer-events: none;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--header-font);
            color: var(--primary-color);
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            line-height: 1.2;
        }
        
        h1 {
            font-size: 2.5rem;
            border-bottom: 3px double var(--primary-color);
            padding-bottom: 0.3em;
            margin-bottom: 1em;
        }
        
        h2 {
            font-size: 1.8rem;
            border-bottom: 1px solid var(--secondary-color);
            padding-bottom: 0.2em;
        }
        
        h3 {
            font-size: 1.5rem;
            color: var(--secondary-color);
        }
        
        a {
            color: var(--primary-color);
            text-decoration: none;
            border-bottom: 1px dotted var(--primary-color);
        }
        
        a:hover {
            color: var(--secondary-color);
            border-bottom: 1px solid var(--secondary-color);
        }
        
        pre {
            background-color: rgba(0, 0, 0, 0.1);
            padding: 1rem;
            overflow-x: auto;
            border-left: 4px solid var(--secondary-color);
            font-family: var(--code-font);
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        code {
            font-family: var(--code-font);
            background-color: rgba(0, 0, 0, 0.05);
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
        }
        
        blockquote {
            border-left: 4px solid var(--secondary-color);
            margin-left: 0;
            padding-left: 1.5rem;
            font-style: italic;
            color: rgba(var(--text-color-rgb), 0.8);
        }
        
        img {
            max-width: 100%;
            height: auto;
            border: 1px solid var(--secondary-color);
            border-radius: 4px;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }
        
        th, td {
            padding: 0.5rem;
            border: 1px solid var(--secondary-color);
        }
        
        th {
            background-color: rgba(0, 0, 0, 0.1);
            font-family: var(--header-font);
            color: var(--primary-color);
        }
        
        /* Admonitions */
        .admonition {
            padding: 1rem;
            margin: 1.5rem 0;
            border-left: 4px solid var(--primary-color);
            background-color: rgba(0, 0, 0, 0.05);
            position: relative;
        }
        
        .admonition-title {
            font-family: var(--header-font);
            font-weight: 700;
            margin-top: 0;
            margin-bottom: 0.5rem;
            color: var(--primary-color);
        }
        
        .admonition.note {
            border-left-color: #00BCD4;
        }
        
        .admonition.warning {
            border-left-color: #FFC107;
        }
        
        .admonition.danger {
            border-left-color: #F44336;
        }
        
        .footer-nav {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid var(--secondary-color);
            display: flex;
            justify-content: space-between;
        }
        
        .back-to-index {
            display: inline-block;
            margin-top: 2rem;
            padding: 0.5rem 1rem;
            background-color: var(--primary-color);
            color: white;
            border-radius: 4px;
            text-decoration: none;
            border: none;
            font-family: var(--header-font);
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 1px;
            transition: background-color 0.3s;
        }
        
        .back-to-index:hover {
            background-color: var(--secondary-color);
            color: white;
            border: none;
        }
    </style>
</head>
<body>
    <div class="grimoire-container">
        {{ content | safe }}
        
        <div class="footer-nav">
            <a href="{{ relative_path }}index.html" class="back-to-index">Back to Grimoire Index</a>
        </div>
    </div>
</body>
</html>""",
        "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Fira+Code&family=IM+Fell+English&family=Major+Mono+Display&family=Orbitron:wght@400;600&family=Philosopher:wght@400;700&display=swap">
    <style>
        {{ css }}
        
        body {
            font-family: var(--body-font);
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 0;
            margin: 0;
            background-image: var(--page-texture);
        }
        
        .grimoire-container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
            border: 7px var(--border-style) var(--primary-color);
            border-radius: 8px;
            background-color: var(--background-color);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            position: relative;
        }
        
        .grimoire-container::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(
                circle at center,
                transparent 80%,
                rgba(0, 0, 0, 0.1)
            );
            pointer-events: none;
        }
        
        h1 {
            font-family: var(--header-font);
            color: var(--primary-color);
            text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
            text-align: center;
            font-size: 3rem;
            margin-bottom: 2rem;
            border-bottom: 3px double var(--primary-color);
            padding-bottom: 1rem;
        }
        
        h2 {
            font-family: var(--header-font);
            color: var(--secondary-color);
            margin-top: 2rem;
            font-size: 1.8rem;
            border-bottom: 1px solid var(--secondary-color);
            padding-bottom: 0.3rem;
        }
        
        .toc-category {
            margin-bottom: 2rem;
        }
        
        .toc-list {
            list-style-type: none;
            padding-left: 1rem;
        }
        
        .toc-item {
            margin: 0.8rem 0;
            padding-left: 1.5rem;
            position: relative;
        }
        
        .toc-item::before {
            content: "⦿";
            position: absolute;
            left: 0;
            color: var(--primary-color);
        }
        
        .toc-link {
            color: var(--primary-color);
            text-decoration: none;
            border-bottom: 1px dotted transparent;
            transition: all 0.3s;
            font-size: 1.1rem;
        }
        
        .toc-link:hover {
            color: var(--secondary-color);
            border-bottom: 1px dotted var(--secondary-color);
        }
        
        .grimoire-footer {
            text-align: center;
            margin-top: 3rem;
            font-style: italic;
            opacity: 0.8;
            border-top: 1px solid var(--secondary-color);
            padding-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="grimoire-container">
        <h1>{{ title }}</h1>
        
        <div class="toc">
            {% for category, pages in categories.items() %}
            <div class="toc-category">
                <h2>{{ category }}</h2>
                <ul class="toc-list">
                    {% for page in pages %}
                    <li class="toc-item">
                        <a href="{{ page.path }}" class="toc-link">{{ page.title }}</a>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>
        
        <div class="grimoire-footer">
            <p>"The difference between madness and genius is measured only by success!"</p>
        </div>
    </div>
</body>
</html>"""
    }
    
    assets_dir = output_path / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    for name, content in templates.items():
        template_file = output_path / name
        with template_file.open('w', encoding='utf-8') as f:
            f.write(content)
    
    console.print(f"[bold green]Template files created in {output_path}![/]")

if __name__ == "__main__":
    app() 