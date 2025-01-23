#!/usr/bin/env python3.11
"""
Setup script for dataset creation and preprocessing tools.
This tool helps create, clean, and prepare datasets for training and evaluation.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict

def check_requirements():
    """Check if required packages are installed."""
    required = ['pandas', 'datasets', 'beautifulsoup4', 'markdown', 'python-dotenv', 'scikit-learn']
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
            f.write("""# Dataset Creation Settings
RAW_DATA_PATH=./data/raw
PROCESSED_DATA_PATH=./data/processed
TRAIN_SPLIT=0.8
VAL_SPLIT=0.1
TEST_SPLIT=0.1
MAX_SAMPLES=10000
MIN_TOKENS=10
MAX_TOKENS=2048
""")
        print("Created .env file with default settings")
    else:
        print(".env file already exists")

def setup_dataset_tools():
    """Setup the dataset creation and processing tools."""
    # Create necessary directories
    for dir_path in ["data/raw", "data/processed", "scripts"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Create data processing script
    with open("scripts/process_data.py", "w") as f:
        f.write("""#!/usr/bin/env python3.11
import json
import os
from pathlib import Path
from typing import List, Dict
import pandas as pd
from bs4 import BeautifulSoup
import markdown
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()

class DataProcessor:
    def __init__(self):
        self.raw_path = Path(os.getenv("RAW_DATA_PATH"))
        self.processed_path = Path(os.getenv("PROCESSED_DATA_PATH"))
        self.train_split = float(os.getenv("TRAIN_SPLIT"))
        self.val_split = float(os.getenv("VAL_SPLIT"))
        self.test_split = float(os.getenv("TEST_SPLIT"))
        self.max_samples = int(os.getenv("MAX_SAMPLES"))
        self.min_tokens = int(os.getenv("MIN_TOKENS"))
        self.max_tokens = int(os.getenv("MAX_TOKENS"))
    
    def process_files(self):
        \"\"\"Process all files in raw directory.\"\"\"
        data = []
        
        # Process each file based on type
        for file_path in self.raw_path.rglob("*"):
            if file_path.is_file():
                if file_path.suffix == ".json":
                    data.extend(self._process_json(file_path))
                elif file_path.suffix == ".md":
                    data.extend(self._process_markdown(file_path))
                elif file_path.suffix == ".html":
                    data.extend(self._process_html(file_path))
                elif file_path.suffix == ".txt":
                    data.extend(self._process_text(file_path))
        
        # Apply filters
        data = self._filter_data(data)
        
        # Split data
        return self._split_data(data)
    
    def _process_json(self, file_path: Path) -> List[Dict]:
        \"\"\"Process JSON file.\"\"\"
        with open(file_path) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return [data]
    
    def _process_markdown(self, file_path: Path) -> List[Dict]:
        \"\"\"Process Markdown file.\"\"\"
        with open(file_path) as f:
            md_text = f.read()
            html = markdown.markdown(md_text)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract sections as instruction-response pairs
            data = []
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                content = []
                for sibling in heading.find_next_siblings():
                    if sibling.name in ['h1', 'h2', 'h3']:
                        break
                    content.append(str(sibling))
                
                if content:
                    data.append({
                        "instruction": heading.get_text(),
                        "output": "\\n".join(content)
                    })
            
            return data
    
    def _process_html(self, file_path: Path) -> List[Dict]:
        \"\"\"Process HTML file.\"\"\"
        with open(file_path) as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            # Extract QA pairs
            data = []
            for qa_pair in soup.find_all(class_=['qa-pair', 'question', 'answer']):
                question = qa_pair.find(class_='question')
                answer = qa_pair.find(class_='answer')
                if question and answer:
                    data.append({
                        "instruction": question.get_text(),
                        "output": answer.get_text()
                    })
            
            return data
    
    def _process_text(self, file_path: Path) -> List[Dict]:
        \"\"\"Process text file.\"\"\"
        with open(file_path) as f:
            lines = f.readlines()
            
            # Try to extract QA pairs (assuming format: Q: ... A: ...)
            data = []
            current_q = None
            current_a = []
            
            for line in lines:
                line = line.strip()
                if line.startswith("Q:"):
                    if current_q:
                        data.append({
                            "instruction": current_q,
                            "output": "\\n".join(current_a)
                        })
                    current_q = line[2:].strip()
                    current_a = []
                elif line.startswith("A:"):
                    current_a.append(line[2:].strip())
                elif current_q and line:
                    current_a.append(line)
            
            # Add last pair
            if current_q:
                data.append({
                    "instruction": current_q,
                    "output": "\\n".join(current_a)
                })
            
            return data
    
    def _filter_data(self, data: List[Dict]) -> List[Dict]:
        \"\"\"Apply filters to data.\"\"\"
        filtered = []
        
        for item in data:
            # Check lengths
            if not (self.min_tokens <= len(item["instruction"].split()) <= self.max_tokens):
                continue
            if not (self.min_tokens <= len(item["output"].split()) <= self.max_tokens):
                continue
            
            filtered.append(item)
        
        # Limit total samples
        if self.max_samples > 0:
            filtered = filtered[:self.max_samples]
        
        return filtered
    
    def _split_data(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        \"\"\"Split data into train/val/test sets.\"\"\"
        # First split: train + remaining
        train_data, temp_data = train_test_split(
            data,
            train_size=self.train_split,
            random_state=42
        )
        
        # Second split: val + test from remaining
        val_size = self.val_split / (self.val_split + self.test_split)
        val_data, test_data = train_test_split(
            temp_data,
            train_size=val_size,
            random_state=42
        )
        
        return {
            "train": train_data,
            "validation": val_data,
            "test": test_data
        }

def main():
    processor = DataProcessor()
    
    print("Processing data files...")
    splits = processor.process_files()
    
    # Save splits
    for split_name, split_data in splits.items():
        output_file = processor.processed_path / f"{split_name}.json"
        with open(output_file, "w") as f:
            json.dump(split_data, f, indent=2)
        print(f"Saved {len(split_data)} examples to {output_file}")

if __name__ == "__main__":
    main()
""")

    # Create data conversion script
    with open("scripts/convert_format.py", "w") as f:
        f.write("""#!/usr/bin/env python3.11
import json
import pandas as pd
from pathlib import Path
import argparse

def convert_csv_to_json(csv_path: str, output_path: str):
    \"\"\"Convert CSV to JSON format.\"\"\"
    df = pd.read_csv(csv_path)
    
    # Try to map common column names
    instruction_cols = ['question', 'instruction', 'input', 'prompt']
    output_cols = ['answer', 'response', 'output', 'completion']
    
    instruction_col = next((col for col in instruction_cols if col in df.columns), None)
    output_col = next((col for col in output_cols if col in df.columns), None)
    
    if not (instruction_col and output_col):
        print("Could not find instruction/output columns")
        return
    
    data = []
    for _, row in df.iterrows():
        item = {
            "instruction": row[instruction_col],
            "output": row[output_col]
        }
        # Add optional input if present
        if "input" in df.columns and pd.notna(row["input"]):
            item["input"] = row["input"]
        data.append(item)
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Convert data formats")
    parser.add_argument("input_file", help="Input file path")
    parser.add_argument("output_file", help="Output file path")
    parser.add_argument("--format", choices=["csv2json"], default="csv2json",
                      help="Conversion format (default: csv2json)")
    
    args = parser.parse_args()
    
    if args.format == "csv2json":
        convert_csv_to_json(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
""")

    # Create example raw data
    example_data = {
        "text": """Q: What is Python?
A: Python is a high-level, interpreted programming language known for its simplicity and readability.

Q: How do you create a list in Python?
A: You can create a list in Python using square brackets []. For example:
my_list = [1, 2, 3]
empty_list = []""",

        "markdown": """# Python Basics

## Variables
Variables in Python are created when you assign a value:
x = 5
name = "Alice"

## Data Types
Python has several built-in data types:
- Numbers (int, float)
- Strings (str)
- Lists
- Dictionaries""",

        "html": """<div class="qa-pair">
    <div class="question">What are functions in Python?</div>
    <div class="answer">Functions are reusable blocks of code that perform specific tasks. They are defined using the def keyword.</div>
</div>"""
    }

    # Save example files
    for fmt, content in example_data.items():
        with open(f"data/raw/example.{fmt}", "w") as f:
            f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Setup dataset creation tools")
    args = parser.parse_args()

    print("Setting up dataset creation tools...")

    # Check and install requirements
    check_requirements()

    # Setup environment
    setup_env()

    # Setup dataset tools
    setup_dataset_tools()

    print("""
Setup complete! To create and process datasets:

1. Add your raw data files to data/raw/:
   - Supported formats: JSON, Markdown, HTML, Text
   - See example files for format reference

2. Process the data:
   python scripts/process_data.py

3. Convert from other formats:
   python scripts/convert_format.py input.csv output.json

The system will:
- Process files based on their format
- Clean and filter the data
- Create train/validation/test splits
- Save processed data to data/processed/

Features:
- Automatic format detection
- Multi-format support
- Data cleaning and filtering
- Configurable split ratios
- Size limits and token filters

Tips:
- Adjust settings in .env file
- Check example files for format reference
- Use convert_format.py for unsupported formats
- Monitor processing logs for issues
""")

if __name__ == "__main__":
    main()
