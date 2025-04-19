#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
THE GRIMOIRE BINDER

A mad scientist's solution to documentation chaos, designed to harvest markdown files
throughout the repository, apply consistent formatting, generate cross-references,
and compile a comprehensive documentation site.

This script represents the prototype/proof of concept for the Grimoire Binder system.
"""

import os
import re
import glob
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Configuration
DEFAULT_CONFIG = {
    'grimoire_root': 'docs/grimoire',
    'output_dir': 'docs/grimoire_site',
    'base_repo_path': '.',
    'excluded_dirs': ['.git', '__pycache__', 'node_modules', 'venv'],
    'markdown_extensions': ['.md', '.markdown'],
    'template_dir': 'docs/grimoire/templates',
    'assets_dir': 'docs/assets',
    'madness_level': 3  # On a scale of 1-5, how mad scientist should the output be
}

class GrimoireBinder:
    def __init__(self, config: Dict = None):
        """Initialize the Grimoire Binder with configuration."""
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        
        self.grimoire_root = Path(self.config['grimoire_root'])
        self.output_dir = Path(self.config['output_dir'])
        self.base_repo_path = Path(self.config['base_repo_path'])
        self.template_dir = Path(self.config['template_dir'])
        self.assets_dir = Path(self.config['assets_dir'])
        
        # Internal state
        self.documents = {}  # Will store all harvested documents
        self.tags = {}       # Will map tags to documents
        self.categories = {} # Will map categories to documents
        
        # Ensure required directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"{Colors.HEADER}{Colors.BOLD}THE GRIMOIRE BINDER{Colors.ENDC}")
        print(f"{Colors.BLUE}A mad scientist's approach to documentation chaos{Colors.ENDC}")
        print(f"Initializing with madness level: {Colors.BOLD}{self.config['madness_level']}{Colors.ENDC}")

    def harvest_documents(self) -> int:
        """
        Scan the repository for markdown files and extract metadata.
        
        Returns:
            int: Number of documents harvested
        """
        print(f"\n{Colors.BOLD}PHASE 1: THE HARVESTING{Colors.ENDC}")
        print("Scanning the repository for knowledge fragments...")
        
        # First, gather docs from the grimoire directory
        grimoire_docs = self._scan_directory(self.grimoire_root)
        print(f"Found {Colors.GREEN}{len(grimoire_docs)}{Colors.ENDC} documents in the grimoire")
        
        # Then, look for other markdown files in the repo
        repo_docs = self._scan_directory(
            self.base_repo_path, 
            exclude_dirs=[str(self.grimoire_root)] + self.config['excluded_dirs']
        )
        print(f"Found {Colors.GREEN}{len(repo_docs)}{Colors.ENDC} additional documents in the repository")
        
        # Combine and process all documents
        all_docs = grimoire_docs + repo_docs
        for doc_path in all_docs:
            self._process_document(doc_path)
        
        # Extract relationships between documents
        self._identify_relationships()
        
        print(f"\nHarvesting complete. {Colors.GREEN}{len(self.documents)}{Colors.ENDC} documents processed.")
        print(f"Discovered {Colors.GREEN}{len(self.tags)}{Colors.ENDC} unique tags.")
        return len(self.documents)

    def format_documents(self) -> int:
        """
        Apply consistent formatting to harvested documents.
        
        Returns:
            int: Number of documents formatted
        """
        print(f"\n{Colors.BOLD}PHASE 2: THE FORMATTING{Colors.ENDC}")
        print("Applying consistent styling to documentation...")
        
        formatted_count = 0
        for doc_id, doc in self.documents.items():
            if self._format_document(doc):
                formatted_count += 1
        
        print(f"\nFormatting complete. {Colors.GREEN}{formatted_count}{Colors.ENDC} documents formatted.")
        return formatted_count

    def generate_crossreferences(self) -> int:
        """
        Generate cross-references between related documents.
        
        Returns:
            int: Number of cross-references created
        """
        print(f"\n{Colors.BOLD}PHASE 3: THE CROSS-REFERENCING{Colors.ENDC}")
        print("Creating neural connections between knowledge fragments...")
        
        xref_count = 0
        for doc_id, doc in self.documents.items():
            added = self._add_crossreferences(doc)
            xref_count += added
            if added > 0:
                print(f"  Added {Colors.GREEN}{added}{Colors.ENDC} references to {doc['title']}")
        
        print(f"\nCross-referencing complete. {Colors.GREEN}{xref_count}{Colors.ENDC} references created.")
        return xref_count

    def generate_indexes(self) -> int:
        """
        Generate indexes for tags, categories, and other metadata.
        
        Returns:
            int: Number of index pages created
        """
        print(f"\n{Colors.BOLD}PHASE 4: THE INDEXING{Colors.ENDC}")
        print("Creating arcane indexes for the grimoire...")
        
        index_count = 0
        
        # Generate tag indexes
        if self.tags:
            index_count += self._generate_tag_indexes()
        
        # Generate category indexes
        if self.categories:
            index_count += self._generate_category_indexes()
        
        # Generate master index
        self._generate_master_index()
        index_count += 1
        
        print(f"\nIndexing complete. {Colors.GREEN}{index_count}{Colors.ENDC} index pages created.")
        return index_count

    def bind_grimoire(self) -> str:
        """
        Compile the processed documentation into a static site.
        
        Returns:
            str: Path to the generated site
        """
        print(f"\n{Colors.BOLD}PHASE 5: THE BINDING{Colors.ENDC}")
        print("Binding the grimoire into a unified tome...")
        
        # For the prototype, we'll just copy files rather than generating a static site
        output_path = self.output_dir
        
        # In a full implementation, this would integrate with a static site generator
        # For now, we'll just create a simple index.html
        with open(output_path / "index.html", "w") as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>The Grimoire of Interactive Madness</title>
    <style>
        body {{ font-family: 'Georgia', serif; background-color: #f5f5f5; margin: 40px; }}
        h1 {{ color: #8b0000; text-align: center; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .footer {{ text-align: center; font-style: italic; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>The Grimoire of Interactive Madness</h1>
        <p>This grimoire contains the collected knowledge of {len(self.documents)} documents, organized into {len(self.categories)} categories with {len(self.tags)} tags.</p>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} with madness level {self.config['madness_level']}.</p>
        <p>This is a prototype implementation. The full Grimoire Binder will generate a complete, navigable site.</p>
    </div>
    <div class="footer">
        <p>"Documentation without madness is like science without explosions—technically functional but devoid of spirit!"</p>
    </div>
</body>
</html>""")
        
        print(f"\nBinding complete. Grimoire available at: {Colors.GREEN}{output_path}{Colors.ENDC}")
        return str(output_path)

    def run(self) -> None:
        """Run the full Grimoire Binder process."""
        start_time = datetime.now()
        
        self.harvest_documents()
        self.format_documents()
        self.generate_crossreferences()
        self.generate_indexes()
        output_path = self.bind_grimoire()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n{Colors.BOLD}THE EXPERIMENT IS COMPLETE!{Colors.ENDC}")
        print(f"Processed {Colors.GREEN}{len(self.documents)}{Colors.ENDC} documents in {Colors.BLUE}{duration:.2f}{Colors.ENDC} seconds")
        print(f"The bound grimoire awaits at: {Colors.GREEN}{output_path}{Colors.ENDC}")

    # Private helper methods

    def _scan_directory(self, base_dir: Path, exclude_dirs: List[str] = None) -> List[Path]:
        """Scan a directory for markdown files recursively."""
        if exclude_dirs is None:
            exclude_dirs = self.config['excluded_dirs']
        
        markdown_files = []
        
        for ext in self.config['markdown_extensions']:
            pattern = f"**/*{ext}"
            files = glob.glob(str(base_dir / pattern), recursive=True)
            
            # Filter out excluded directories
            for file_path in files:
                path = Path(file_path)
                excluded = False
                
                for excluded_dir in exclude_dirs:
                    if excluded_dir in str(path):
                        excluded = True
                        break
                
                if not excluded:
                    markdown_files.append(path)
        
        return markdown_files

    def _process_document(self, doc_path: Path) -> Dict:
        """Extract metadata and content from a markdown document."""
        doc_id = str(doc_path.relative_to(self.base_repo_path))
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title (first heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else doc_path.stem
        
        # Extract tags
        tag_matches = re.findall(r'`#([a-zA-Z0-9_-]+)`', content)
        tags = list(set(tag_matches))
        
        # Determine category based on path
        category = self._determine_category(doc_path)
        
        # Extract quotations (text in italics)
        quotations = re.findall(r'\*"(.+?)"\*', content)
        
        # Extract last modified date (use file modification date as fallback)
        last_modified = datetime.fromtimestamp(os.path.getmtime(doc_path))
        date_match = re.search(r'Updated: (\d{4}-\d{2}-\d{2})', content)
        if date_match:
            try:
                last_modified = datetime.strptime(date_match.group(1), '%Y-%m-%d')
            except ValueError:
                pass
        
        # Store document data
        doc_data = {
            'id': doc_id,
            'path': str(doc_path),
            'title': title,
            'tags': tags,
            'category': category,
            'quotations': quotations,
            'last_modified': last_modified,
            'content': content,
            'related_docs': set()  # Will be populated during relationship identification
        }
        
        self.documents[doc_id] = doc_data
        
        # Update tag and category indexes
        for tag in tags:
            if tag not in self.tags:
                self.tags[tag] = set()
            self.tags[tag].add(doc_id)
        
        if category not in self.categories:
            self.categories[category] = set()
        self.categories[category].add(doc_id)
        
        return doc_data

    def _determine_category(self, doc_path: Path) -> str:
        """Determine the category of a document based on its path."""
        path_str = str(doc_path)
        
        # Check if it's in the grimoire structure
        if 'grimoire/arcana' in path_str:
            return 'arcana'
        elif 'grimoire/chronicles' in path_str:
            return 'chronicles'
        elif 'grimoire/experiments' in path_str:
            return 'experiments'
        elif 'grimoire/incantations' in path_str:
            return 'incantations'
        elif 'grimoire/projects' in path_str:
            # Extract project name from path
            match = re.search(r'grimoire/projects/([^/]+)', path_str)
            if match:
                return f"projects/{match.group(1)}"
            return 'projects'
        elif 'grimoire/wisdom' in path_str:
            return 'wisdom'
        
        # For non-grimoire documents, use directory name
        parent_dir = doc_path.parent.name
        if parent_dir == doc_path.name or parent_dir == '':
            return 'uncategorized'
        return parent_dir

    def _identify_relationships(self) -> None:
        """Identify relationships between documents based on tags and content."""
        # Identify by tags
        for tag, doc_ids in self.tags.items():
            if len(doc_ids) > 1:
                for doc_id in doc_ids:
                    self.documents[doc_id]['related_docs'].update(
                        [related_id for related_id in doc_ids if related_id != doc_id]
                    )
        
        # Identify by explicit references
        for doc_id, doc in self.documents.items():
            content = doc['content']
            
            # Look for markdown links
            for other_doc_id in self.documents:
                # Skip self-references
                if other_doc_id == doc_id:
                    continue
                
                # Check if this document links to other_doc
                relative_path = os.path.relpath(
                    self.documents[other_doc_id]['path'], 
                    os.path.dirname(doc['path'])
                )
                if f"]({relative_path})" in content or f"]({other_doc_id})" in content:
                    doc['related_docs'].add(other_doc_id)
                    self.documents[other_doc_id]['related_docs'].add(doc_id)

    def _format_document(self, doc: Dict) -> bool:
        """Apply consistent formatting to a document. Returns True if changes were made."""
        # In a full implementation, this would apply templates and formatting
        # For the prototype, we'll just log what would happen
        print(f"  Would format: {Colors.BLUE}{doc['title']}{Colors.ENDC} ({doc['category']})")
        return True

    def _add_crossreferences(self, doc: Dict) -> int:
        """Add cross-references to a document. Returns number of references added."""
        # In a full implementation, this would modify the document content
        # For the prototype, we'll just return the number of potential references
        return len(doc['related_docs'])

    def _generate_tag_indexes(self) -> int:
        """Generate index pages for tags. Returns number of indexes created."""
        # In a full implementation, this would create actual index pages
        # For the prototype, we'll just log what would happen
        print(f"  Would create {Colors.GREEN}{len(self.tags)}{Colors.ENDC} tag index pages")
        return len(self.tags)

    def _generate_category_indexes(self) -> int:
        """Generate index pages for categories. Returns number of indexes created."""
        # In a full implementation, this would create actual index pages
        # For the prototype, we'll just log what would happen
        print(f"  Would create {Colors.GREEN}{len(self.categories)}{Colors.ENDC} category index pages")
        return len(self.categories)

    def _generate_master_index(self) -> None:
        """Generate the master index page for the grimoire."""
        # In a full implementation, this would create an actual index page
        # For the prototype, we'll just log what would happen
        print(f"  Would create {Colors.GREEN}master index{Colors.ENDC} page")


def main():
    parser = argparse.ArgumentParser(description="The Grimoire Binder - A mad scientist's documentation generator")
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--madness-level', type=int, choices=[1, 2, 3, 4, 5], 
                        help='Level of mad scientist themeing (1-5)')
    parser.add_argument('--grimoire-root', type=str, help='Root directory of the grimoire')
    parser.add_argument('--output-dir', type=str, help='Output directory for the bound grimoire')
    parser.add_argument('--base-repo-path', type=str, help='Base repository path')
    
    args = parser.parse_args()
    
    config = DEFAULT_CONFIG.copy()
    
    # Load configuration from file if specified
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    config.update(file_config)
    
    # Override with command-line arguments
    if args.madness_level:
        config['madness_level'] = args.madness_level
    if args.grimoire_root:
        config['grimoire_root'] = args.grimoire_root
    if args.output_dir:
        config['output_dir'] = args.output_dir
    if args.base_repo_path:
        config['base_repo_path'] = args.base_repo_path
    
    # Run the binder
    binder = GrimoireBinder(config)
    binder.run()


if __name__ == "__main__":
    main() 
