#!/usr/bin/env python3.11
"""
Setup script for fine-tuning local models.
This tool helps prepare datasets and run fine-tuning on local models.
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
    required = ['torch', 'transformers', 'datasets', 'accelerate', 'bitsandbytes', 'python-dotenv']
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
            f.write("""# Fine-tuning Settings
BASE_MODEL=codellama
DATASET_PATH=./data/training
OUTPUT_PATH=./data/finetuned
BATCH_SIZE=4
LEARNING_RATE=2e-5
NUM_EPOCHS=3
MAX_LENGTH=512
GRADIENT_ACCUMULATION=4
""")
        print("Created .env file with default settings")
    else:
        print(".env file already exists")

def setup_finetune():
    """Setup the fine-tuning system files."""
    # Create necessary directories
    for dir_path in ["data/training", "data/finetuned", "scripts"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create dataset preparation script
    with open("scripts/prepare_dataset.py", "w") as f:
        f.write("""#!/usr/bin/env python3
import json
from pathlib import Path
from typing import List, Dict
import pandas as pd
from datasets import Dataset

def convert_to_instruction_format(data: List[Dict]) -> Dataset:
    \"\"\"Convert data to instruction format.\"\"\"
    formatted_data = []
    for item in data:
        formatted_data.append({
            "instruction": item["instruction"],
            "input": item.get("input", ""),
            "output": item["output"]
        })
    return Dataset.from_pandas(pd.DataFrame(formatted_data))

def main():
    training_dir = Path("data/training")
    
    # Load and combine all JSON files in training directory
    all_data = []
    for json_file in training_dir.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
            if isinstance(data, list):
                all_data.extend(data)
            else:
                all_data.append(data)
    
    # Convert to instruction dataset
    dataset = convert_to_instruction_format(all_data)
    
    # Save as Hugging Face dataset
    dataset.save_to_disk(training_dir / "processed")
    print(f"Processed {len(dataset)} examples")

if __name__ == "__main__":
    main()
""")
    
    # Create fine-tuning script
    with open("scripts/finetune.py", "w") as f:
        f.write("""#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_from_disk
import torch

load_dotenv()

def prepare_model():
    \"\"\"Prepare model and tokenizer for fine-tuning.\"\"\"
    model = AutoModelForCausalLM.from_pretrained(
        os.getenv("BASE_MODEL"),
        device_map="auto",
        torch_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained(os.getenv("BASE_MODEL"))
    return model, tokenizer

def prepare_dataset(tokenizer):
    \"\"\"Prepare dataset for training.\"\"\"
    dataset = load_from_disk(Path(os.getenv("DATASET_PATH")) / "processed")
    
    def tokenize(example):
        # Format as instruction
        text = f"### Instruction: {example['instruction']}\\n"
        if example['input']:
            text += f"### Input: {example['input']}\\n"
        text += f"### Response: {example['output']}"
        
        return tokenizer(
            text,
            truncation=True,
            max_length=int(os.getenv("MAX_LENGTH")),
            padding="max_length"
        )
    
    tokenized_dataset = dataset.map(
        tokenize,
        remove_columns=dataset.column_names
    )
    return tokenized_dataset

def main():
    # Prepare model and tokenizer
    model, tokenizer = prepare_model()
    
    # Prepare dataset
    dataset = prepare_dataset(tokenizer)
    
    # Setup training arguments
    training_args = TrainingArguments(
        output_dir=os.getenv("OUTPUT_PATH"),
        num_train_epochs=int(os.getenv("NUM_EPOCHS")),
        per_device_train_batch_size=int(os.getenv("BATCH_SIZE")),
        gradient_accumulation_steps=int(os.getenv("GRADIENT_ACCUMULATION")),
        learning_rate=float(os.getenv("LEARNING_RATE")),
        fp16=True,
        save_strategy="epoch",
        logging_steps=10,
        report_to="none"
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )
    
    # Start training
    trainer.train()
    
    # Save model
    trainer.save_model()
    tokenizer.save_pretrained(os.getenv("OUTPUT_PATH"))

if __name__ == "__main__":
    main()
""")

    # Create example dataset
    example_data = [
        {
            "instruction": "Explain what recursion is in programming.",
            "output": "Recursion is a programming concept where a function calls itself to solve a problem by breaking it down into smaller, similar sub-problems. It consists of a base case that stops the recursion and a recursive case that continues it."
        },
        {
            "instruction": "Write a function to calculate factorial.",
            "input": "n = 5",
            "output": "def factorial(n):\\n    if n <= 1:\\n        return 1\\n    return n * factorial(n-1)"
        }
    ]
    
    with open("data/training/example.json", "w") as f:
        json.dump(example_data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Setup fine-tuning environment for local models")
    parser.add_argument("--model", default="codellama", help="Base model to fine-tune (default: codellama)")
    args = parser.parse_args()
    
    print("Setting up fine-tuning environment...")
    
    # Check and install requirements
    check_requirements()
    
    # Setup environment
    setup_env()
    
    # Setup fine-tuning system
    setup_finetune()
    
    print(f"""
Setup complete! To fine-tune your model:

1. Prepare your training data:
   - Add JSON files to data/training/
   - Format: {{"instruction": "task", "input": "optional input", "output": "expected output"}}
   - See example.json for reference

2. Process your dataset:
   python scripts/prepare_dataset.py

3. Start fine-tuning:
   python scripts/finetune.py

The system will:
- Load your base model ({args.model})
- Process and tokenize your dataset
- Fine-tune using specified parameters
- Save the resulting model to data/finetuned/

Tips:
- Adjust hyperparameters in .env file
- Monitor training progress in output logs
- Use smaller batch sizes if running out of memory
- Consider using gradient accumulation for larger effective batch sizes
""")

if __name__ == "__main__":
    main() 
